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

/** @typedef {"CLIENT_NOT_FOUND" | "NO_SALES" | "SALES_LIST"} ClienteSalesState */

export const CLIENTE_SALES_STATE = /** @type {const} */ ({
  CLIENT_NOT_FOUND: "CLIENT_NOT_FOUND",
  NO_SALES: "NO_SALES",
  SALES_LIST: "SALES_LIST",
});

export const CLIENT_NOT_FOUND_MESSAGE = "Cliente no encontrado";
export const NO_SALES_MESSAGE = "El cliente no tiene ventas registradas";

/**
 * @typedef {Object} ClienteSalesEvaluation
 * @property {ClienteSalesState} state
 * @property {string} [message]
 * @property {import("./api/ventasApi.js").VentaClienteResumen[]} [sales]
 */

/**
 * Interpreta el resultado de la búsqueda de las ventas de un cliente
 * por DNI para la modificación (HU-VEN-06): a diferencia de
 * `evaluateClienteSalesParaAnular`, no filtra por estado — cada venta
 * conserva su `status` para que la vista decida en cuáles habilitar el
 * ícono de editar (RF-8).
 * @param {import("./api/ventasApi.js").VentasDeClienteSuccess | import("./api/ventasApi.js").VentasDeClienteFailure} searchResult
 * @returns {ClienteSalesEvaluation}
 */
export function evaluateClienteSalesParaModificar(searchResult) {
  if (!searchResult.success) {
    return { state: CLIENTE_SALES_STATE.CLIENT_NOT_FOUND, message: CLIENT_NOT_FOUND_MESSAGE };
  }

  if (searchResult.sales.length === 0) {
    return { state: CLIENTE_SALES_STATE.NO_SALES, message: NO_SALES_MESSAGE };
  }

  return { state: CLIENTE_SALES_STATE.SALES_LIST, sales: searchResult.sales };
}

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
