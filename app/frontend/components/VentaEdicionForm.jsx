import { useEffect, useState } from "react";

import { buscarProductosParaVenta } from "../api/productosApi.js";
import { buscarVenta, buscarVentasDeCliente, cerrarVenta, reemplazarDetalleVenta } from "../api/ventasApi.js";
import {
  POSITIVE_NUMBER_MESSAGE,
  addItem,
  computeTotal,
  removeItem,
  validateQuantityFormat,
} from "../ventaDetalle.js";
import {
  CLIENTE_SALES_STATE,
  EDICION_STATE,
  evaluateClienteSalesParaModificar,
  evaluateEdicionResult,
} from "../ventaEdicion.js";
import "./VentaEdicionForm.css";

const NO_PRODUCTS_FOUND_MESSAGE = "No se encontraron productos";
const PRODUCT_SEARCH_DEBOUNCE_MS = 300;

/**
 * @param {import("../api/ventasApi.js").VentaItem[]} items
 * @returns {import("../ventaDetalle.js").VentaItem[]}
 */
function toVentaDetalleItems(items) {
  return items.map((item) => ({
    sku: item.sku,
    name: item.name,
    unitPrice: item.unit_price,
    quantity: item.quantity,
  }));
}

/**
 * Formulario de modificación de venta (HU-VEN-03, HU-VEN-06): búsqueda
 * de las ventas de un cliente por DNI, elección de una en Borrador
 * (ícono de editar) para editar su detalle (agregar/quitar productos)
 * y cierre definitivo.
 * @returns {import("react").JSX.Element}
 */
export function VentaEdicionForm() {
  const [dniInput, setDniInput] = useState("");
  const [isSearchingClient, setIsSearchingClient] = useState(false);
  const [clienteEvaluation, setClienteEvaluation] = useState(
    /** @type {import("../ventaEdicion.js").ClienteSalesEvaluation | null} */ (null)
  );

  const [editState, setEditState] = useState(
    /** @type {import("../ventaEdicion.js").EdicionEvaluation | null} */ (null)
  );
  const [saleId, setSaleId] = useState(/** @type {number | null} */ (null));
  const [items, setItems] = useState(
    /** @type {import("../ventaDetalle.js").VentaItem[]} */ ([])
  );

  const [productQuery, setProductQuery] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(
    /** @type {import("../api/productosApi.js").ProductoVentaCandidato | null} */ (null)
  );
  const [productResults, setProductResults] = useState(
    /** @type {import("../api/productosApi.js").ProductoVentaCandidato[]} */ ([])
  );
  const [hasSearchedProducts, setHasSearchedProducts] = useState(false);
  const [quantityInput, setQuantityInput] = useState("");
  const [itemError, setItemError] = useState("");

  useEffect(() => {
    if (selectedProduct || !productQuery.trim()) {
      setProductResults([]);
      setHasSearchedProducts(false);
      return;
    }
    let cancelled = false;
    const timeoutId = setTimeout(() => {
      buscarProductosParaVenta(productQuery).then((result) => {
        if (cancelled) {
          return;
        }
        setProductResults(result.products);
        setHasSearchedProducts(true);
      });
    }, PRODUCT_SEARCH_DEBOUNCE_MS);
    return () => {
      cancelled = true;
      clearTimeout(timeoutId);
    };
  }, [productQuery, selectedProduct]);

  /** @param {string} value */
  function handleProductQueryChange(value) {
    setProductQuery(value);
    setSelectedProduct(null);
  }

  /** @param {import("../api/productosApi.js").ProductoVentaCandidato} product */
  function handleSelectProduct(product) {
    setSelectedProduct(product);
    setProductQuery(product.name);
    setProductResults([]);
  }

  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [saveErrors, setSaveErrors] = useState(/** @type {string[]} */ ([]));

  const [showCloseConfirm, setShowCloseConfirm] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [closeMessage, setCloseMessage] = useState("");
  const [closeError, setCloseError] = useState("");
  const [confirmedSale, setConfirmedSale] = useState(
    /** @type {import("../api/ventasApi.js").Venta | null} */ (null)
  );

  function resetEditing() {
    setEditState(null);
    setSaleId(null);
    setItems([]);
    setProductQuery("");
    setSelectedProduct(null);
    setProductResults([]);
    setHasSearchedProducts(false);
    setQuantityInput("");
    setItemError("");
    setSaveMessage("");
    setSaveErrors([]);
    setShowCloseConfirm(false);
    setCloseMessage("");
    setCloseError("");
    setConfirmedSale(null);
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSearchClient(event) {
    event.preventDefault();
    setIsSearchingClient(true);
    setClienteEvaluation(null);
    resetEditing();
    try {
      const result = await buscarVentasDeCliente(dniInput);
      setClienteEvaluation(evaluateClienteSalesParaModificar(result));
    } finally {
      setIsSearchingClient(false);
    }
  }

  /** @param {number} id */
  async function handleSelectSaleToEdit(id) {
    setEditState(null);
    const result = await buscarVenta(id);
    const evaluation = evaluateEdicionResult(result);
    setEditState(evaluation);
    if (evaluation.state === EDICION_STATE.EDITABLE && evaluation.sale) {
      setSaleId(evaluation.sale.id);
      setItems(toVentaDetalleItems(evaluation.sale.items));
    }
  }

  async function handleBackToList() {
    resetEditing();
    const result = await buscarVentasDeCliente(dniInput);
    setClienteEvaluation(evaluateClienteSalesParaModificar(result));
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  function handleAddItem(event) {
    event.preventDefault();
    setItemError("");

    if (!selectedProduct) {
      return;
    }

    const outcome = addItem(items, {
      sku: selectedProduct.sku,
      name: selectedProduct.name,
      unitPrice: selectedProduct.unit_price,
      stock: selectedProduct.stock,
      quantity: quantityInput,
    });

    if (outcome.error) {
      setItemError(outcome.error);
      return;
    }

    setItems(outcome.items);
    setProductQuery("");
    setSelectedProduct(null);
    setQuantityInput("");
  }

  /** @param {string} sku */
  function handleRemoveItem(sku) {
    setItems(removeItem(items, sku));
  }

  async function handleSaveDetail() {
    if (saleId === null) {
      return;
    }
    setIsSaving(true);
    setSaveMessage("");
    setSaveErrors([]);
    try {
      const result = await reemplazarDetalleVenta(
        saleId,
        items.map((item) => ({
          sku: item.sku,
          quantity: String(item.quantity),
          unit_price: String(item.unitPrice),
        }))
      );

      if (result.success) {
        setSaveMessage(result.message);
        setItems(toVentaDetalleItems(result.sale.items));
        return;
      }

      setSaveErrors(result.errors.map((error) => error.message));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleConfirmClose() {
    if (saleId === null) {
      return;
    }
    setIsClosing(true);
    setCloseError("");
    try {
      const result = await cerrarVenta(saleId);
      if (result.success) {
        setCloseMessage(result.message);
        setConfirmedSale(result.sale);
        setShowCloseConfirm(false);
        return;
      }
      setCloseError(result.errors[0].message);
      setShowCloseConfirm(false);
    } finally {
      setIsClosing(false);
    }
  }

  function handleCancelClose() {
    setShowCloseConfirm(false);
  }

  const total = computeTotal(items);
  const isEditable =
    editState?.state === EDICION_STATE.EDITABLE && confirmedSale === null;

  return (
    <div className="venta-edicion">
      <form className="venta-edicion__search" onSubmit={handleSearchClient} noValidate>
        <p className="venta-edicion__intro">
          Ingresá el DNI del cliente para ver sus ventas.
        </p>

        <div className="venta-edicion__field">
          <label htmlFor="edicion-dni">DNI del cliente</label>
          <input
            id="edicion-dni"
            name="dni"
            type="text"
            inputMode="numeric"
            autoComplete="off"
            value={dniInput}
            onChange={(event) => setDniInput(event.target.value)}
          />
        </div>

        <button type="submit" disabled={isSearchingClient || !dniInput}>
          {isSearchingClient ? "Buscando…" : "Buscar ventas"}
        </button>
      </form>

      {!editState && clienteEvaluation?.state === CLIENTE_SALES_STATE.CLIENT_NOT_FOUND && (
        <p className="venta-edicion__banner venta-edicion__banner--error" role="alert">
          {clienteEvaluation.message}
        </p>
      )}

      {!editState && clienteEvaluation?.state === CLIENTE_SALES_STATE.NO_SALES && (
        <p className="venta-edicion__banner venta-edicion__banner--warning" role="alert">
          {clienteEvaluation.message}
        </p>
      )}

      {!editState && clienteEvaluation?.state === CLIENTE_SALES_STATE.SALES_LIST && (
        <table className="venta-edicion__client-sales-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Fecha</th>
              <th>Estado</th>
              <th>Total</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(clienteEvaluation.sales ?? []).map((sale) => (
              <tr key={sale.id}>
                <td>{sale.id}</td>
                <td>{sale.sale_date}</td>
                <td>{sale.status}</td>
                <td>{sale.total}</td>
                <td>
                  <button
                    type="button"
                    aria-label={`Editar venta ${sale.id}`}
                    disabled={sale.status !== "Borrador"}
                    onClick={() => handleSelectSaleToEdit(sale.id)}
                  >
                    Editar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {editState?.state === EDICION_STATE.NOT_FOUND && (
        <p className="venta-edicion__banner venta-edicion__banner--error" role="alert">
          {editState.message}
        </p>
      )}

      {editState?.state === EDICION_STATE.NOT_DRAFT && confirmedSale === null && (
        <p className="venta-edicion__banner venta-edicion__banner--warning" role="alert">
          {editState.message}
        </p>
      )}

      {closeMessage && confirmedSale && (
        <p className="venta-edicion__banner venta-edicion__banner--success" role="status">
          {closeMessage}
        </p>
      )}

      {editState && (
        <button type="button" onClick={handleBackToList}>
          Volver a la lista
        </button>
      )}

      {isEditable && (
        <>
          <form className="venta-edicion__add-item" onSubmit={handleAddItem} noValidate>
            <div className="venta-edicion__field venta-edicion__field--product">
              <label htmlFor="edicion-producto">Producto</label>
              <input
                id="edicion-producto"
                name="producto"
                type="text"
                autoComplete="off"
                value={productQuery}
                onChange={(event) => handleProductQueryChange(event.target.value)}
              />
              {!selectedProduct && productQuery.trim() && (
                <>
                  {productResults.length > 0 ? (
                    <ul className="venta-edicion__product-results">
                      {productResults.map((product) => (
                        <li key={product.sku}>
                          <button
                            type="button"
                            onMouseDown={() => handleSelectProduct(product)}
                          >
                            {product.name} ({product.sku})
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    hasSearchedProducts && (
                      <p className="venta-edicion__product-no-results">
                        {NO_PRODUCTS_FOUND_MESSAGE}
                      </p>
                    )
                  )}
                </>
              )}
            </div>
            <div className="venta-edicion__field">
              <label htmlFor="edicion-cantidad">Cantidad</label>
              <input
                id="edicion-cantidad"
                name="quantity"
                type="text"
                inputMode="numeric"
                autoComplete="off"
                value={quantityInput}
                onChange={(event) => {
                  setQuantityInput(event.target.value);
                  if (itemError === POSITIVE_NUMBER_MESSAGE) {
                    setItemError("");
                  }
                }}
                onBlur={() => {
                  if (!quantityInput.trim()) {
                    return;
                  }
                  const error = validateQuantityFormat(quantityInput);
                  if (error) {
                    setItemError(error);
                  }
                }}
              />
            </div>
            <button type="submit" disabled={!selectedProduct || !quantityInput}>
              Agregar
            </button>
          </form>

          {itemError && (
            <p className="venta-edicion__banner venta-edicion__banner--error" role="alert">
              {itemError}
            </p>
          )}

          <table className="venta-edicion__table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Nombre</th>
                <th>Cantidad</th>
                <th>Precio unitario</th>
                <th>Subtotal</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.sku}>
                  <td>{item.sku}</td>
                  <td>{item.name}</td>
                  <td>{item.quantity}</td>
                  <td>{item.unitPrice}</td>
                  <td>{item.quantity * item.unitPrice}</td>
                  <td>
                    <button type="button" onClick={() => handleRemoveItem(item.sku)}>
                      Quitar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <p className="venta-edicion__total">Total: {total}</p>

          {saveMessage && (
            <p className="venta-edicion__banner venta-edicion__banner--success" role="status">
              {saveMessage}
            </p>
          )}

          {saveErrors.length > 0 && (
            <ul className="venta-edicion__banner venta-edicion__banner--error" role="alert">
              {saveErrors.map((message) => (
                <li key={message}>{message}</li>
              ))}
            </ul>
          )}

          {closeError && (
            <p className="venta-edicion__banner venta-edicion__banner--error" role="alert">
              {closeError}
            </p>
          )}

          <div className="venta-edicion__actions">
            <button type="button" onClick={handleSaveDetail} disabled={isSaving}>
              {isSaving ? "Guardando…" : "Guardar cambios"}
            </button>
            <button
              type="button"
              disabled={items.length === 0}
              onClick={() => setShowCloseConfirm(true)}
            >
              Cerrar venta
            </button>
          </div>

          {showCloseConfirm && (
            <div className="venta-edicion__confirm">
              <p>¿Confirmás cerrar esta venta? Se descontará el stock de sus productos.</p>
              <div className="venta-edicion__confirm-actions">
                <button type="button" onClick={handleConfirmClose} disabled={isClosing}>
                  {isClosing ? "Cerrando…" : "Confirmar"}
                </button>
                <button
                  type="button"
                  className="venta-edicion__cancel"
                  onClick={handleCancelClose}
                  disabled={isClosing}
                >
                  Cancelar
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
