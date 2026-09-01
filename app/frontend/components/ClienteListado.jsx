import { useEffect, useState } from "react";

import { listarClientes } from "../api/clientesApi.js";
import "./ClienteListado.css";

/**
 * Listado y filtro de clientes (HU-CLI-04).
 * @returns {import("react").JSX.Element}
 */
export function ClienteListado() {
  const [searchInput, setSearchInput] = useState("");
  const [customers, setCustomers] = useState(
    /** @type {import("../api/clientesApi.js").Cliente[]} */ ([])
  );
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [appliedQuery, setAppliedQuery] = useState(/** @type {string | undefined} */ (undefined));
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    listarClientes({ q: appliedQuery, page }).then((result) => {
      if (cancelled) {
        return;
      }
      setCustomers(result.customers);
      setHasNext(result.hasNext);
      setIsLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [appliedQuery, page]);

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  function handleSearch(event) {
    event.preventDefault();
    setAppliedQuery(searchInput.trim() || undefined);
    setPage(1);
  }

  return (
    <div className="cliente-listado">
      <form className="cliente-listado__search" onSubmit={handleSearch}>
        <label htmlFor="listado-buscar">Buscar</label>
        <input
          id="listado-buscar"
          name="buscar"
          type="text"
          value={searchInput}
          onChange={(event) => setSearchInput(event.target.value)}
        />
        <button type="submit" disabled={isLoading}>
          Buscar
        </button>
      </form>

      {!isLoading && customers.length === 0 ? (
        <p className="cliente-listado__banner" role="status">
          No se encontraron resultados
        </p>
      ) : (
        <table className="cliente-listado__table">
          <thead>
            <tr>
              <th>DNI</th>
              <th>Nombre</th>
              <th>Apellido</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((customer) => (
              <tr key={customer.dni}>
                <td>{customer.dni}</td>
                <td>{customer.first_name}</td>
                <td>{customer.last_name}</td>
                <td>{customer.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="cliente-listado__pagination">
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
