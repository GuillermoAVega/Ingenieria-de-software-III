/**
 * Formateo de fechas puro, sin depender de React.
 */

/**
 * Recorta un datetime ISO (el que devuelve el backend en `sale_date`) a
 * su parte de fecha, sin hora.
 * @param {string} isoDateTime
 * @returns {string} fecha en formato "YYYY-MM-DD"
 */
export function toDateOnly(isoDateTime) {
  return isoDateTime.split("T")[0];
}
