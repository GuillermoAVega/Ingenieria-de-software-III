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
 * @typedef {Object} VentaRegistroSuccess
 * @property {true} success
 * @property {string} message
 * @property {Object} sale
 */

/**
 * @typedef {Object} VentaRegistroFailure
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
