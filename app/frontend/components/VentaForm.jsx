import { useEffect, useState } from "react";

import { buscarCliente } from "../api/clientesApi.js";
import { buscarProducto, buscarProductosParaVenta } from "../api/productosApi.js";
import { confirmarVenta, registrarVenta } from "../api/ventasApi.js";
import {
  POSITIVE_NUMBER_MESSAGE,
  addItem,
  computeTotal,
  removeItem,
  updateItemQuantity,
  validateQuantityFormat,
} from "../ventaDetalle.js";
import "./VentaForm.css";

const INACTIVE_CUSTOMER_MESSAGE = "No se pueden emitir ventas a clientes dados de baja";
const NO_PRODUCTS_FOUND_MESSAGE = "No se encontraron productos";
const PRODUCT_SEARCH_DEBOUNCE_MS = 300;

/**
 * Formulario de registro de venta (HU-VEN-01): búsqueda de cliente por
 * DNI, armado del detalle eligiendo el producto por nombre o
 * descripción (HU-VEN-05), y confirmación explícita antes de
 * registrar (descuenta stock).
 * @returns {import("react").JSX.Element}
 */
export function VentaForm() {
  const [dniInput, setDniInput] = useState("");
  const [customer, setCustomer] = useState(
    /** @type {{ dni: number, first_name: string, last_name: string, status: string } | null} */ (null)
  );
  const [customerError, setCustomerError] = useState("");
  const [isSearchingCustomer, setIsSearchingCustomer] = useState(false);

  const [productQuery, setProductQuery] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(
    /** @type {import("../api/productosApi.js").ProductoVentaCandidato | null} */ (null)
  );
  const [productResults, setProductResults] = useState(
    /** @type {import("../api/productosApi.js").ProductoVentaCandidato[]} */ ([])
  );
  const [hasSearchedProducts, setHasSearchedProducts] = useState(false);
  const [quantityInput, setQuantityInput] = useState("");
  const [items, setItems] = useState(
    /** @type {import("../ventaDetalle.js").VentaItem[]} */ ([])
  );
  const [itemError, setItemError] = useState("");

  const [quantityDrafts, setQuantityDrafts] = useState(
    /** @type {Record<string, string>} */ ({})
  );
  const [quantityErrors, setQuantityErrors] = useState(
    /** @type {Record<string, string>} */ ({})
  );

  const [pendingAction, setPendingAction] = useState(
    /** @type {"registrar" | "confirmar" | null} */ (null)
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

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

  function resetAll() {
    setDniInput("");
    setCustomer(null);
    setCustomerError("");
    setProductQuery("");
    setSelectedProduct(null);
    setProductResults([]);
    setHasSearchedProducts(false);
    setQuantityInput("");
    setItems([]);
    setItemError("");
    setQuantityDrafts({});
    setQuantityErrors({});
    setPendingAction(null);
  }

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

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSearchCustomer(event) {
    event.preventDefault();
    setSuccessMessage("");
    setCustomerError("");
    setCustomer(null);
    setIsSearchingCustomer(true);
    try {
      const result = await buscarCliente(dniInput);
      if (!result.success) {
        setCustomerError(result.errors[0].message);
        return;
      }
      if (result.customer.status === "Inactivo") {
        setCustomerError(INACTIVE_CUSTOMER_MESSAGE);
        return;
      }
      setCustomer(result.customer);
    } finally {
      setIsSearchingCustomer(false);
    }
  }

  /** @param {string} sku */
  function handleRemoveItem(sku) {
    setItems(removeItem(items, sku));
    setQuantityDrafts((current) => {
      const next = { ...current };
      delete next[sku];
      return next;
    });
    setQuantityErrors((current) => {
      const next = { ...current };
      delete next[sku];
      return next;
    });
  }

  /**
   * @param {string} sku
   * @param {string} value
   */
  function handleQuantityDraftChange(sku, value) {
    setQuantityDrafts((current) => ({ ...current, [sku]: value }));
    setQuantityErrors((current) => {
      if (!(sku in current)) {
        return current;
      }
      const next = { ...current };
      delete next[sku];
      return next;
    });
  }

  /** @param {string} sku */
  async function handleQuantityBlur(sku) {
    const draft = quantityDrafts[sku];
    if (draft === undefined) {
      return;
    }

    const currentItem = items.find((item) => item.sku === sku);
    if (currentItem && draft === String(currentItem.quantity)) {
      setQuantityDrafts((current) => {
        const next = { ...current };
        delete next[sku];
        return next;
      });
      return;
    }

    const formatError = validateQuantityFormat(draft);
    if (formatError) {
      setQuantityErrors((current) => ({ ...current, [sku]: formatError }));
      return;
    }

    const result = await buscarProducto(sku);
    if (!result.success) {
      setQuantityErrors((current) => ({ ...current, [sku]: result.errors[0].message }));
      return;
    }

    const outcome = updateItemQuantity(items, sku, draft, result.product.stock);
    const stockError = outcome.error;
    if (stockError) {
      setQuantityErrors((current) => ({ ...current, [sku]: stockError }));
      return;
    }

    setItems(outcome.items);
    setQuantityDrafts((current) => {
      const next = { ...current };
      delete next[sku];
      return next;
    });
    setQuantityErrors((current) => {
      const next = { ...current };
      delete next[sku];
      return next;
    });
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

  async function handleConfirmAction() {
    setIsSubmitting(true);
    try {
      const submit = pendingAction === "confirmar" ? confirmarVenta : registrarVenta;
      const result = await submit({
        dni: dniInput,
        items: items.map((item) => ({
          sku: item.sku,
          quantity: String(item.quantity),
          unit_price: String(item.unitPrice),
        })),
      });

      if (result.success) {
        setSuccessMessage(result.message);
        resetAll();
        return;
      }

      setItemError(result.errors[0].message);
      setPendingAction(null);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleCancelAction() {
    setPendingAction(null);
  }

  const total = computeTotal(items);

  return (
    <div className="venta-form">
      <form className="venta-form__search" onSubmit={handleSearchCustomer} noValidate>
        <p className="venta-form__intro">
          Buscá al cliente para iniciar la venta.
        </p>

        {successMessage && (
          <p className="venta-form__banner venta-form__banner--success" role="status">
            {successMessage}
          </p>
        )}

        <div className="venta-form__field">
          <label htmlFor="venta-dni">DNI del cliente</label>
          <input
            id="venta-dni"
            name="dni"
            type="text"
            inputMode="numeric"
            autoComplete="off"
            value={dniInput}
            onChange={(event) => setDniInput(event.target.value)}
          />
        </div>

        <button type="submit" disabled={isSearchingCustomer || !dniInput}>
          {isSearchingCustomer ? "Buscando…" : "Buscar cliente"}
        </button>
      </form>

      {customerError && (
        <p className="venta-form__banner venta-form__banner--error" role="alert">
          {customerError}
        </p>
      )}

      {customer && (
        <>
          <p className="venta-form__customer-summary">
            {customer.first_name} {customer.last_name}
          </p>

          <form className="venta-form__add-item" onSubmit={handleAddItem} noValidate>
            <div className="venta-form__field venta-form__field--product">
              <label htmlFor="venta-producto">Producto</label>
              <input
                id="venta-producto"
                name="producto"
                type="text"
                autoComplete="off"
                value={productQuery}
                onChange={(event) => handleProductQueryChange(event.target.value)}
              />
              {!selectedProduct && productQuery.trim() && (
                <>
                  {productResults.length > 0 ? (
                    <ul className="venta-form__product-results">
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
                      <p className="venta-form__product-no-results">
                        {NO_PRODUCTS_FOUND_MESSAGE}
                      </p>
                    )
                  )}
                </>
              )}
            </div>
            <div className="venta-form__field">
              <label htmlFor="venta-cantidad">Cantidad</label>
              <input
                id="venta-cantidad"
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
            <p className="venta-form__banner venta-form__banner--error" role="alert">
              {itemError}
            </p>
          )}

          <table className="venta-form__table">
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
                  <td>
                    <input
                      type="text"
                      inputMode="numeric"
                      autoComplete="off"
                      aria-label={`Cantidad de ${item.name}`}
                      value={quantityDrafts[item.sku] ?? String(item.quantity)}
                      onChange={(event) =>
                        handleQuantityDraftChange(item.sku, event.target.value)
                      }
                      onBlur={() => handleQuantityBlur(item.sku)}
                      className={
                        quantityErrors[item.sku]
                          ? "venta-form__quantity-input venta-form__quantity-input--invalid"
                          : "venta-form__quantity-input"
                      }
                    />
                    {quantityErrors[item.sku] && (
                      <p className="venta-form__quantity-error" role="alert">
                        {quantityErrors[item.sku]}
                      </p>
                    )}
                  </td>
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

          <p className="venta-form__total">Total: {total}</p>

          <div className="venta-form__actions">
            <button
              type="button"
              disabled={items.length === 0}
              onClick={() => setPendingAction("registrar")}
            >
              Registrar venta
            </button>
            <button
              type="button"
              disabled={items.length === 0}
              onClick={() => setPendingAction("confirmar")}
            >
              Confirmar venta
            </button>
          </div>
        </>
      )}

      {pendingAction && (
        <div className="venta-form__confirm-backdrop">
          <div className="venta-form__confirm" role="dialog" aria-modal="true">
            <p>
              {pendingAction === "confirmar"
                ? "¿Confirmás esta venta? Quedará Confirmada y se descontará el stock de inmediato."
                : "¿Confirmás registrar esta venta? Quedará en Borrador, sin descontar stock."}
            </p>
            <div className="venta-form__confirm-actions">
              <button type="button" onClick={handleConfirmAction} disabled={isSubmitting}>
                {isSubmitting
                  ? pendingAction === "confirmar"
                    ? "Confirmando…"
                    : "Registrando…"
                  : "Confirmar"}
              </button>
              <button
                type="button"
                className="venta-form__cancel"
                onClick={handleCancelAction}
                disabled={isSubmitting}
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
