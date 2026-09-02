/**
 * Formateo de fechas puro, sin depender de React.
 */

/**
 * Recorta un datetime ISO (el que devuelve el backend en `sale_date`) a
 * su parte de fecha, sin hora, y la muestra en formato local.
 * @param {string} isoDateTime
 * @returns {string} fecha en formato "dd/mm/aaaa"
 */
export function toDateOnly(isoDateTime) {
  const [year, month, day] = isoDateTime.split("T")[0].split("-");
  return `${day}/${month}/${year}`;
}

/**
 * Convierte la fecha elegida en el datepicker al formato ISO que espera
 * el backend, usando los valores locales (no UTC) para que el día no se
 * corra por zona horaria.
 * @param {Date} date
 * @returns {string} "aaaa-mm-dd"
 */
export function toIsoFromDate(date) {
  const year = String(date.getFullYear()).padStart(4, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
