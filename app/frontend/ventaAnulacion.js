/**
 * Interpreta el resultado de la búsqueda de las ventas de un cliente
 * por DNI para la anulación (HU-VEN-06), sin depender de React.
 * Análogo a `ventaEdicion.js`.
 */

/** @typedef {"CLIENT_NOT_FOUND" | "NO_CONFIRMED_SALES" | "SALES_LIST"} AnulacionState */

export const ANULACION_STATE = /** @type {const} */ ({
  CLIENT_NOT_FOUND: "CLIENT_NOT_FOUND",
  NO_CONFIRMED_SALES: "NO_CONFIRMED_SALES",
  SALES_LIST: "SALES_LIST",
});

export const CLIENT_NOT_FOUND_MESSAGE = "Cliente no encontrado";
export const NO_CONFIRMED_SALES_MESSAGE =
  "El cliente no tiene ventas confirmadas para anular";

/**
 * @typedef {Object} AnulacionEvaluation
 * @property {AnulacionState} state
 * @property {string} [message]
 * @property {import("./api/ventasApi.js").VentaClienteResumen[]} [sales]
 */

/**
 * @param {import("./api/ventasApi.js").VentasDeClienteSuccess | import("./api/ventasApi.js").VentasDeClienteFailure} searchResult
 * @returns {AnulacionEvaluation}
 */
export function evaluateClienteSalesParaAnular(searchResult) {
  if (!searchResult.success) {
    return { state: ANULACION_STATE.CLIENT_NOT_FOUND, message: CLIENT_NOT_FOUND_MESSAGE };
  }

  const confirmedSales = searchResult.sales.filter((sale) => sale.status === "Confirmada");

  if (confirmedSales.length === 0) {
    return { state: ANULACION_STATE.NO_CONFIRMED_SALES, message: NO_CONFIRMED_SALES_MESSAGE };
  }

  return { state: ANULACION_STATE.SALES_LIST, sales: confirmedSales };
}
