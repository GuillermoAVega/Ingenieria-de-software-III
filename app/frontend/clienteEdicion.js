/**
 * Interpreta el resultado de la búsqueda de un cliente para la edición
 * (HU-CLI-03), sin depender de React.
 */

/** @typedef {"NOT_FOUND" | "INACTIVE" | "FOUND"} EdicionState */

export const EDICION_STATE = /** @type {const} */ ({
  NOT_FOUND: "NOT_FOUND",
  INACTIVE: "INACTIVE",
  FOUND: "FOUND",
});

export const NOT_FOUND_MESSAGE = "Cliente no encontrado";
export const INACTIVE_MESSAGE = "El cliente está inactivo y no puede modificarse";

/**
 * @typedef {Object} EdicionEvaluation
 * @property {EdicionState} state
 * @property {string} [message]
 * @property {import("./api/clientesApi.js").Cliente} [customer]
 */

/**
 * @param {import("./api/clientesApi.js").ClienteBusquedaSuccess | import("./api/clientesApi.js").ClienteBusquedaFailure} searchResult
 * @returns {EdicionEvaluation}
 */
export function evaluateEdicionBusqueda(searchResult) {
  if (!searchResult.success) {
    return { state: EDICION_STATE.NOT_FOUND, message: NOT_FOUND_MESSAGE };
  }

  if (searchResult.customer.status === "Inactivo") {
    return {
      state: EDICION_STATE.INACTIVE,
      message: INACTIVE_MESSAGE,
      customer: searchResult.customer,
    };
  }

  return { state: EDICION_STATE.FOUND, customer: searchResult.customer };
}
