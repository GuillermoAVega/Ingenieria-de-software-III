/**
 * Metadata compartida de los 5 campos del cliente (DNI, nombre, apellido,
 * email, teléfono), usada tanto por el formulario de alta (`ClienteForm.jsx`)
 * como por el de edición (`ClienteEdicionForm.jsx`).
 */

/** @type {{ field: string, label: string, hint: string, inputMode: "numeric" | "tel" | "text" }[]} */
export const CLIENTE_FIELDS = [
  { field: "dni", label: "DNI", hint: "Solo números, 7 u 8 dígitos", inputMode: "numeric" },
  { field: "first_name", label: "Nombre", hint: "Solo letras y espacios", inputMode: "text" },
  { field: "last_name", label: "Apellido", hint: "Solo letras y espacios", inputMode: "text" },
  { field: "email", label: "Email", hint: "usuario@dominio.com", inputMode: "text" },
  { field: "phone", label: "Teléfono", hint: "Solo números y guiones", inputMode: "tel" },
];
