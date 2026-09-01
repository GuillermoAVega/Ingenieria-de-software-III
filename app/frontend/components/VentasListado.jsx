import { useEffect, useState } from "react";

import { listarVentas } from "../api/ventasApi.js";
import "./VentasListado.css";

/**
 * Listado y filtro del historial de ventas (HU-VEN-04).
 * @returns {import("react").JSX.Element}
 */
export function VentasListado() {
  const [dniInput, setDniInput] = useState("");
  const [dateFromInput, setDateFromInput] = useState("");
  const [dateToInput, setDateToInput] = useState("");

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
      dateFrom: dateFromInput || undefined,
      dateTo: dateToInput || undefined,
    });
    setPage(1);
  }

  return (
    <div className="ventas-listado">
      <form className="ventas-listado__search" onSubmit={handleSearch}>
        <div className="ventas-listado__field">
          <label htmlFor="listado-venta-desde">Desde</label>
          <input
            id="listado-venta-desde"
            name="date_from"
            type="date"
            value={dateFromInput}
            onChange={(event) => setDateFromInput(event.target.value)}
          />
        </div>
        <div className="ventas-listado__field">
          <label htmlFor="listado-venta-hasta">Hasta</label>
          <input
            id="listado-venta-hasta"
            name="date_to"
            type="date"
            value={dateToInput}
            onChange={(event) => setDateToInput(event.target.value)}
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
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {sales.map((sale) => (
                <tr key={sale.id}>
                  <td>{sale.id}</td>
                  <td>{sale.sale_date}</td>
                  <td>
                    {sale.customer.first_name} {sale.customer.last_name} ({sale.customer.dni})
                  </td>
                  <td>{sale.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )
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
