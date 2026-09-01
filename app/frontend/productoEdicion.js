/**
 * Interpreta el resultado de la búsqueda de un producto para la edición
 * (HU-PROD-03), sin depender de React. Análogo a `clienteEdicion.js`.
 */

/** @typedef {"NOT_FOUND" | "FOUND"} EdicionState */

export const EDICION_STATE = /** @type {const} */ ({
  NOT_FOUND: "NOT_FOUND",
  FOUND: "FOUND",
});

export const NOT_FOUND_MESSAGE = "Producto no encontrado";

/**
 * @typedef {Object} EdicionEvaluation
 * @property {EdicionState} state
 * @property {string} [message]
 * @property {import("./api/productosApi.js").Producto} [product]
 */

/**
 * @param {import("./api/productosApi.js").ProductoBusquedaSuccess | import("./api/productosApi.js").ProductoBusquedaFailure} searchResult
 * @returns {EdicionEvaluation}
 */
export function evaluateEdicionBusqueda(searchResult) {
  if (!searchResult.success) {
    return { state: EDICION_STATE.NOT_FOUND, message: NOT_FOUND_MESSAGE };
  }

  return { state: EDICION_STATE.FOUND, product: searchResult.product };
}
