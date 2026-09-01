import { useState } from "react";

import { altaCliente } from "../api/clientesApi.js";
import { CLIENTE_FIELDS } from "../clienteFields.js";
import { validateClienteForm } from "../validation.js";
import "./ClienteForm.css";

const EMPTY_FORM = {
  dni: "",
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
};

const FIELDS = CLIENTE_FIELDS;

/**
 * Formulario de alta de cliente (HU-CLI-01).
 * @returns {import("react").JSX.Element}
 */
export function ClienteForm() {
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

  /** @param {Record<string, string>} errorsByField */
  function showErrorsAndFocusFirstField(errorsByField) {
    setFieldErrors(errorsByField);
    const firstInvalidField = FIELDS.find((item) => errorsByField[item.field]);
    if (firstInvalidField) {
      document.getElementById(firstInvalidField.field)?.focus();
    }
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSubmit(event) {
    event.preventDefault();
    setSuccessMessage("");

    const frontendErrors = validateClienteForm(formValues);
    if (Object.keys(frontendErrors).length > 0) {
      showErrorsAndFocusFirstField(frontendErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await altaCliente(
        /** @type {import("../api/clientesApi.js").ClienteAltaInput} */ (formValues)
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
    <form className="cliente-form" onSubmit={handleSubmit} noValidate>
      <p className="cliente-form__intro">
        Completá los datos para registrar un nuevo cliente. Todos los campos
        son obligatorios.
      </p>

      {successMessage && (
        <p className="cliente-form__banner cliente-form__banner--success" role="status">
          {successMessage}
        </p>
      )}

      {errorCount > 0 && (
        <p className="cliente-form__banner cliente-form__banner--error" role="alert">
          {errorCount === 1
            ? "Hay 1 campo con errores. Revisalo antes de continuar."
            : `Hay ${errorCount} campos con errores. Revisalos antes de continuar.`}
        </p>
      )}

      {FIELDS.map(({ field, label, hint, inputMode }) => {
        const errorId = `${field}-error`;
        const hintId = `${field}-hint`;
        const hasError = Boolean(fieldErrors[field]);

        return (
          <div className="cliente-form__field" key={field}>
            <label htmlFor={field}>{label}</label>
            <input
              id={field}
              name={field}
              type="text"
              inputMode={inputMode}
              autoComplete="off"
              required
              aria-required="true"
              value={formValues[field]}
              onChange={(event) => handleChange(field, event.target.value)}
              aria-invalid={hasError}
              aria-describedby={hasError ? errorId : hintId}
              className={hasError ? "cliente-form__input--invalid" : undefined}
            />
            {hasError ? (
              <p id={errorId} className="cliente-form__error">
                {fieldErrors[field]}
              </p>
            ) : (
              <p id={hintId} className="cliente-form__hint">
                {hint}
              </p>
            )}
          </div>
        );
      })}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Registrando…" : "Registrar cliente"}
      </button>
    </form>
  );
}
