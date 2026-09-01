import { useEffect, useState } from "react";

import { buscarVenta, listarVentas } from "../api/ventasApi.js";
import { toDateOnly } from "../dateFormat.js";
import { DETALLE_STATE, evaluateDetalleVenta } from "../ventaListado.js";
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
      dateFrom: dateFromInput || undefined,
      dateTo: dateToInput || undefined,
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
                  <td>{sale.total}</td>
                  <td>
                    <button
                      type="button"
                      aria-label={`Ver detalle de la venta ${sale.id}`}
                      onClick={() => handleViewDetail(sale.id)}
                    >
                      👁
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
            {detailEvaluation.state === DETALLE_STATE.NOT_FOUND && (
              <p role="alert">{detailEvaluation.message}</p>
            )}

            {detailEvaluation.state === DETALLE_STATE.FOUND && detailEvaluation.sale && (
              <>
                <p>
                  Venta #{detailEvaluation.sale.id} — {toDateOnly(detailEvaluation.sale.sale_date)}
                </p>
                <p>
                  {detailEvaluation.sale.customer.first_name}{" "}
                  {detailEvaluation.sale.customer.last_name} ({detailEvaluation.sale.customer.dni})
                </p>
                <p>Estado: {detailEvaluation.sale.status}</p>
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
                <p>Total: {detailEvaluation.sale.total}</p>
              </>
            )}

            <button type="button" onClick={handleCloseDetail}>
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
