import { useState } from "react";

import { buscarProducto } from "../api/productosApi.js";
import { buscarVenta, cerrarVenta, reemplazarDetalleVenta } from "../api/ventasApi.js";
import {
  POSITIVE_NUMBER_MESSAGE,
  addItem,
  computeTotal,
  removeItem,
  validateQuantityFormat,
} from "../ventaDetalle.js";
import { EDICION_STATE, evaluateEdicionResult } from "../ventaEdicion.js";
import "./VentaEdicionForm.css";

const INACTIVE_PRODUCT_MESSAGE = "El producto no está disponible para la venta";

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
 * Formulario de modificación de venta (HU-VEN-03): búsqueda por ID,
 * edición del detalle de una venta en "Borrador" (agregar/quitar
 * productos) y cierre definitivo.
 * @returns {import("react").JSX.Element}
 */
export function VentaEdicionForm() {
  const [idInput, setIdInput] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [editState, setEditState] = useState(
    /** @type {import("../ventaEdicion.js").EdicionEvaluation | null} */ (null)
  );
  const [saleId, setSaleId] = useState(/** @type {number | null} */ (null));
  const [items, setItems] = useState(
    /** @type {import("../ventaDetalle.js").VentaItem[]} */ ([])
  );

  const [skuInput, setSkuInput] = useState("");
  const [quantityInput, setQuantityInput] = useState("");
  const [itemError, setItemError] = useState("");
  const [isSearchingProduct, setIsSearchingProduct] = useState(false);

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

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSearch(event) {
    event.preventDefault();
    setIsSearching(true);
    setEditState(null);
    setConfirmedSale(null);
    setSaveMessage("");
    setSaveErrors([]);
    setCloseMessage("");
    setCloseError("");
    try {
      const result = await buscarVenta(idInput);
      const evaluation = evaluateEdicionResult(result);
      setEditState(evaluation);
      if (evaluation.state === EDICION_STATE.EDITABLE && evaluation.sale) {
        setSaleId(evaluation.sale.id);
        setItems(toVentaDetalleItems(evaluation.sale.items));
      }
    } finally {
      setIsSearching(false);
    }
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleAddItem(event) {
    event.preventDefault();
    setItemError("");
    setIsSearchingProduct(true);
    try {
      const result = await buscarProducto(skuInput);
      if (!result.success) {
        setItemError(result.errors[0].message);
        return;
      }
      if (result.product.status === "Inactivo") {
        setItemError(INACTIVE_PRODUCT_MESSAGE);
        return;
      }

      const outcome = addItem(items, {
        sku: result.product.sku,
        name: result.product.name,
        unitPrice: result.product.unit_price,
        stock: result.product.stock,
        quantity: quantityInput,
      });

      if (outcome.error) {
        setItemError(outcome.error);
        return;
      }

      setItems(outcome.items);
      setSkuInput("");
      setQuantityInput("");
    } finally {
      setIsSearchingProduct(false);
    }
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
      <form className="venta-edicion__search" onSubmit={handleSearch} noValidate>
        <p className="venta-edicion__intro">
          Ingresá el ID de la venta que querés modificar.
        </p>

        <div className="venta-edicion__field">
          <label htmlFor="edicion-id">ID de la venta</label>
          <input
            id="edicion-id"
            name="id"
            type="text"
            inputMode="numeric"
            autoComplete="off"
            value={idInput}
            onChange={(event) => setIdInput(event.target.value)}
          />
        </div>

        <button type="submit" disabled={isSearching || !idInput}>
          {isSearching ? "Buscando…" : "Buscar venta"}
        </button>
      </form>

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

      {isEditable && (
        <>
          <form className="venta-edicion__add-item" onSubmit={handleAddItem} noValidate>
            <div className="venta-edicion__field">
              <label htmlFor="edicion-sku">SKU</label>
              <input
                id="edicion-sku"
                name="sku"
                type="text"
                autoComplete="off"
                value={skuInput}
                onChange={(event) => setSkuInput(event.target.value)}
              />
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
            <button type="submit" disabled={isSearchingProduct || !skuInput || !quantityInput}>
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
