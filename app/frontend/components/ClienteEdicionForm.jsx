import { useState } from "react";

import { buscarCliente, editarCliente } from "../api/clientesApi.js";
import { EDICION_STATE, evaluateEdicionBusqueda } from "../clienteEdicion.js";
import { CLIENTE_FIELDS } from "../clienteFields.js";
import { validateClienteForm } from "../validation.js";
import "./ClienteEdicionForm.css";

const EMPTY_FORM = {
  dni: "",
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
};

/**
 * Formulario de modificación de cliente (HU-CLI-03): búsqueda por DNI,
 * formulario pre-cargado, validación inmediata y confirmación explícita
 * antes de guardar los cambios.
 * @returns {import("react").JSX.Element}
 */
export function ClienteEdicionForm() {
  const [searchDni, setSearchDni] = useState("");
  const [editingDni, setEditingDni] = useState("");
  const [searchResult, setSearchResult] = useState(
    /** @type {import("../clienteEdicion.js").EdicionEvaluation | null} */ (null)
  );
  const [formValues, setFormValues] = useState(
    /** @type {Record<string, string>} */ (EMPTY_FORM)
  );
  const [fieldErrors, setFieldErrors] = useState(
    /** @type {Record<string, string>} */ ({})
  );
  const [showConfirm, setShowConfirm] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSearch(event) {
    event.preventDefault();
    setSuccessMessage("");
    setSearchResult(null);
    setFieldErrors({});
    setShowConfirm(false);
    setIsSearching(true);
    try {
      const result = await buscarCliente(searchDni);
      const evaluation = evaluateEdicionBusqueda(result);
      setSearchResult(evaluation);
      if (evaluation.state === EDICION_STATE.FOUND && evaluation.customer) {
        const { dni, first_name, last_name, email, phone } = evaluation.customer;
        setFormValues({
          dni: String(dni),
          first_name,
          last_name,
          email,
          phone,
        });
        setEditingDni(searchDni);
      }
    } finally {
      setIsSearching(false);
    }
  }

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

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  function handleSubmit(event) {
    event.preventDefault();
    setSuccessMessage("");

    const frontendErrors = validateClienteForm(formValues);
    if (Object.keys(frontendErrors).length > 0) {
      setFieldErrors(frontendErrors);
      setShowConfirm(false);
      return;
    }

    setFieldErrors({});
    setShowConfirm(true);
  }

  async function handleConfirm() {
    setIsSaving(true);
    try {
      const result = await editarCliente(
        editingDni,
        /** @type {import("../api/clientesApi.js").ClienteAltaInput} */ (formValues)
      );

      if (result.success) {
        setSuccessMessage(result.message);
        setSearchResult(null);
        setSearchDni("");
        setFormValues(EMPTY_FORM);
        setShowConfirm(false);
        return;
      }

      /** @type {Record<string, string>} */
      const errorsByField = {};
      for (const error of result.errors) {
        errorsByField[error.field] = error.message;
      }
      setFieldErrors(errorsByField);
      setShowConfirm(false);
    } finally {
      setIsSaving(false);
    }
  }

  function handleCancel() {
    setShowConfirm(false);
  }

  const errorCount = Object.keys(fieldErrors).length;

  return (
    <div className="cliente-edicion">
      <form className="cliente-edicion__search" onSubmit={handleSearch} noValidate>
        <p className="cliente-edicion__intro">
          Ingresá el DNI del cliente que querés editar.
        </p>

        {successMessage && (
          <p
            className="cliente-edicion__banner cliente-edicion__banner--success"
            role="status"
          >
            {successMessage}
          </p>
        )}

        <div className="cliente-edicion__field">
          <label htmlFor="edicion-search-dni">DNI</label>
          <input
            id="edicion-search-dni"
            name="search-dni"
            type="text"
            inputMode="numeric"
            autoComplete="off"
            value={searchDni}
            onChange={(event) => setSearchDni(event.target.value)}
          />
        </div>

        <button type="submit" disabled={isSearching || !searchDni}>
          {isSearching ? "Buscando…" : "Buscar cliente"}
        </button>
      </form>

      {searchResult?.state === EDICION_STATE.NOT_FOUND && (
        <p
          className="cliente-edicion__banner cliente-edicion__banner--error"
          role="alert"
        >
          {searchResult.message}
        </p>
      )}

      {searchResult?.state === EDICION_STATE.FOUND && (
        <form className="cliente-edicion__form" onSubmit={handleSubmit} noValidate>
          {errorCount > 0 && (
            <p
              className="cliente-edicion__banner cliente-edicion__banner--error"
              role="alert"
            >
              {errorCount === 1
                ? "Hay 1 campo con errores. Revisalo antes de continuar."
                : `Hay ${errorCount} campos con errores. Revisalos antes de continuar.`}
            </p>
          )}

          {CLIENTE_FIELDS.map(({ field, label, hint, inputMode }) => {
            const errorId = `edicion-${field}-error`;
            const hintId = `edicion-${field}-hint`;
            const hasError = Boolean(fieldErrors[field]);

            return (
              <div className="cliente-edicion__field" key={field}>
                <label htmlFor={`edicion-${field}`}>{label}</label>
                <input
                  id={`edicion-${field}`}
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
                  className={hasError ? "cliente-edicion__input--invalid" : undefined}
                />
                {hasError ? (
                  <p id={errorId} className="cliente-edicion__error">
                    {fieldErrors[field]}
                  </p>
                ) : (
                  <p id={hintId} className="cliente-edicion__hint">
                    {hint}
                  </p>
                )}
              </div>
            );
          })}

          <button type="submit" disabled={isSaving}>
            Guardar cambios
          </button>
        </form>
      )}

      {showConfirm && (
        <div className="cliente-edicion__confirm">
          <p>¿Confirmás guardar estos cambios?</p>
          <div className="cliente-edicion__confirm-actions">
            <button type="button" onClick={handleConfirm} disabled={isSaving}>
              {isSaving ? "Guardando…" : "Confirmar"}
            </button>
            <button
              type="button"
              className="cliente-edicion__cancel"
              onClick={handleCancel}
              disabled={isSaving}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
