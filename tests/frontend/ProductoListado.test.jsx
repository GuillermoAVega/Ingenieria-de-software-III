import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { listarProductos } from "../../app/frontend/api/productosApi.js";
import { ProductoListado } from "../../app/frontend/components/ProductoListado.jsx";

vi.mock("../../app/frontend/api/productosApi.js", () => ({
  listarProductos: vi.fn(),
}));

afterEach(() => {
  vi.clearAllMocks();
});

const PRODUCTS = [
  { sku: "ABC123", name: "Coca-Cola 500ml", brand: "Coca-Cola", unit_price: 350.5, stock: 100, status: "Activo" },
  { sku: "XYZ999", name: "Otro producto", brand: "Otra marca", unit_price: 10, stock: 5, status: "Inactivo" },
];

describe("ProductoListado", () => {
  it("al montarse, pide la página 1 sin filtro y renderiza la tabla con los resultados", async () => {
    listarProductos.mockResolvedValue({ products: PRODUCTS, page: 1, hasNext: false });

    render(<ProductoListado />);

    expect(await screen.findByText("Coca-Cola 500ml")).toBeInTheDocument();
    expect(screen.getByText("Otro producto")).toBeInTheDocument();
    expect(screen.getByText("Inactivo")).toBeInTheDocument();
    expect(listarProductos).toHaveBeenCalledWith({ q: undefined, page: 1 });
  });

  it("buscar un criterio llama a listarProductos con ese q", async () => {
    listarProductos.mockResolvedValue({ products: PRODUCTS, page: 1, hasNext: false });
    const user = userEvent.setup();
    render(<ProductoListado />);

    await screen.findByText("Coca-Cola 500ml");
    await user.type(screen.getByLabelText("Buscar"), "coca");
    await user.click(screen.getByRole("button", { name: "Buscar" }));

    expect(listarProductos).toHaveBeenLastCalledWith({ q: "coca", page: 1 });
  });

  it("borrar el criterio y volver a buscar llama sin q", async () => {
    listarProductos.mockResolvedValue({ products: PRODUCTS, page: 1, hasNext: false });
    const user = userEvent.setup();
    render(<ProductoListado />);

    await screen.findByText("Coca-Cola 500ml");
    const input = screen.getByLabelText("Buscar");
    await user.type(input, "coca");
    await user.click(screen.getByRole("button", { name: "Buscar" }));
    await user.clear(input);
    await user.click(screen.getByRole("button", { name: "Buscar" }));

    expect(listarProductos).toHaveBeenLastCalledWith({ q: undefined, page: 1 });
  });

  it("muestra 'no se encontraron resultados' cuando products viene vacío", async () => {
    listarProductos.mockResolvedValue({ products: [], page: 1, hasNext: false });

    render(<ProductoListado />);

    expect(
      await screen.findByText("No se encontraron resultados")
    ).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("con hasNext:true, 'Siguiente' está habilitado y pide la página 2", async () => {
    listarProductos.mockResolvedValue({ products: PRODUCTS, page: 1, hasNext: true });
    const user = userEvent.setup();
    render(<ProductoListado />);

    await screen.findByText("Coca-Cola 500ml");
    const siguiente = screen.getByRole("button", { name: "Siguiente" });
    expect(siguiente).toBeEnabled();

    await user.click(siguiente);

    expect(listarProductos).toHaveBeenLastCalledWith({ q: undefined, page: 2 });
  });

  it("con hasNext:false, 'Siguiente' está deshabilitado", async () => {
    listarProductos.mockResolvedValue({ products: PRODUCTS, page: 1, hasNext: false });
    render(<ProductoListado />);

    await screen.findByText("Coca-Cola 500ml");

    expect(screen.getByRole("button", { name: "Siguiente" })).toBeDisabled();
  });

  it("cambiar el criterio estando en la página 2 vuelve a pedir la página 1", async () => {
    listarProductos.mockResolvedValue({ products: PRODUCTS, page: 1, hasNext: true });
    const user = userEvent.setup();
    render(<ProductoListado />);

    await screen.findByText("Coca-Cola 500ml");
    await user.click(screen.getByRole("button", { name: "Siguiente" }));
    expect(listarProductos).toHaveBeenLastCalledWith({ q: undefined, page: 2 });

    await user.type(screen.getByLabelText("Buscar"), "coca");
    await user.click(screen.getByRole("button", { name: "Buscar" }));

    expect(listarProductos).toHaveBeenLastCalledWith({ q: "coca", page: 1 });
  });
});
