/**
 * Reglas de validación de formato replicadas de `app/backend/core.py`, para
 * dar feedback inmediato en el Frontend sin esperar la respuesta del
 * servidor. El backend sigue siendo la autoridad final (vuelve a validar
 * todo, más la unicidad del DNI, que no puede resolverse en el cliente).
 */

const NAME_PATTERN = /^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$/;
const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+$/;
const PHONE_PATTERN = /^[0-9-]+$/;
const DNI_FORMAT_PATTERN = /^\d{7,8}$/;

const REQUIRED_FIELD_MESSAGE = "El campo es obligatorio";
const INVALID_NAME_MESSAGE = "El campo solo debe contener letras";
const INVALID_EMAIL_MESSAGE = "El email debe tener el formato usuario@dominio";
const INVALID_PHONE_MESSAGE = "El teléfono debe contener solo números y guiones";
const INVALID_DNI_MESSAGE = "El DNI debe contener solo números (7 u 8 dígitos)";

const REQUIRED_FIELDS = ["dni", "first_name", "last_name", "email", "phone"];

/**
 * Recorta el espacio simple al inicio/fin, igual que `core.trim_leading_trailing_space`.
 * @param {string} value
 * @returns {string}
 */
export function trimLeadingTrailingSpace(value) {
  let start = 0;
  let end = value.length;
  while (start < end && value[start] === " ") start += 1;
  while (end > start && value[end - 1] === " ") end -= 1;
  return value.slice(start, end);
}

/**
 * Valida los 5 campos del alta de cliente y devuelve los errores encontrados
 * en un mismo intento, igual que hace el backend.
 * @param {Record<string, string>} values
 * @returns {Record<string, string>}
 */
export function validateClienteForm(values) {
  /** @type {Record<string, string>} */
  const errors = {};
  /** @type {Record<string, string>} */
  const trimmed = {};

  for (const field of REQUIRED_FIELDS) {
    const value = trimLeadingTrailingSpace(values[field] ?? "");
    trimmed[field] = value;
    if (!value) {
      errors[field] = REQUIRED_FIELD_MESSAGE;
    }
  }

  if (!errors.first_name && !NAME_PATTERN.test(trimmed.first_name)) {
    errors.first_name = INVALID_NAME_MESSAGE;
  }
  if (!errors.last_name && !NAME_PATTERN.test(trimmed.last_name)) {
    errors.last_name = INVALID_NAME_MESSAGE;
  }
  if (!errors.email && !EMAIL_PATTERN.test(trimmed.email)) {
    errors.email = INVALID_EMAIL_MESSAGE;
  }
  if (!errors.phone && !PHONE_PATTERN.test(trimmed.phone)) {
    errors.phone = INVALID_PHONE_MESSAGE;
  }
  if (!errors.dni && !DNI_FORMAT_PATTERN.test(trimmed.dni)) {
    errors.dni = INVALID_DNI_MESSAGE;
  }

  return errors;
}
