import { useState } from "react";

import { buscarCliente, darDeBajaCliente } from "../api/clientesApi.js";
import { BAJA_STATE, evaluateBajaResult } from "../bajaCliente.js";
import "./ClienteBajaForm.css";

/**
 * Formulario de baja de cliente (HU-CLI-02): búsqueda por DNI, seguida de
 * una confirmación explícita antes de inactivar al cliente encontrado.
 * @returns {import("react").JSX.Element}
 */
export function ClienteBajaForm() {
  const [dni, setDni] = useState("");
  const [searchResult, setSearchResult] = useState(
    /** @type {import("../bajaCliente.js").BajaEvaluation | null} */ (null)
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
      const result = await buscarCliente(dni);
      setSearchResult(evaluateBajaResult(result));
    } finally {
      setIsSearching(false);
    }
  }

  async function handleConfirm() {
    setIsConfirming(true);
    try {
      const result = await darDeBajaCliente(dni);
      if (result.success) {
        setSuccessMessage(result.message);
        setSearchResult(null);
        setDni("");
        return;
      }
      setSearchResult({ state: BAJA_STATE.NOT_FOUND, message: result.errors[0].message });
    } finally {
      setIsConfirming(false);
    }
  }

  function handleCancel() {
    setSearchResult(null);
  }

  const customer = searchResult?.customer;

  return (
    <div className="cliente-baja">
      <form className="cliente-baja__search" onSubmit={handleSearch} noValidate>
        <p className="cliente-baja__intro">
          Ingresá el DNI del cliente que querés dar de baja.
        </p>

        {successMessage && (
          <p className="cliente-baja__banner cliente-baja__banner--success" role="status">
            {successMessage}
          </p>
        )}

        <div className="cliente-baja__field">
          <label htmlFor="baja-dni">DNI</label>
          <input
            id="baja-dni"
            name="dni"
            type="text"
            inputMode="numeric"
            autoComplete="off"
            value={dni}
            onChange={(event) => setDni(event.target.value)}
          />
        </div>

        <button type="submit" disabled={isSearching || !dni}>
          {isSearching ? "Buscando…" : "Buscar cliente"}
        </button>
      </form>

      {searchResult?.state === BAJA_STATE.NOT_FOUND && (
        <p className="cliente-baja__banner cliente-baja__banner--error" role="alert">
          {searchResult.message}
        </p>
      )}

      {searchResult?.state === BAJA_STATE.ALREADY_INACTIVE && (
        <p className="cliente-baja__banner cliente-baja__banner--warning" role="alert">
          {searchResult.message}
        </p>
      )}

      {searchResult?.state === BAJA_STATE.REQUIRES_CONFIRMATION && customer && (
        <div className="cliente-baja__confirm">
          <p className="cliente-baja__confirm-summary">
            {customer.first_name} {customer.last_name} — DNI {customer.dni}
          </p>
          <p>¿Confirmás dar de baja a este cliente?</p>
          <div className="cliente-baja__confirm-actions">
            <button type="button" onClick={handleConfirm} disabled={isConfirming}>
              {isConfirming ? "Confirmando…" : "Confirmar"}
            </button>
            <button
              type="button"
              className="cliente-baja__cancel"
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
