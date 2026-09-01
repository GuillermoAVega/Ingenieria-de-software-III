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
 * @property {"Confirmada" | "Anulada"} status
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
