import { useState } from "react";

import { buscarCliente } from "../api/clientesApi.js";
import { buscarProducto } from "../api/productosApi.js";
import { registrarVenta } from "../api/ventasApi.js";
import { POSITIVE_NUMBER_MESSAGE, addItem, computeTotal, validateQuantityFormat } from "../ventaDetalle.js";
import "./VentaForm.css";

const INACTIVE_CUSTOMER_MESSAGE = "No se pueden emitir ventas a clientes dados de baja";
const INACTIVE_PRODUCT_MESSAGE = "El producto no está disponible para la venta";

/**
 * Formulario de registro de venta (HU-VEN-01): búsqueda de cliente por
 * DNI, armado del detalle buscando productos por SKU, y confirmación
 * explícita antes de registrar (descuenta stock).
 * @returns {import("react").JSX.Element}
 */
export function VentaForm() {
  const [dniInput, setDniInput] = useState("");
  const [customer, setCustomer] = useState(
    /** @type {{ dni: number, first_name: string, last_name: string, status: string } | null} */ (null)
  );
  const [customerError, setCustomerError] = useState("");
  const [isSearchingCustomer, setIsSearchingCustomer] = useState(false);

  const [skuInput, setSkuInput] = useState("");
  const [quantityInput, setQuantityInput] = useState("");
  const [items, setItems] = useState(
    /** @type {import("../ventaDetalle.js").VentaItem[]} */ ([])
  );
  const [itemError, setItemError] = useState("");
  const [isSearchingProduct, setIsSearchingProduct] = useState(false);

  const [showConfirm, setShowConfirm] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  function resetAll() {
    setDniInput("");
    setCustomer(null);
    setCustomerError("");
    setSkuInput("");
    setQuantityInput("");
    setItems([]);
    setItemError("");
    setShowConfirm(false);
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

  async function handleConfirm() {
    setIsRegistering(true);
    try {
      const result = await registrarVenta({
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
      setShowConfirm(false);
    } finally {
      setIsRegistering(false);
    }
  }

  function handleCancel() {
    setShowConfirm(false);
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
            <div className="venta-form__field">
              <label htmlFor="venta-sku">SKU</label>
              <input
                id="venta-sku"
                name="sku"
                type="text"
                autoComplete="off"
                value={skuInput}
                onChange={(event) => setSkuInput(event.target.value)}
              />
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
            <button type="submit" disabled={isSearchingProduct || !skuInput || !quantityInput}>
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
                </tr>
              ))}
            </tbody>
          </table>

          <p className="venta-form__total">Total: {total}</p>

          <button
            type="button"
            disabled={items.length === 0}
            onClick={() => setShowConfirm(true)}
          >
            Registrar venta
          </button>
        </>
      )}

      {showConfirm && (
        <div className="venta-form__confirm">
          <p>¿Confirmás registrar esta venta?</p>
          <div className="venta-form__confirm-actions">
            <button type="button" onClick={handleConfirm} disabled={isRegistering}>
              {isRegistering ? "Registrando…" : "Confirmar"}
            </button>
            <button
              type="button"
              className="venta-form__cancel"
              onClick={handleCancel}
              disabled={isRegistering}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
