import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { listarClientes } from "../../app/frontend/api/clientesApi.js";
import { ClienteListado } from "../../app/frontend/components/ClienteListado.jsx";

vi.mock("../../app/frontend/api/clientesApi.js", () => ({
  listarClientes: vi.fn(),
}));

afterEach(() => {
  vi.clearAllMocks();
});

const CUSTOMERS = [
  { dni: 30111222, first_name: "Juan", last_name: "Perez", status: "Activo" },
  { dni: 41234567, first_name: "Ana", last_name: "Lopez", status: "Inactivo" },
];

describe("ClienteListado", () => {
  it("al montarse, pide la página 1 sin filtro y renderiza la tabla con los resultados", async () => {
    listarClientes.mockResolvedValue({ customers: CUSTOMERS, page: 1, hasNext: false });

    render(<ClienteListado />);

    expect(await screen.findByText("Juan")).toBeInTheDocument();
    expect(screen.getByText("Perez")).toBeInTheDocument();
    expect(screen.getByText("Ana")).toBeInTheDocument();
    expect(screen.getByText("Inactivo")).toBeInTheDocument();
    expect(listarClientes).toHaveBeenCalledWith({ q: undefined, page: 1 });
  });

  it("buscar un criterio llama a listarClientes con ese q", async () => {
    listarClientes.mockResolvedValue({ customers: CUSTOMERS, page: 1, hasNext: false });
    const user = userEvent.setup();
    render(<ClienteListado />);

    await screen.findByText("Juan");
    await user.type(screen.getByLabelText("Buscar"), "perez");
    await user.click(screen.getByRole("button", { name: "Buscar" }));

    expect(listarClientes).toHaveBeenLastCalledWith({ q: "perez", page: 1 });
  });

  it("borrar el criterio y volver a buscar llama sin q", async () => {
    listarClientes.mockResolvedValue({ customers: CUSTOMERS, page: 1, hasNext: false });
    const user = userEvent.setup();
    render(<ClienteListado />);

    await screen.findByText("Juan");
    const input = screen.getByLabelText("Buscar");
    await user.type(input, "perez");
    await user.click(screen.getByRole("button", { name: "Buscar" }));
    await user.clear(input);
    await user.click(screen.getByRole("button", { name: "Buscar" }));

    expect(listarClientes).toHaveBeenLastCalledWith({ q: undefined, page: 1 });
  });

  it("muestra 'no se encontraron resultados' cuando customers viene vacío", async () => {
    listarClientes.mockResolvedValue({ customers: [], page: 1, hasNext: false });

    render(<ClienteListado />);

    expect(
      await screen.findByText("No se encontraron resultados")
    ).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("con hasNext:true, 'Siguiente' está habilitado y pide la página 2", async () => {
    listarClientes.mockResolvedValue({ customers: CUSTOMERS, page: 1, hasNext: true });
    const user = userEvent.setup();
    render(<ClienteListado />);

    await screen.findByText("Juan");
    const siguiente = screen.getByRole("button", { name: "Siguiente" });
    expect(siguiente).toBeEnabled();

    await user.click(siguiente);

    expect(listarClientes).toHaveBeenLastCalledWith({ q: undefined, page: 2 });
  });

  it("con hasNext:false, 'Siguiente' está deshabilitado", async () => {
    listarClientes.mockResolvedValue({ customers: CUSTOMERS, page: 1, hasNext: false });
    render(<ClienteListado />);

    await screen.findByText("Juan");

    expect(screen.getByRole("button", { name: "Siguiente" })).toBeDisabled();
  });

  it("cambiar el criterio estando en la página 2 vuelve a pedir la página 1", async () => {
    listarClientes.mockResolvedValue({ customers: CUSTOMERS, page: 1, hasNext: true });
    const user = userEvent.setup();
    render(<ClienteListado />);

    await screen.findByText("Juan");
    await user.click(screen.getByRole("button", { name: "Siguiente" }));
    expect(listarClientes).toHaveBeenLastCalledWith({ q: undefined, page: 2 });

    await user.type(screen.getByLabelText("Buscar"), "perez");
    await user.click(screen.getByRole("button", { name: "Buscar" }));

    expect(listarClientes).toHaveBeenLastCalledWith({ q: "perez", page: 1 });
  });
});
