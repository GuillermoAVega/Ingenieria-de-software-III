/**
 * @typedef {Object} VentaItemInput
 * @property {string} sku
 * @property {string} quantity
 * @property {string} unit_price
 */

/**
 * @typedef {Object} VentaRegistroInput
 * @property {string} dni
 * @property {VentaItemInput[]} items
 */

/**
 * @typedef {Object} FieldError
 * @property {string} field
 * @property {string} message
 */

/**
 * @typedef {Object} VentaItem
 * @property {string} sku
 * @property {string} name
 * @property {number} quantity
 * @property {number} unit_price
 * @property {number} subtotal
 */

/**
 * @typedef {Object} Venta
 * @property {number} id
 * @property {{ dni: number, first_name: string, last_name: string }} customer
 * @property {string} sale_date
 * @property {VentaItem[]} items
 * @property {number} total
 * @property {"Borrador" | "Confirmada" | "Anulada"} status
 */

/**
 * @typedef {Object} VentaRegistroSuccess
 * @property {true} success
 * @property {string} message
 * @property {Venta} sale
 */

/**
 * @typedef {Object} VentaRegistroFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} VentaBusquedaSuccess
 * @property {true} success
 * @property {Venta} sale
 */

/**
 * @typedef {Object} VentaBusquedaFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} VentaAnulacionSuccess
 * @property {true} success
 * @property {string} message
 * @property {Venta} sale
 */

/**
 * @typedef {Object} VentaAnulacionFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} VentaDetalleSuccess
 * @property {true} success
 * @property {string} message
 * @property {Venta} sale
 */

/**
 * @typedef {Object} VentaDetalleFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} VentaCierreSuccess
 * @property {true} success
 * @property {string} message
 * @property {Venta} sale
 */

/**
 * @typedef {Object} VentaCierreFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} VentaResumen
 * @property {number} id
 * @property {string} sale_date
 * @property {{ dni: number, first_name: string, last_name: string }} customer
 * @property {number} total
 */

/**
 * @typedef {Object} VentaListadoSuccess
 * @property {true} success
 * @property {VentaResumen[]} sales
 * @property {number} page
 * @property {boolean} hasNext
 */

/**
 * @typedef {Object} VentaListadoFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} VentaClienteResumen
 * @property {number} id
 * @property {string} sale_date
 * @property {"Borrador" | "Confirmada" | "Anulada"} status
 * @property {number} total
 */

/**
 * @typedef {Object} VentasDeClienteSuccess
 * @property {true} success
 * @property {VentaClienteResumen[]} sales
 */

/**
 * @typedef {Object} VentasDeClienteFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

const VENTAS_ENDPOINT = "/ventas";

/**
 * @param {VentaRegistroInput} input
 * @returns {Promise<VentaRegistroSuccess | VentaRegistroFailure>}
 */
export async function registrarVenta(input) {
  const response = await fetch(VENTAS_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, sale: body.sale };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {VentaRegistroInput} input
 * @returns {Promise<VentaRegistroSuccess | VentaRegistroFailure>}
 */
export async function confirmarVenta(input) {
  const response = await fetch(`${VENTAS_ENDPOINT}/confirmar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, sale: body.sale };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {number | string} id
 * @returns {Promise<VentaBusquedaSuccess | VentaBusquedaFailure>}
 */
export async function buscarVenta(id) {
  const response = await fetch(`${VENTAS_ENDPOINT}/${encodeURIComponent(id)}`);

  const body = await response.json();

  if (response.ok) {
    return { success: true, sale: body.sale };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {number | string} id
 * @returns {Promise<VentaAnulacionSuccess | VentaAnulacionFailure>}
 */
export async function anularVenta(id) {
  const response = await fetch(
    `${VENTAS_ENDPOINT}/${encodeURIComponent(id)}/anular`,
    { method: "PATCH" }
  );

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, sale: body.sale };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {{ dni?: string, dateFrom?: string, dateTo?: string, page?: number }} [options]
 * @returns {Promise<VentaListadoSuccess | VentaListadoFailure>}
 */
export async function listarVentas(options = {}) {
  const { dni, dateFrom, dateTo, page } = options;
  const params = new URLSearchParams();
  if (dni) {
    params.set("dni", dni);
  }
  if (dateFrom) {
    params.set("date_from", dateFrom);
  }
  if (dateTo) {
    params.set("date_to", dateTo);
  }
  if (page) {
    params.set("page", String(page));
  }
  const queryString = params.toString();
  const url = queryString ? `${VENTAS_ENDPOINT}?${queryString}` : VENTAS_ENDPOINT;

  const response = await fetch(url);
  const body = await response.json();

  if (response.ok) {
    return { success: true, sales: body.sales, page: body.page, hasNext: body.has_next };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {number | string} id
 * @param {VentaItemInput[]} items
 * @returns {Promise<VentaDetalleSuccess | VentaDetalleFailure>}
 */
export async function reemplazarDetalleVenta(id, items) {
  const response = await fetch(`${VENTAS_ENDPOINT}/${encodeURIComponent(id)}/detalle`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items }),
  });

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, sale: body.sale };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {number | string} id
 * @returns {Promise<VentaCierreSuccess | VentaCierreFailure>}
 */
export async function cerrarVenta(id) {
  const response = await fetch(`${VENTAS_ENDPOINT}/${encodeURIComponent(id)}/cerrar`, {
    method: "PATCH",
  });

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, sale: body.sale };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {string} dni
 * @returns {Promise<VentasDeClienteSuccess | VentasDeClienteFailure>}
 */
export async function buscarVentasDeCliente(dni) {
  const response = await fetch(`${VENTAS_ENDPOINT}/cliente/${encodeURIComponent(dni)}`);

  const body = await response.json();

  if (response.ok) {
    return { success: true, sales: body.sales };
  }

  return { success: false, errors: body.errors };
}
