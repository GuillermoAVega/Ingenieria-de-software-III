/**
 * Interpreta el resultado de la búsqueda de un producto para la baja
 * (HU-PROD-02), sin depender de React. Análogo a `bajaCliente.js`.
 */

/** @typedef {"NOT_FOUND" | "ALREADY_INACTIVE" | "REQUIRES_CONFIRMATION"} BajaState */

export const BAJA_STATE = /** @type {const} */ ({
  NOT_FOUND: "NOT_FOUND",
  ALREADY_INACTIVE: "ALREADY_INACTIVE",
  REQUIRES_CONFIRMATION: "REQUIRES_CONFIRMATION",
});

export const NOT_FOUND_MESSAGE = "Producto no encontrado";
export const ALREADY_INACTIVE_MESSAGE = "El producto ya se encuentra dado de baja";

/**
 * @typedef {Object} BajaEvaluation
 * @property {BajaState} state
 * @property {string} [message]
 * @property {import("./api/productosApi.js").Producto} [product]
 */

/**
 * @param {import("./api/productosApi.js").ProductoBusquedaSuccess | import("./api/productosApi.js").ProductoBusquedaFailure} searchResult
 * @returns {BajaEvaluation}
 */
export function evaluateBajaResult(searchResult) {
  if (!searchResult.success) {
    return { state: BAJA_STATE.NOT_FOUND, message: NOT_FOUND_MESSAGE };
  }

  if (searchResult.product.status === "Inactivo") {
    return { state: BAJA_STATE.ALREADY_INACTIVE, message: ALREADY_INACTIVE_MESSAGE };
  }

  return { state: BAJA_STATE.REQUIRES_CONFIRMATION, product: searchResult.product };
}
