/**
 * Reglas de validación replicadas de `app/backend/core_producto.py` y
 * `app/backend/routes/productos.py`, para dar feedback inmediato en el
 * Frontend sin esperar la respuesta del servidor. El backend sigue siendo
 * la autoridad final (vuelve a validar todo, más la unicidad del SKU, que
 * no puede resolverse en el cliente).
 */

import { trimLeadingTrailingSpace } from "./validation.js";

const REQUIRED_FIELD_MESSAGE = "El campo es obligatorio";
const POSITIVE_NUMBER_MESSAGE = "El valor debe ser un número positivo";

const REQUIRED_FIELDS = ["sku", "name", "brand", "unit_price", "stock"];
const TEXT_FIELDS = ["sku", "name", "brand", "description"];

/**
 * @param {string} value
 * @returns {boolean}
 */
function isPositiveNumber(value) {
  const parsed = Number(value);
  return value.trim() !== "" && Number.isFinite(parsed) && parsed > 0;
}

/**
 * @param {string} value
 * @returns {boolean}
 */
function isPositiveInteger(value) {
  return isPositiveNumber(value) && Number.isInteger(Number(value));
}

/**
 * Valida los 6 campos del alta de producto y devuelve los errores
 * encontrados en un mismo intento, igual que hace el backend.
 * @param {Record<string, string>} values
 * @returns {Record<string, string>}
 */
export function validateProductoForm(values) {
  /** @type {Record<string, string>} */
  const errors = {};
  /** @type {Record<string, string>} */
  const trimmed = {};

  for (const field of TEXT_FIELDS) {
    trimmed[field] = trimLeadingTrailingSpace(values[field] ?? "");
  }
  trimmed.unit_price = values.unit_price ?? "";
  trimmed.stock = values.stock ?? "";

  for (const field of REQUIRED_FIELDS) {
    if (!trimmed[field]) {
      errors[field] = REQUIRED_FIELD_MESSAGE;
    }
  }

  if (!errors.unit_price && !isPositiveNumber(trimmed.unit_price)) {
    errors.unit_price = POSITIVE_NUMBER_MESSAGE;
  }
  if (!errors.stock && !isPositiveInteger(trimmed.stock)) {
    errors.stock = POSITIVE_NUMBER_MESSAGE;
  }

  return errors;
}
