import { useState } from "react";

import { buscarProducto, darDeBajaProducto } from "../api/productosApi.js";
import { BAJA_STATE, evaluateBajaResult } from "../productoBaja.js";
import "./ProductoBajaForm.css";

/**
 * Formulario de baja de producto (HU-PROD-02): búsqueda por SKU, seguida
 * de una confirmación explícita antes de inactivar el producto encontrado.
 * @returns {import("react").JSX.Element}
 */
export function ProductoBajaForm() {
  const [sku, setSku] = useState("");
  const [searchResult, setSearchResult] = useState(
    /** @type {import("../productoBaja.js").BajaEvaluation | null} */ (null)
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
      const result = await buscarProducto(sku);
      setSearchResult(evaluateBajaResult(result));
    } finally {
      setIsSearching(false);
    }
  }

  async function handleConfirm() {
    setIsConfirming(true);
    try {
      const result = await darDeBajaProducto(sku);
      if (result.success) {
        setSuccessMessage(result.message);
        setSearchResult(null);
        setSku("");
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

  const product = searchResult?.product;

  return (
    <div className="producto-baja">
      <form className="producto-baja__search" onSubmit={handleSearch} noValidate>
        <p className="producto-baja__intro">
          Ingresá el SKU del producto que querés dar de baja.
        </p>

        {successMessage && (
          <p className="producto-baja__banner producto-baja__banner--success" role="status">
            {successMessage}
          </p>
        )}

        <div className="producto-baja__field">
          <label htmlFor="baja-sku">SKU</label>
          <input
            id="baja-sku"
            name="sku"
            type="text"
            autoComplete="off"
            value={sku}
            onChange={(event) => setSku(event.target.value)}
          />
        </div>

        <button type="submit" disabled={isSearching || !sku}>
          {isSearching ? "Buscando…" : "Buscar producto"}
        </button>
      </form>

      {searchResult?.state === BAJA_STATE.NOT_FOUND && (
        <p className="producto-baja__banner producto-baja__banner--error" role="alert">
          {searchResult.message}
        </p>
      )}

      {searchResult?.state === BAJA_STATE.ALREADY_INACTIVE && (
        <p className="producto-baja__banner producto-baja__banner--warning" role="alert">
          {searchResult.message}
        </p>
      )}

      {searchResult?.state === BAJA_STATE.REQUIRES_CONFIRMATION && product && (
        <div className="producto-baja__confirm">
          <p className="producto-baja__confirm-summary">
            {product.name} — SKU {product.sku}
          </p>
          <p>¿Confirmás dar de baja a este producto?</p>
          <div className="producto-baja__confirm-actions">
            <button type="button" onClick={handleConfirm} disabled={isConfirming}>
              {isConfirming ? "Confirmando…" : "Confirmar"}
            </button>
            <button
              type="button"
              className="producto-baja__cancel"
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
