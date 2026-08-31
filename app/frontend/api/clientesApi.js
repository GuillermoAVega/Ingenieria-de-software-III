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
 * @typedef {Object} ClienteAltaSuccess
 * @property {true} success
 * @property {string} message
 * @property {Object} customer
 */

/**
 * @typedef {Object} ClienteAltaFailure
 * @property {false} success
 * @property {FieldError[]} errors
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
