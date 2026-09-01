/**
 * @typedef {Object} ProductoAltaInput
 * @property {string} sku
 * @property {string} name
 * @property {string} brand
 * @property {string} description
 * @property {string} unit_price
 * @property {string} stock
 */

/**
 * @typedef {Object} FieldError
 * @property {string} field
 * @property {string} message
 */

/**
 * @typedef {Object} Producto
 * @property {string} sku
 * @property {string} name
 * @property {string} brand
 * @property {string | null} description
 * @property {number} unit_price
 * @property {number} stock
 */

/**
 * @typedef {Object} ProductoAltaSuccess
 * @property {true} success
 * @property {string} message
 * @property {Producto} product
 */

/**
 * @typedef {Object} ProductoAltaFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

const PRODUCTOS_ENDPOINT = "/productos";

/**
 * @param {ProductoAltaInput} input
 * @returns {Promise<ProductoAltaSuccess | ProductoAltaFailure>}
 */
export async function altaProducto(input) {
  const response = await fetch(PRODUCTOS_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, product: body.product };
  }

  return { success: false, errors: body.errors };
}
