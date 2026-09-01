import { useState } from "react";

import { altaProducto } from "../api/productosApi.js";
import { PRODUCTO_FIELDS } from "../productoFields.js";
import { validateProductoForm } from "../validationProducto.js";
import "./ProductoForm.css";

const EMPTY_FORM = {
  sku: "",
  name: "",
  brand: "",
  description: "",
  unit_price: "",
  stock: "",
};

/**
 * Formulario de alta de producto (HU-PROD-01).
 * @returns {import("react").JSX.Element}
 */
export function ProductoForm() {
  const [formValues, setFormValues] = useState(
    /** @type {Record<string, string>} */ (EMPTY_FORM)
  );
  const [fieldErrors, setFieldErrors] = useState(
    /** @type {Record<string, string>} */ ({})
  );
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * @param {string} field
   * @param {string} value
   */
  function handleChange(field, value) {
    setFormValues((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => {
      if (!(field in current)) {
        return current;
      }
      const next = { ...current };
      delete next[field];
      return next;
    });
  }

  /** @param {string} field */
  function handleBlur(field) {
    if (!formValues[field]?.trim()) {
      return;
    }
    const errors = validateProductoForm(formValues);
    setFieldErrors((current) => {
      const next = { ...current };
      if (errors[field]) {
        next[field] = errors[field];
      } else {
        delete next[field];
      }
      return next;
    });
  }

  /** @param {Record<string, string>} errorsByField */
  function showErrorsAndFocusFirstField(errorsByField) {
    setFieldErrors(errorsByField);
    const firstInvalidField = PRODUCTO_FIELDS.find((item) => errorsByField[item.field]);
    if (firstInvalidField) {
      document.getElementById(firstInvalidField.field)?.focus();
    }
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSubmit(event) {
    event.preventDefault();
    setSuccessMessage("");

    const frontendErrors = validateProductoForm(formValues);
    if (Object.keys(frontendErrors).length > 0) {
      showErrorsAndFocusFirstField(frontendErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await altaProducto(
        /** @type {import("../api/productosApi.js").ProductoAltaInput} */ (formValues)
      );

      if (result.success) {
        setFieldErrors({});
        setSuccessMessage(result.message);
        setFormValues(EMPTY_FORM);
        return;
      }

      /** @type {Record<string, string>} */
      const errorsByField = {};
      for (const error of result.errors) {
        errorsByField[error.field] = error.message;
      }
      showErrorsAndFocusFirstField(errorsByField);
    } finally {
      setIsSubmitting(false);
    }
  }

  const errorCount = Object.keys(fieldErrors).length;

  return (
    <form className="producto-form" onSubmit={handleSubmit} noValidate>
      <p className="producto-form__intro">
        Completá los datos para registrar un nuevo producto. La descripción
        es el único campo opcional.
      </p>

      {successMessage && (
        <p className="producto-form__banner producto-form__banner--success" role="status">
          {successMessage}
        </p>
      )}

      {errorCount > 0 && (
        <p className="producto-form__banner producto-form__banner--error" role="alert">
          {errorCount === 1
            ? "Hay 1 campo con errores. Revisalo antes de continuar."
            : `Hay ${errorCount} campos con errores. Revisalos antes de continuar.`}
        </p>
      )}

      {PRODUCTO_FIELDS.map(({ field, label, hint, inputMode, required }) => {
        const errorId = `${field}-error`;
        const hintId = `${field}-hint`;
        const hasError = Boolean(fieldErrors[field]);

        return (
          <div className="producto-form__field" key={field}>
            <label htmlFor={field}>{label}</label>
            <input
              id={field}
              name={field}
              type="text"
              inputMode={inputMode === "decimal" ? "decimal" : inputMode}
              autoComplete="off"
              required={required}
              aria-required={required}
              value={formValues[field]}
              onChange={(event) => handleChange(field, event.target.value)}
              onBlur={() => handleBlur(field)}
              aria-invalid={hasError}
              aria-describedby={hasError ? errorId : hintId}
              className={hasError ? "producto-form__input--invalid" : undefined}
            />
            {hasError ? (
              <p id={errorId} className="producto-form__error">
                {fieldErrors[field]}
              </p>
            ) : (
              <p id={hintId} className="producto-form__hint">
                {hint}
              </p>
            )}
          </div>
        );
      })}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Registrando…" : "Registrar producto"}
      </button>
    </form>
  );
}
