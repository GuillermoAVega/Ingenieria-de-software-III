import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { listarVentas } from "../../app/frontend/api/ventasApi.js";
import { VentasListado } from "../../app/frontend/components/VentasListado.jsx";

vi.mock("../../app/frontend/api/ventasApi.js", () => ({
  listarVentas: vi.fn(),
}));

afterEach(() => {
  vi.clearAllMocks();
});

const SALES = [
  {
    id: 1,
    sale_date: "2026-01-15T10:00:00+00:00",
    customer: { dni: 30111222, first_name: "Juan", last_name: "Perez" },
    total: 701,
  },
  {
    id: 2,
    sale_date: "2026-01-10T10:00:00+00:00",
    customer: { dni: 40222333, first_name: "Ana", last_name: "Diaz" },
    total: 200,
  },
];

describe("VentasListado", () => {
  it("al montarse, pide la página 1 sin filtros y renderiza la tabla con los resultados", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: false });

    render(<VentasListado />);

    expect(await screen.findByText("Juan Perez (30111222)")).toBeInTheDocument();
    expect(screen.getByText("Ana Diaz (40222333)")).toBeInTheDocument();
    expect(listarVentas).toHaveBeenCalledWith({
      dni: undefined,
      dateFrom: undefined,
      dateTo: undefined,
      page: 1,
    });
  });

  it("filtrar por fecha y DNI llama a listarVentas con ambos valores", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: false });
    const user = userEvent.setup();
    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");
    const desde = screen.getByLabelText("Desde");
    const hasta = screen.getByLabelText("Hasta");
    await user.type(desde, "2026-01-01");
    await user.type(hasta, "2026-01-31");
    await user.type(screen.getByLabelText("DNI del cliente"), "3011");
    await user.click(screen.getByRole("button", { name: "Buscar" }));

    expect(listarVentas).toHaveBeenLastCalledWith({
      dni: "3011",
      dateFrom: "2026-01-01",
      dateTo: "2026-01-31",
      page: 1,
    });
  });

  it("borrar los filtros y volver a buscar llama sin ellos", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: false });
    const user = userEvent.setup();
    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");
    const dniInput = screen.getByLabelText("DNI del cliente");
    await user.type(dniInput, "3011");
    await user.click(screen.getByRole("button", { name: "Buscar" }));
    await user.clear(dniInput);
    await user.click(screen.getByRole("button", { name: "Buscar" }));

    expect(listarVentas).toHaveBeenLastCalledWith({
      dni: undefined,
      dateFrom: undefined,
      dateTo: undefined,
      page: 1,
    });
  });

  it("muestra 'no se encontraron resultados' cuando sales viene vacío", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: [], page: 1, hasNext: false });

    render(<VentasListado />);

    expect(await screen.findByText("No se encontraron resultados")).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("muestra el mensaje de rango de fechas inválido devuelto por el backend", async () => {
    listarVentas.mockResolvedValue({
      success: false,
      errors: [{ field: "date_range", message: "El rango de fechas es inválido" }],
    });

    render(<VentasListado />);

    expect(await screen.findByText("El rango de fechas es inválido")).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("con hasNext:true, 'Siguiente' está habilitado y pide la página 2", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: true });
    const user = userEvent.setup();
    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");
    const siguiente = screen.getByRole("button", { name: "Siguiente" });
    expect(siguiente).toBeEnabled();

    await user.click(siguiente);

    expect(listarVentas).toHaveBeenLastCalledWith({
      dni: undefined,
      dateFrom: undefined,
      dateTo: undefined,
      page: 2,
    });
  });

  it("con hasNext:false, 'Siguiente' está deshabilitado", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: false });
    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");

    expect(screen.getByRole("button", { name: "Siguiente" })).toBeDisabled();
  });

  it("cambiar un filtro estando en la página 2 vuelve a pedir la página 1", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: true });
    const user = userEvent.setup();
    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");
    await user.click(screen.getByRole("button", { name: "Siguiente" }));
    expect(listarVentas).toHaveBeenLastCalledWith(
      expect.objectContaining({ page: 2 })
    );

    await user.type(screen.getByLabelText("DNI del cliente"), "3011");
    await user.click(screen.getByRole("button", { name: "Buscar" }));

    expect(listarVentas).toHaveBeenLastCalledWith(
      expect.objectContaining({ dni: "3011", page: 1 })
    );
  });
});
