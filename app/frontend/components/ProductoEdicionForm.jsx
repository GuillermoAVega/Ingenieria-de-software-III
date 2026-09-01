import { useState } from "react";

import { buscarProducto, editarProducto } from "../api/productosApi.js";
import { EDICION_STATE, evaluateEdicionBusqueda } from "../productoEdicion.js";
import { PRODUCTO_EDICION_FIELDS } from "../productoFields.js";
import { validateProductoEdicionForm } from "../validationProducto.js";
import "./ProductoEdicionForm.css";

const EMPTY_FORM = {
  name: "",
  brand: "",
  description: "",
  unit_price: "",
  stock: "",
};

/**
 * Formulario de modificación de producto (HU-PROD-03): búsqueda por SKU,
 * formulario pre-cargado (SKU de solo lectura), validación inmediata y
 * guardado directo, sin confirmación adicional.
 * @returns {import("react").JSX.Element}
 */
export function ProductoEdicionForm() {
  const [searchSku, setSearchSku] = useState("");
  const [editingSku, setEditingSku] = useState("");
  const [searchResult, setSearchResult] = useState(
    /** @type {import("../productoEdicion.js").EdicionEvaluation | null} */ (null)
  );
  const [formValues, setFormValues] = useState(
    /** @type {Record<string, string>} */ (EMPTY_FORM)
  );
  const [fieldErrors, setFieldErrors] = useState(
    /** @type {Record<string, string>} */ ({})
  );
  const [successMessage, setSuccessMessage] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSearch(event) {
    event.preventDefault();
    setSuccessMessage("");
    setSearchResult(null);
    setFieldErrors({});
    setIsSearching(true);
    try {
      const result = await buscarProducto(searchSku);
      const evaluation = evaluateEdicionBusqueda(result);
      setSearchResult(evaluation);
      if (evaluation.state === EDICION_STATE.FOUND && evaluation.product) {
        const { name, brand, description, unit_price, stock } = evaluation.product;
        setFormValues({
          name,
          brand,
          description: description ?? "",
          unit_price: String(unit_price),
          stock: String(stock),
        });
        setEditingSku(searchSku);
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

  /** @param {string} field */
  function handleBlur(field) {
    if (!formValues[field]?.trim()) {
      return;
    }
    const errors = validateProductoEdicionForm(formValues);
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

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleSubmit(event) {
    event.preventDefault();
    setSuccessMessage("");

    const frontendErrors = validateProductoEdicionForm(formValues);
    if (Object.keys(frontendErrors).length > 0) {
      setFieldErrors(frontendErrors);
      return;
    }

    setIsSaving(true);
    try {
      const result = await editarProducto(
        editingSku,
        /** @type {import("../api/productosApi.js").ProductoEdicionInput} */ (formValues)
      );

      if (result.success) {
        setSuccessMessage(result.message);
        setSearchResult(null);
        setSearchSku("");
        setFormValues(EMPTY_FORM);
        return;
      }

      /** @type {Record<string, string>} */
      const errorsByField = {};
      for (const error of result.errors) {
        errorsByField[error.field] = error.message;
      }
      setFieldErrors(errorsByField);
    } finally {
      setIsSaving(false);
    }
  }

  const errorCount = Object.keys(fieldErrors).length;
  const product = searchResult?.product;

  return (
    <div className="producto-edicion">
      <form className="producto-edicion__search" onSubmit={handleSearch} noValidate>
        <p className="producto-edicion__intro">
          Ingresá el SKU del producto que querés editar.
        </p>

        {successMessage && (
          <p
            className="producto-edicion__banner producto-edicion__banner--success"
            role="status"
          >
            {successMessage}
          </p>
        )}

        <div className="producto-edicion__field">
          <label htmlFor="edicion-search-sku">SKU</label>
          <input
            id="edicion-search-sku"
            name="search-sku"
            type="text"
            autoComplete="off"
            value={searchSku}
            onChange={(event) => setSearchSku(event.target.value)}
          />
        </div>

        <button type="submit" disabled={isSearching || !searchSku}>
          {isSearching ? "Buscando…" : "Buscar producto"}
        </button>
      </form>

      {searchResult?.state === EDICION_STATE.NOT_FOUND && (
        <p
          className="producto-edicion__banner producto-edicion__banner--error"
          role="alert"
        >
          {searchResult.message}
        </p>
      )}

      {searchResult?.state === EDICION_STATE.FOUND && product && (
        <form className="producto-edicion__form" onSubmit={handleSubmit} noValidate>
          {errorCount > 0 && (
            <p
              className="producto-edicion__banner producto-edicion__banner--error"
              role="alert"
            >
              {errorCount === 1
                ? "Hay 1 campo con errores. Revisalo antes de continuar."
                : `Hay ${errorCount} campos con errores. Revisalos antes de continuar.`}
            </p>
          )}

          <div className="producto-edicion__field">
            <span className="producto-edicion__label">SKU</span>
            <p className="producto-edicion__sku-fijo">{product.sku}</p>
          </div>

          {PRODUCTO_EDICION_FIELDS.map(({ field, label, hint, inputMode }) => {
            const errorId = `edicion-${field}-error`;
            const hintId = `edicion-${field}-hint`;
            const hasError = Boolean(fieldErrors[field]);

            return (
              <div className="producto-edicion__field" key={field}>
                <label htmlFor={`edicion-${field}`}>{label}</label>
                <input
                  id={`edicion-${field}`}
                  name={field}
                  type="text"
                  inputMode={inputMode === "decimal" ? "decimal" : inputMode}
                  autoComplete="off"
                  value={formValues[field]}
                  onChange={(event) => handleChange(field, event.target.value)}
                  onBlur={() => handleBlur(field)}
                  aria-invalid={hasError}
                  aria-describedby={hasError ? errorId : hintId}
                  className={hasError ? "producto-edicion__input--invalid" : undefined}
                />
                {hasError ? (
                  <p id={errorId} className="producto-edicion__error">
                    {fieldErrors[field]}
                  </p>
                ) : (
                  <p id={hintId} className="producto-edicion__hint">
                    {hint}
                  </p>
                )}
              </div>
            );
          })}

          <button type="submit" disabled={isSaving}>
            {isSaving ? "Guardando…" : "Guardar cambios"}
          </button>
        </form>
      )}
    </div>
  );
}
