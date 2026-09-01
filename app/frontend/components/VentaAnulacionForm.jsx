import { useState } from "react";

import { anularVenta, buscarVentasDeCliente } from "../api/ventasApi.js";
import { ANULACION_STATE, evaluateClienteSalesParaAnular } from "../ventaAnulacion.js";
import "./VentaAnulacionForm.css";

/**
 * Formulario de anulación de venta (HU-VEN-02, HU-VEN-06): búsqueda de
 * las ventas confirmadas de un cliente por su DNI, elección de una de
 * la lista, y confirmación explícita antes de anularla.
 * @returns {import("react").JSX.Element}
 */
export function VentaAnulacionForm() {
  const [dniInput, setDniInput] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [evaluation, setEvaluation] = useState(
    /** @type {import("../ventaAnulacion.js").AnulacionEvaluation | null} */ (null)
  );
  const [confirmingSale, setConfirmingSale] = useState(
    /** @type {import("../api/ventasApi.js").VentaClienteResumen | null} */ (null)
  );
  const [confirmError, setConfirmError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isConfirming, setIsConfirming] = useState(false);

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSearch(event) {
    event.preventDefault();
    setSuccessMessage("");
    setConfirmError("");
    setConfirmingSale(null);
    setEvaluation(null);
    setIsSearching(true);
    try {
      const result = await buscarVentasDeCliente(dniInput);
      setEvaluation(evaluateClienteSalesParaAnular(result));
    } finally {
      setIsSearching(false);
    }
  }

  /** @param {import("../api/ventasApi.js").VentaClienteResumen} sale */
  function handleSelectSale(sale) {
    setConfirmError("");
    setConfirmingSale(sale);
  }

  async function handleConfirm() {
    if (!confirmingSale) {
      return;
    }
    setIsConfirming(true);
    setConfirmError("");
    try {
      const result = await anularVenta(confirmingSale.id);
      if (result.success) {
        setSuccessMessage(result.message);
        setConfirmingSale(null);
        const refreshed = await buscarVentasDeCliente(dniInput);
        setEvaluation(evaluateClienteSalesParaAnular(refreshed));
        return;
      }
      setConfirmError(result.errors[0].message);
      setConfirmingSale(null);
    } finally {
      setIsConfirming(false);
    }
  }

  function handleCancel() {
    setConfirmingSale(null);
  }

  return (
    <div className="venta-anulacion">
      <form className="venta-anulacion__search" onSubmit={handleSearch} noValidate>
        <p className="venta-anulacion__intro">
          Ingresá el DNI del cliente para ver sus ventas confirmadas.
        </p>

        {successMessage && (
          <p
            className="venta-anulacion__banner venta-anulacion__banner--success"
            role="status"
          >
            {successMessage}
          </p>
        )}

        <div className="venta-anulacion__field">
          <label htmlFor="anulacion-dni">DNI del cliente</label>
          <input
            id="anulacion-dni"
            name="dni"
            type="text"
            inputMode="numeric"
            autoComplete="off"
            value={dniInput}
            onChange={(event) => setDniInput(event.target.value)}
          />
        </div>

        <button type="submit" disabled={isSearching || !dniInput}>
          {isSearching ? "Buscando…" : "Buscar ventas"}
        </button>
      </form>

      {evaluation?.state === ANULACION_STATE.CLIENT_NOT_FOUND && (
        <p
          className="venta-anulacion__banner venta-anulacion__banner--error"
          role="alert"
        >
          {evaluation.message}
        </p>
      )}

      {evaluation?.state === ANULACION_STATE.NO_CONFIRMED_SALES && (
        <p
          className="venta-anulacion__banner venta-anulacion__banner--warning"
          role="alert"
        >
          {evaluation.message}
        </p>
      )}

      {confirmError && (
        <p className="venta-anulacion__banner venta-anulacion__banner--error" role="alert">
          {confirmError}
        </p>
      )}

      {evaluation?.state === ANULACION_STATE.SALES_LIST && (
        <table className="venta-anulacion__table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Fecha</th>
              <th>Total</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(evaluation.sales ?? []).map((sale) => (
              <tr key={sale.id}>
                <td>{sale.id}</td>
                <td>{sale.sale_date}</td>
                <td>{sale.total}</td>
                <td>
                  <button type="button" onClick={() => handleSelectSale(sale)}>
                    Anular
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {confirmingSale && (
        <div className="venta-anulacion__confirm">
          <p className="venta-anulacion__confirm-summary">
            Venta #{confirmingSale.id} — Total {confirmingSale.total}
          </p>
          <p>¿Confirmás anular esta venta? Se repondrá el stock de sus productos.</p>
          <div className="venta-anulacion__confirm-actions">
            <button type="button" onClick={handleConfirm} disabled={isConfirming}>
              {isConfirming ? "Confirmando…" : "Confirmar"}
            </button>
            <button
              type="button"
              className="venta-anulacion__cancel"
              onClick={handleCancel}
              disabled={isConfirming}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
