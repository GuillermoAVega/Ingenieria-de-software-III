/**
 * Interpreta el resultado de la búsqueda de una venta para editar su
 * detalle (HU-VEN-03), sin depender de React. Análogo a
 * `ventaAnulacion.js`.
 */

/** @typedef {"NOT_FOUND" | "NOT_DRAFT" | "EDITABLE"} EdicionState */

export const EDICION_STATE = /** @type {const} */ ({
  NOT_FOUND: "NOT_FOUND",
  NOT_DRAFT: "NOT_DRAFT",
  EDITABLE: "EDITABLE",
});

export const NOT_FOUND_MESSAGE = "Venta no encontrada";
export const NOT_DRAFT_MESSAGE = "La venta ya no admite modificaciones";

/**
 * @typedef {Object} EdicionEvaluation
 * @property {EdicionState} state
 * @property {string} [message]
 * @property {import("./api/ventasApi.js").Venta} [sale]
 */

/**
 * @param {import("./api/ventasApi.js").VentaBusquedaSuccess | import("./api/ventasApi.js").VentaBusquedaFailure} searchResult
 * @returns {EdicionEvaluation}
 */
export function evaluateEdicionResult(searchResult) {
  if (!searchResult.success) {
    return { state: EDICION_STATE.NOT_FOUND, message: NOT_FOUND_MESSAGE };
  }

  if (searchResult.sale.status !== "Borrador") {
    return {
      state: EDICION_STATE.NOT_DRAFT,
      message: NOT_DRAFT_MESSAGE,
      sale: searchResult.sale,
    };
  }

  return { state: EDICION_STATE.EDITABLE, sale: searchResult.sale };
}
