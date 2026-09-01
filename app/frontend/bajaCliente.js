/**
 * Interpreta el resultado de la búsqueda de un cliente para la baja
 * (HU-CLI-02), sin depender de React. Decide entre los tres estados
 * posibles y expone los mensajes en español correspondientes.
 */

/** @typedef {"NOT_FOUND" | "ALREADY_INACTIVE" | "REQUIRES_CONFIRMATION"} BajaState */

export const BAJA_STATE = /** @type {const} */ ({
  NOT_FOUND: "NOT_FOUND",
  ALREADY_INACTIVE: "ALREADY_INACTIVE",
  REQUIRES_CONFIRMATION: "REQUIRES_CONFIRMATION",
});

export const NOT_FOUND_MESSAGE = "Cliente no encontrado";
export const ALREADY_INACTIVE_MESSAGE = "El cliente ya se encuentra dado de baja";

/**
 * @typedef {Object} BajaEvaluation
 * @property {BajaState} state
 * @property {string} [message]
 * @property {import("./api/clientesApi.js").Cliente} [customer]
 */

/**
 * @param {import("./api/clientesApi.js").ClienteBusquedaSuccess | import("./api/clientesApi.js").ClienteBusquedaFailure} searchResult
 * @returns {BajaEvaluation}
 */
export function evaluateBajaResult(searchResult) {
  if (!searchResult.success) {
    return { state: BAJA_STATE.NOT_FOUND, message: NOT_FOUND_MESSAGE };
  }

  if (searchResult.customer.status === "Inactivo") {
    return { state: BAJA_STATE.ALREADY_INACTIVE, message: ALREADY_INACTIVE_MESSAGE };
  }

  return { state: BAJA_STATE.REQUIRES_CONFIRMATION, customer: searchResult.customer };
}
