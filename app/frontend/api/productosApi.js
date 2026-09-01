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

/**
 * @typedef {Object} ProductoListadoResult
 * @property {Producto[]} products
 * @property {number} page
 * @property {boolean} hasNext
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

/**
 * @param {{ q?: string, page?: number }} [options]
 * @returns {Promise<ProductoListadoResult>}
 */
export async function listarProductos(options = {}) {
  const { q, page } = options;
  const params = new URLSearchParams();
  if (q) {
    params.set("q", q);
  }
  if (page) {
    params.set("page", String(page));
  }
  const queryString = params.toString();
  const url = queryString ? `${PRODUCTOS_ENDPOINT}?${queryString}` : PRODUCTOS_ENDPOINT;

  const response = await fetch(url);
  const body = await response.json();

  return { products: body.products, page: body.page, hasNext: body.has_next };
}
