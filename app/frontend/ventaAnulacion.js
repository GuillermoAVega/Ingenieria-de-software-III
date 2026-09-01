/**
 * Interpreta el resultado de la búsqueda de una venta para la anulación
 * (HU-VEN-02), sin depender de React. Análogo a `bajaCliente.js`/
 * `productoBaja.js`.
 */

/** @typedef {"NOT_FOUND" | "ALREADY_CANCELLED" | "REQUIRES_CONFIRMATION"} AnulacionState */

export const ANULACION_STATE = /** @type {const} */ ({
  NOT_FOUND: "NOT_FOUND",
  ALREADY_CANCELLED: "ALREADY_CANCELLED",
  REQUIRES_CONFIRMATION: "REQUIRES_CONFIRMATION",
});

export const NOT_FOUND_MESSAGE = "Venta no encontrada";
export const ALREADY_CANCELLED_MESSAGE = "La venta ya se encuentra anulada";

/**
 * @typedef {Object} AnulacionEvaluation
 * @property {AnulacionState} state
 * @property {string} [message]
 * @property {import("./api/ventasApi.js").Venta} [sale]
 */

/**
 * @param {import("./api/ventasApi.js").VentaBusquedaSuccess | import("./api/ventasApi.js").VentaBusquedaFailure} searchResult
 * @returns {AnulacionEvaluation}
 */
export function evaluateAnulacionResult(searchResult) {
  if (!searchResult.success) {
    return { state: ANULACION_STATE.NOT_FOUND, message: NOT_FOUND_MESSAGE };
  }

  if (searchResult.sale.status === "Anulada") {
    return { state: ANULACION_STATE.ALREADY_CANCELLED, message: ALREADY_CANCELLED_MESSAGE };
  }

  return { state: ANULACION_STATE.REQUIRES_CONFIRMATION, sale: searchResult.sale };
}
