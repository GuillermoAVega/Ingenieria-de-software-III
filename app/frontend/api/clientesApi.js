/**
 * @typedef {Object} ClienteAltaInput
 * @property {string} dni
 * @property {string} first_name
 * @property {string} last_name
 * @property {string} email
 * @property {string} phone
 */

/**
 * @typedef {Object} FieldError
 * @property {string} field
 * @property {string} message
 */

/**
 * @typedef {Object} Cliente
 * @property {number} dni
 * @property {string} first_name
 * @property {string} last_name
 * @property {string} email
 * @property {string} phone
 * @property {"Activo" | "Inactivo"} status
 */

/**
 * @typedef {Object} ClienteAltaSuccess
 * @property {true} success
 * @property {string} message
 * @property {Cliente} customer
 */

/**
 * @typedef {Object} ClienteAltaFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} ClienteBusquedaSuccess
 * @property {true} success
 * @property {Cliente} customer
 */

/**
 * @typedef {Object} ClienteBusquedaFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} ClienteBajaSuccess
 * @property {true} success
 * @property {string} message
 * @property {Cliente} customer
 */

/**
 * @typedef {Object} ClienteBajaFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} ClienteEdicionSuccess
 * @property {true} success
 * @property {string} message
 * @property {Cliente} customer
 */

/**
 * @typedef {Object} ClienteEdicionFailure
 * @property {false} success
 * @property {FieldError[]} errors
 */

/**
 * @typedef {Object} ClienteListadoResult
 * @property {Cliente[]} customers
 * @property {number} page
 * @property {boolean} hasNext
 */

const CLIENTES_ENDPOINT = "/clientes";

/**
 * @param {ClienteAltaInput} input
 * @returns {Promise<ClienteAltaSuccess | ClienteAltaFailure>}
 */
export async function altaCliente(input) {
  const response = await fetch(CLIENTES_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, customer: body.customer };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {string} dni
 * @param {ClienteAltaInput} input
 * @returns {Promise<ClienteEdicionSuccess | ClienteEdicionFailure>}
 */
export async function editarCliente(dni, input) {
  const response = await fetch(
    `${CLIENTES_ENDPOINT}/${encodeURIComponent(dni)}/editar`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }
  );

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, customer: body.customer };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {{ q?: string, page?: number }} [options]
 * @returns {Promise<ClienteListadoResult>}
 */
export async function listarClientes(options = {}) {
  const { q, page } = options;
  const params = new URLSearchParams();
  if (q) {
    params.set("q", q);
  }
  if (page) {
    params.set("page", String(page));
  }
  const queryString = params.toString();
  const url = queryString ? `${CLIENTES_ENDPOINT}?${queryString}` : CLIENTES_ENDPOINT;

  const response = await fetch(url);
  const body = await response.json();

  return { customers: body.customers, page: body.page, hasNext: body.has_next };
}

/**
 * @param {string} dni
 * @returns {Promise<ClienteBusquedaSuccess | ClienteBusquedaFailure>}
 */
export async function buscarCliente(dni) {
  const response = await fetch(`${CLIENTES_ENDPOINT}/${encodeURIComponent(dni)}`);

  const body = await response.json();

  if (response.ok) {
    return { success: true, customer: body.customer };
  }

  return { success: false, errors: body.errors };
}

/**
 * @param {string} dni
 * @returns {Promise<ClienteBajaSuccess | ClienteBajaFailure>}
 */
export async function darDeBajaCliente(dni) {
  const response = await fetch(
    `${CLIENTES_ENDPOINT}/${encodeURIComponent(dni)}/baja`,
    { method: "PATCH" }
  );

  const body = await response.json();

  if (response.ok) {
    return { success: true, message: body.message, customer: body.customer };
  }

  return { success: false, errors: body.errors };
}
