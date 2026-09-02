/**
 * Lógica de negocio pura del armado del detalle de una venta
 * (HU-VEN-01), sin depender de React: consolidación de ítems repetidos
 * (RF-10), validación de cantidad (RF-8) y de stock disponible (RF-9), y
 * cálculo del total (RF-13).
 */

export const POSITIVE_NUMBER_MESSAGE = "El valor debe ser un número positivo";
const INSUFFICIENT_STOCK_MESSAGE = "No hay stock suficiente para completar la operación";

/**
 * @param {number} stock
 * @returns {string}
 */
function insufficientStockMessage(stock) {
  return `${INSUFFICIENT_STOCK_MESSAGE} (disponible: ${stock})`;
}

/**
 * @typedef {Object} VentaItem
 * @property {string} sku
 * @property {string} name
 * @property {number} unitPrice
 * @property {number} quantity
 */

/**
 * @param {string} value
 * @returns {boolean}
 */
function isPositiveInteger(value) {
  const parsed = Number(value);
  return value.trim() !== "" && Number.isInteger(parsed) && parsed > 0;
}

/**
 * Valida únicamente el formato de la cantidad (entero positivo), sin
 * depender del producto ni de su stock — se puede invocar apenas se
 * pierde el foco del campo, antes de haber buscado el SKU.
 * @param {string} quantity
 * @returns {string | null}
 */
export function validateQuantityFormat(quantity) {
  if (!isPositiveInteger(quantity)) {
    return POSITIVE_NUMBER_MESSAGE;
  }
  return null;
}

/**
 * @param {VentaItem[]} items
 * @param {{ sku: string, name: string, unitPrice: number, stock: number, quantity: string }} candidate
 * @returns {{ items: VentaItem[], error: string | null }}
 */
export function addItem(items, candidate) {
  const { sku, name, unitPrice, stock, quantity } = candidate;

  if (!isPositiveInteger(quantity)) {
    return { items, error: POSITIVE_NUMBER_MESSAGE };
  }

  const existing = items.find((item) => item.sku === sku);
  const accumulatedQuantity = (existing ? existing.quantity : 0) + Number(quantity);

  if (accumulatedQuantity > stock) {
    return { items, error: insufficientStockMessage(stock) };
  }

  if (existing) {
    return {
      items: items.map((item) =>
        item.sku === sku ? { ...item, quantity: accumulatedQuantity } : item
      ),
      error: null,
    };
  }

  return {
    items: [...items, { sku, name, unitPrice, quantity: accumulatedQuantity }],
    error: null,
  };
}

/**
 * Actualiza la cantidad de un ítem ya presente en el detalle (a
 * diferencia de `addItem`, reemplaza el valor en vez de acumularlo),
 * validando formato y stock disponible.
 * @param {VentaItem[]} items
 * @param {string} sku
 * @param {string} quantity
 * @param {number} stock
 * @returns {{ items: VentaItem[], error: string | null }}
 */
export function updateItemQuantity(items, sku, quantity, stock) {
  if (!isPositiveInteger(quantity)) {
    return { items, error: POSITIVE_NUMBER_MESSAGE };
  }

  const numericQuantity = Number(quantity);
  if (numericQuantity > stock) {
    return { items, error: insufficientStockMessage(stock) };
  }

  return {
    items: items.map((item) =>
      item.sku === sku ? { ...item, quantity: numericQuantity } : item
    ),
    error: null,
  };
}

/**
 * @param {VentaItem[]} items
 * @returns {number}
 */
export function computeTotal(items) {
  return items.reduce((total, item) => total + item.quantity * item.unitPrice, 0);
}

/**
 * @param {VentaItem[]} items
 * @param {string} sku
 * @returns {VentaItem[]}
 */
export function removeItem(items, sku) {
  return items.filter((item) => item.sku !== sku);
}
