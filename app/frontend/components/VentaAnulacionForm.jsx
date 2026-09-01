import { useState } from "react";

import { anularVenta, buscarVenta } from "../api/ventasApi.js";
import { ANULACION_STATE, evaluateAnulacionResult } from "../ventaAnulacion.js";
import "./VentaAnulacionForm.css";

/**
 * Formulario de anulación de venta (HU-VEN-02): búsqueda por ID, seguida
 * de una confirmación explícita antes de anular la venta encontrada.
 * @returns {import("react").JSX.Element}
 */
export function VentaAnulacionForm() {
  const [idInput, setIdInput] = useState("");
  const [searchResult, setSearchResult] = useState(
    /** @type {import("../ventaAnulacion.js").AnulacionEvaluation | null} */ (null)
  );
  const [successMessage, setSuccessMessage] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSearch(event) {
    event.preventDefault();
    setSuccessMessage("");
    setSearchResult(null);
    setIsSearching(true);
    try {
      const result = await buscarVenta(idInput);
      setSearchResult(evaluateAnulacionResult(result));
    } finally {
      setIsSearching(false);
    }
  }

  async function handleConfirm() {
    setIsConfirming(true);
    try {
      const result = await anularVenta(idInput);
      if (result.success) {
        setSuccessMessage(result.message);
        setSearchResult(null);
        setIdInput("");
        return;
      }
      setSearchResult({
        state: ANULACION_STATE.NOT_FOUND,
        message: result.errors[0].message,
      });
    } finally {
      setIsConfirming(false);
    }
  }

  function handleCancel() {
    setSearchResult(null);
  }

  const sale = searchResult?.sale;

  return (
    <div className="venta-anulacion">
      <form className="venta-anulacion__search" onSubmit={handleSearch} noValidate>
        <p className="venta-anulacion__intro">
          Ingresá el ID de la venta que querés anular.
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
          <label htmlFor="anulacion-id">ID de la venta</label>
          <input
            id="anulacion-id"
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

      {searchResult?.state === ANULACION_STATE.NOT_FOUND && (
        <p
          className="venta-anulacion__banner venta-anulacion__banner--error"
          role="alert"
        >
          {searchResult.message}
        </p>
      )}

      {searchResult?.state === ANULACION_STATE.ALREADY_CANCELLED && (
        <p
          className="venta-anulacion__banner venta-anulacion__banner--warning"
          role="alert"
        >
          {searchResult.message}
        </p>
      )}

      {searchResult?.state === ANULACION_STATE.REQUIRES_CONFIRMATION && sale && (
        <div className="venta-anulacion__confirm">
          <p className="venta-anulacion__confirm-summary">
            Venta #{sale.id} — Total {sale.total}
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
