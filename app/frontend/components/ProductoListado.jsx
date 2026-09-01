import { useEffect, useState } from "react";

import { listarProductos } from "../api/productosApi.js";
import "./ProductoListado.css";

/**
 * Listado y filtro de productos (HU-PROD-04).
 * @returns {import("react").JSX.Element}
 */
export function ProductoListado() {
  const [searchInput, setSearchInput] = useState("");
  const [products, setProducts] = useState(
    /** @type {import("../api/productosApi.js").Producto[]} */ ([])
  );
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [appliedQuery, setAppliedQuery] = useState(/** @type {string | undefined} */ (undefined));
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    listarProductos({ q: appliedQuery, page }).then((result) => {
      if (cancelled) {
        return;
      }
      setProducts(result.products);
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
    <div className="producto-listado">
      <form className="producto-listado__search" onSubmit={handleSearch}>
        <label htmlFor="listado-buscar-producto">Buscar</label>
        <input
          id="listado-buscar-producto"
          name="buscar"
          type="text"
          value={searchInput}
          onChange={(event) => setSearchInput(event.target.value)}
        />
        <button type="submit" disabled={isLoading}>
          Buscar
        </button>
      </form>

      <p className="producto-listado__hint">
        Podés buscar por Nombre o Código/SKU.
      </p>

      {!isLoading && products.length === 0 ? (
        <p className="producto-listado__banner" role="status">
          No se encontraron resultados
        </p>
      ) : (
        <table className="producto-listado__table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Nombre</th>
              <th>Marca</th>
              <th>Precio</th>
              <th>Stock</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.sku}>
                <td>{product.sku}</td>
                <td>{product.name}</td>
                <td>{product.brand}</td>
                <td>{product.unit_price}</td>
                <td>{product.stock}</td>
                <td>{product.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="producto-listado__pagination">
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
