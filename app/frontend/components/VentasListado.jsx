import { es } from "date-fns/locale/es";
import { useEffect, useState } from "react";
import DatePicker, { registerLocale } from "react-datepicker";

import { buscarVenta, listarVentas } from "../api/ventasApi.js";
import { toDateOnly, toIsoFromDate } from "../dateFormat.js";
import { DETALLE_STATE, evaluateDetalleVenta } from "../ventaListado.js";
import "react-datepicker/dist/react-datepicker.css";
import "./VentasListado.css";

registerLocale("es", es);

/**
 * Listado y filtro del historial de ventas (HU-VEN-04).
 * @returns {import("react").JSX.Element}
 */
export function VentasListado() {
  const [dniInput, setDniInput] = useState("");
  const [dateFromInput, setDateFromInput] = useState(/** @type {Date | null} */ (null));
  const [dateToInput, setDateToInput] = useState(/** @type {Date | null} */ (null));

  const [sales, setSales] = useState(
    /** @type {import("../api/ventasApi.js").VentaResumen[]} */ ([])
  );
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const [appliedFilters, setAppliedFilters] = useState({
    dni: /** @type {string | undefined} */ (undefined),
    dateFrom: /** @type {string | undefined} */ (undefined),
    dateTo: /** @type {string | undefined} */ (undefined),
  });

  const [detailEvaluation, setDetailEvaluation] = useState(
    /** @type {import("../ventaListado.js").DetalleEvaluation | null} */ (null)
  );

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    listarVentas({ ...appliedFilters, page }).then((result) => {
      if (cancelled) {
        return;
      }
      if (!result.success) {
        setErrorMessage(result.errors[0].message);
        setSales([]);
        setHasNext(false);
        setIsLoading(false);
        return;
      }
      setErrorMessage("");
      setSales(result.sales);
      setHasNext(result.hasNext);
      setIsLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [appliedFilters, page]);

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  function handleSearch(event) {
    event.preventDefault();
    setAppliedFilters({
      dni: dniInput.trim() || undefined,
      dateFrom: dateFromInput ? toIsoFromDate(dateFromInput) : undefined,
      dateTo: dateToInput ? toIsoFromDate(dateToInput) : undefined,
    });
    setPage(1);
  }

  /** @param {number} id */
  async function handleViewDetail(id) {
    const result = await buscarVenta(id);
    setDetailEvaluation(evaluateDetalleVenta(result));
  }

  function handleCloseDetail() {
    setDetailEvaluation(null);
  }

  return (
    <div className="ventas-listado">
      <form className="ventas-listado__search" onSubmit={handleSearch}>
        <div className="ventas-listado__field">
          <label htmlFor="listado-venta-desde">Desde</label>
          <DatePicker
            id="listado-venta-desde"
            name="date_from"
            locale="es"
            dateFormat="dd/MM/yyyy"
            placeholderText="dd/mm/aaaa"
            autoComplete="off"
            isClearable
            showPopperArrow={false}
            selectsStart
            selected={dateFromInput}
            startDate={dateFromInput}
            endDate={dateToInput}
            maxDate={dateToInput ?? undefined}
            onChange={(/** @type {Date | null} */ date) => setDateFromInput(date)}
          />
        </div>
        <div className="ventas-listado__field">
          <label htmlFor="listado-venta-hasta">Hasta</label>
          <DatePicker
            id="listado-venta-hasta"
            name="date_to"
            locale="es"
            dateFormat="dd/MM/yyyy"
            placeholderText="dd/mm/aaaa"
            autoComplete="off"
            isClearable
            showPopperArrow={false}
            selectsEnd
            selected={dateToInput}
            startDate={dateFromInput}
            endDate={dateToInput}
            minDate={dateFromInput ?? undefined}
            onChange={(/** @type {Date | null} */ date) => setDateToInput(date)}
          />
        </div>
        <div className="ventas-listado__field">
          <label htmlFor="listado-venta-dni">DNI del cliente</label>
          <input
            id="listado-venta-dni"
            name="dni"
            type="text"
            inputMode="numeric"
            autoComplete="off"
            value={dniInput}
            onChange={(event) => setDniInput(event.target.value)}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          Buscar
        </button>
      </form>

      {errorMessage && (
        <p className="ventas-listado__banner ventas-listado__banner--error" role="alert">
          {errorMessage}
        </p>
      )}

      {!errorMessage && !isLoading && sales.length === 0 ? (
        <p className="ventas-listado__banner" role="status">
          No se encontraron resultados
        </p>
      ) : (
        !errorMessage && (
          <table className="ventas-listado__table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Estado</th>
                <th>Total</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {sales.map((sale) => (
                <tr key={sale.id}>
                  <td>{sale.id}</td>
                  <td>{toDateOnly(sale.sale_date)}</td>
                  <td>
                    {sale.customer.first_name} {sale.customer.last_name} ({sale.customer.dni})
                  </td>
                  <td>
                    <span
                      className={`ventas-listado__status ventas-listado__status--${sale.status.toLowerCase()}`}
                    >
                      {sale.status}
                    </span>
                  </td>
                  <td>{sale.total}</td>
                  <td>
                    <button
                      type="button"
                      className="ventas-listado__detail-button"
                      aria-label={`Ver detalle de la venta ${sale.id}`}
                      title="Ver detalle"
                      onClick={() => handleViewDetail(sale.id)}
                    >
                      <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.75"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                      >
                        <path d="M2.5 12c1.9-3.7 5.2-6 9.5-6s7.6 2.3 9.5 6c-1.9 3.7-5.2 6-9.5 6s-7.6-2.3-9.5-6Z" />
                        <circle cx="12" cy="12" r="2.6" fill="currentColor" stroke="none" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      )}

      {detailEvaluation && (
        <div className="ventas-listado__modal-backdrop">
          <div className="ventas-listado__modal" role="dialog" aria-modal="true">
            <button
              type="button"
              className="ventas-listado__modal-close"
              aria-label="Cerrar detalle"
              onClick={handleCloseDetail}
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M18 6 6 18" />
                <path d="M6 6l12 12" />
              </svg>
            </button>

            {detailEvaluation.state === DETALLE_STATE.NOT_FOUND && (
              <p className="ventas-listado__modal-notfound" role="alert">
                {detailEvaluation.message}
              </p>
            )}

            {detailEvaluation.state === DETALLE_STATE.FOUND && detailEvaluation.sale && (
              <>
                <div className="ventas-listado__modal-header">
                  <p className="ventas-listado__modal-title">
                    Venta #{detailEvaluation.sale.id}
                    <span className="ventas-listado__modal-date">
                      {" "}
                      · {toDateOnly(detailEvaluation.sale.sale_date)}
                    </span>
                  </p>
                  <p className="ventas-listado__modal-customer">
                    {detailEvaluation.sale.customer.first_name}{" "}
                    {detailEvaluation.sale.customer.last_name} ({detailEvaluation.sale.customer.dni})
                  </p>
                  <p
                    className={`ventas-listado__modal-status ventas-listado__modal-status--${detailEvaluation.sale.status.toLowerCase()}`}
                  >
                    Estado: {detailEvaluation.sale.status}
                  </p>
                </div>

                <table className="ventas-listado__detail-table">
                  <thead>
                    <tr>
                      <th>SKU</th>
                      <th>Nombre</th>
                      <th>Cantidad</th>
                      <th>Precio unitario</th>
                      <th>Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detailEvaluation.sale.items.map((item) => (
                      <tr key={item.sku}>
                        <td>{item.sku}</td>
                        <td>{item.name}</td>
                        <td>{item.quantity}</td>
                        <td>{item.unit_price}</td>
                        <td>{item.subtotal}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <p className="ventas-listado__modal-total">
                  Total: {detailEvaluation.sale.total}
                </p>
              </>
            )}

            <button
              type="button"
              className="ventas-listado__modal-footer-close"
              onClick={handleCloseDetail}
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      <div className="ventas-listado__pagination">
        <button
          type="button"
          onClick={() => setPage((current) => current - 1)}
          disabled={page <= 1}
        >
          Anterior
        </button>
        <button
          type="button"
          onClick={() => setPage((current) => current + 1)}
          disabled={!hasNext}
        >
          Siguiente
        </button>
      </div>
    </div>
  );
}
