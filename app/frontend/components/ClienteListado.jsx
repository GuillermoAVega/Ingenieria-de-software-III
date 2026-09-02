import { useEffect, useState } from "react";

import { listarClientes } from "../api/clientesApi.js";
import "./ClienteListado.css";

/**
 * Listado y filtro de clientes (HU-CLI-04).
 * @returns {import("react").JSX.Element}
 */
export function ClienteListado() {
  const [searchInput, setSearchInput] = useState("");
  const [fieldInput, setFieldInput] = useState("first_name");
  const [customers, setCustomers] = useState(
    /** @type {import("../api/clientesApi.js").Cliente[]} */ ([])
  );
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [appliedQuery, setAppliedQuery] = useState(/** @type {string | undefined} */ (undefined));
  const [appliedField, setAppliedField] = useState("first_name");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    listarClientes({ q: appliedQuery, field: appliedField, page }).then((result) => {
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
  }, [appliedQuery, appliedField, page]);

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  function handleSearch(event) {
    event.preventDefault();
    setAppliedQuery(searchInput.trim() || undefined);
    setAppliedField(fieldInput);
    setPage(1);
  }

  return (
    <div className="cliente-listado">
      <form className="cliente-listado__search" onSubmit={handleSearch}>
        <div className="cliente-listado__field cliente-listado__field--campo">
          <label htmlFor="listado-buscar-campo">Filtro</label>
          <select
            id="listado-buscar-campo"
            name="campo"
            value={fieldInput}
            onChange={(event) => setFieldInput(event.target.value)}
          >
            <option value="first_name">Nombre</option>
            <option value="last_name">Apellido</option>
            <option value="dni">DNI</option>
          </select>
        </div>

        <div className="cliente-listado__field cliente-listado__field--valor">
          <label htmlFor="listado-buscar">Buscar</label>
          <input
            id="listado-buscar"
            name="buscar"
            type="text"
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          Buscar
        </button>
      </form>

      <p className="cliente-listado__hint">
        Podés buscar por Nombre, Apellido o DNI.
      </p>

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
