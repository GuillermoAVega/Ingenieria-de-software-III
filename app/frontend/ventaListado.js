/**
 * Interpreta el resultado de la búsqueda del detalle completo de una
 * venta para el modal de "ver detalle" del listado (HU-VEN-08), sin
 * depender de React. Análogo a `ventaEdicion.js`/`ventaAnulacion.js`.
 */

/** @typedef {"NOT_FOUND" | "FOUND"} DetalleState */

export const DETALLE_STATE = /** @type {const} */ ({
  NOT_FOUND: "NOT_FOUND",
  FOUND: "FOUND",
});

export const NOT_FOUND_MESSAGE = "Venta no encontrada";

/**
 * @typedef {Object} DetalleEvaluation
 * @property {DetalleState} state
 * @property {string} [message]
 * @property {import("./api/ventasApi.js").Venta} [sale]
 */

/**
 * @param {import("./api/ventasApi.js").VentaBusquedaSuccess | import("./api/ventasApi.js").VentaBusquedaFailure} searchResult
 * @returns {DetalleEvaluation}
 */
export function evaluateDetalleVenta(searchResult) {
  if (!searchResult.success) {
    return { state: DETALLE_STATE.NOT_FOUND, message: NOT_FOUND_MESSAGE };
  }

  return { state: DETALLE_STATE.FOUND, sale: searchResult.sale };
}
