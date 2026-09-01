import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { buscarVenta, listarVentas } from "../../app/frontend/api/ventasApi.js";
import { VentasListado } from "../../app/frontend/components/VentasListado.jsx";

vi.mock("../../app/frontend/api/ventasApi.js", () => ({
  listarVentas: vi.fn(),
  buscarVenta: vi.fn(),
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

  it("la columna Fecha muestra año-mes-día, sin hora", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: false });

    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");
    expect(screen.getByText("2026-01-15")).toBeInTheDocument();
    expect(screen.getByText("2026-01-10")).toBeInTheDocument();
    expect(screen.queryByText("2026-01-15T10:00:00+00:00")).not.toBeInTheDocument();
  });

  it("cada fila tiene una acción para ver el detalle de esa venta", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: false });

    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");
    expect(screen.getByRole("button", { name: "Ver detalle de la venta 1" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Ver detalle de la venta 2" })).toBeInTheDocument();
  });

  it("ver detalle de una venta muestra sus ítems, total, fecha y cliente en un modal", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: false });
    buscarVenta.mockResolvedValue({
      success: true,
      sale: {
        id: 1,
        sale_date: "2026-01-15T10:00:00+00:00",
        customer: { dni: 30111222, first_name: "Juan", last_name: "Perez" },
        items: [
          { sku: "ABC123", name: "Coca-Cola 500ml", quantity: 2, unit_price: 350.5, subtotal: 701 },
        ],
        total: 701,
        status: "Confirmada",
      },
    });
    const user = userEvent.setup();
    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");
    await user.click(screen.getByRole("button", { name: "Ver detalle de la venta 1" }));

    expect(buscarVenta).toHaveBeenCalledWith(1);
    expect(await screen.findByText("Coca-Cola 500ml")).toBeInTheDocument();
    const dialog = screen.getByRole("dialog");
    expect(within(dialog).getByText("Total: 701")).toBeInTheDocument();
    expect(within(dialog).getByText("Estado: Confirmada")).toBeInTheDocument();
  });

  it("ver detalle de una venta inexistente muestra 'Venta no encontrada' en el modal", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: false });
    buscarVenta.mockResolvedValue({
      success: false,
      errors: [{ field: "id", message: "Venta no encontrada" }],
    });
    const user = userEvent.setup();
    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");
    await user.click(screen.getByRole("button", { name: "Ver detalle de la venta 1" }));

    expect(await screen.findByText("Venta no encontrada")).toBeInTheDocument();
  });

  it("cerrar el modal conserva la página y los filtros del listado de fondo", async () => {
    listarVentas.mockResolvedValue({ success: true, sales: SALES, page: 1, hasNext: true });
    buscarVenta.mockResolvedValue({
      success: true,
      sale: {
        id: 1,
        sale_date: "2026-01-15T10:00:00+00:00",
        customer: { dni: 30111222, first_name: "Juan", last_name: "Perez" },
        items: [],
        total: 0,
        status: "Confirmada",
      },
    });
    const user = userEvent.setup();
    render(<VentasListado />);

    await screen.findByText("Juan Perez (30111222)");
    await user.type(screen.getByLabelText("DNI del cliente"), "3011");
    await user.click(screen.getByRole("button", { name: "Buscar" }));
    const llamadasAntes = listarVentas.mock.calls.length;

    await user.click(screen.getByRole("button", { name: "Ver detalle de la venta 1" }));
    await screen.findByRole("button", { name: "Cerrar" });
    await user.click(screen.getByRole("button", { name: "Cerrar" }));

    expect(listarVentas.mock.calls.length).toBe(llamadasAntes);
    expect(screen.getByText("Juan Perez (30111222)")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Cerrar" })).not.toBeInTheDocument();
  });
});
