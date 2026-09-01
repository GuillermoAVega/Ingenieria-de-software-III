/**
 * Metadata de los 6 campos del formulario de alta de producto, usada por
 * `ProductoForm.jsx`.
 */

/** @type {{ field: string, label: string, hint: string, inputMode: "numeric" | "decimal" | "text", required: boolean }[]} */
export const PRODUCTO_FIELDS = [
  { field: "sku", label: "Código/SKU", hint: "Cualquier texto, sin espacios al inicio/fin", inputMode: "text", required: true },
  { field: "name", label: "Nombre", hint: "Nombre del producto", inputMode: "text", required: true },
  { field: "brand", label: "Marca", hint: "Marca del producto", inputMode: "text", required: true },
  { field: "description", label: "Descripción (opcional)", hint: "Detalle adicional del producto", inputMode: "text", required: false },
  { field: "unit_price", label: "Precio unitario", hint: "Número positivo, ej. 350.50", inputMode: "decimal", required: true },
  { field: "stock", label: "Stock inicial", hint: "Número entero positivo", inputMode: "numeric", required: true },
];

/**
 * Campos editables del formulario de modificación de producto
 * (`ProductoEdicionForm.jsx`): los mismos de `PRODUCTO_FIELDS` sin el SKU,
 * que no es editable (HU-PROD-03, RF-7).
 * @type {typeof PRODUCTO_FIELDS}
 */
export const PRODUCTO_EDICION_FIELDS = PRODUCTO_FIELDS.filter(
  (item) => item.field !== "sku"
);
