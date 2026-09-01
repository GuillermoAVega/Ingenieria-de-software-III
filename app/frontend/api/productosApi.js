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
 * @property {"Activo" | "Inactivo"} status
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

/**
 * @typedef {Object} ProductoBusquedaSuccess
 * @property {true} success
 * @property {Producto} product
 */

/**
 * @typedef {Object} ProductoBusquedaFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} ProductoBajaSuccess
 * @property {true} success
 * @property {string} message
 * @property {Producto} product
 */

/**
 * @typedef {Object} ProductoBajaFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} ProductoEdicionInput
 * @property {string} name
 * @property {string} brand
 * @property {string} description
 * @property {string} unit_price
 * @property {string} stock
 */

/**
 * @typedef {Object} ProductoEdicionSuccess
 * @property {true} success
 * @property {string} message
 * @property {Producto} product
 */

/**
 * @typedef {Object} ProductoEdicionFailure
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

/**
 * @param {string} sku
 * @returns {Promise<ProductoBusquedaSuccess | ProductoBusquedaFailure>}
 */
export async function buscarProducto(sku) {
  const response = await fetch(`${PRODUCTOS_ENDPOINT}/${encodeURIComponent(sku)}`);

  const body = await response.json();

  if (response.ok) {
    return { success: true, product: body.product };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {string} sku
 * @returns {Promise<ProductoBajaSuccess | ProductoBajaFailure>}
 */
export async function darDeBajaProducto(sku) {
  const response = await fetch(
    `${PRODUCTOS_ENDPOINT}/${encodeURIComponent(sku)}/baja`,
    { method: "PATCH" }
  );

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, product: body.product };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {string} sku
 * @param {ProductoEdicionInput} input
 * @returns {Promise<ProductoEdicionSuccess | ProductoEdicionFailure>}
 */
export async function editarProducto(sku, input) {
  const response = await fetch(
    `${PRODUCTOS_ENDPOINT}/${encodeURIComponent(sku)}/editar`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }
  );

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, product: body.product };
  }

  return { success: false, errors: body.errors };
}
