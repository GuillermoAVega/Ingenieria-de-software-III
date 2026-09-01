import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { anularVenta, buscarVentasDeCliente } from "../../app/frontend/api/ventasApi.js";
import { VentaAnulacionForm } from "../../app/frontend/components/VentaAnulacionForm.jsx";

vi.mock("../../app/frontend/api/ventasApi.js", () => ({
  buscarVentasDeCliente: vi.fn(),
  anularVenta: vi.fn(),
}));

afterEach(() => {
  vi.clearAllMocks();
});

async function buscar(user, dni = "30111222") {
  await user.type(screen.getByLabelText("DNI del cliente"), dni);
  await user.click(screen.getByRole("button", { name: "Buscar ventas" }));
}

describe("VentaAnulacionForm", () => {
  it("muestra 'Cliente no encontrado' y no renderiza la lista", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);

    expect(await screen.findByText("Cliente no encontrado")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Anular" })).not.toBeInTheDocument();
  });

  it("muestra el mensaje de sin ventas confirmadas cuando el cliente no tiene ninguna", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: true,
      sales: [{ id: 1, sale_date: "2026-01-01", status: "Borrador", total: 100 }],
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);

    expect(
      await screen.findByText("El cliente no tiene ventas confirmadas para anular")
    ).toBeInTheDocument();
  });

  it("lista todas las ventas Confirmada del cliente", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: true,
      sales: [
        { id: 1, sale_date: "2026-01-15", status: "Confirmada", total: 701 },
        { id: 2, sale_date: "2026-01-10", status: "Confirmada", total: 200 },
        { id: 3, sale_date: "2026-01-05", status: "Borrador", total: 50 },
      ],
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);

    expect(await screen.findByText("701")).toBeInTheDocument();
    expect(screen.getByText("200")).toBeInTheDocument();
    expect(screen.queryByText("50")).not.toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Anular" })).toHaveLength(2);
  });

  it("muestra la fecha en formato año-mes-día, sin hora", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: true,
      sales: [
        { id: 1, sale_date: "2026-01-15T10:00:00+00:00", status: "Confirmada", total: 701 },
      ],
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);

    expect(await screen.findByText("2026-01-15")).toBeInTheDocument();
    expect(screen.queryByText("2026-01-15T10:00:00+00:00")).not.toBeInTheDocument();
  });

  it("presionar 'Anular' en una fila abre la confirmación con los datos de esa venta", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: true,
      sales: [
        { id: 1, sale_date: "2026-01-15", status: "Confirmada", total: 701 },
        { id: 2, sale_date: "2026-01-10", status: "Confirmada", total: 200 },
      ],
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);
    await screen.findByText("701");
    const filas = screen.getAllByRole("button", { name: "Anular" });
    await user.click(filas[1]);

    expect(await screen.findByText("Venta #2 — Total 200")).toBeInTheDocument();
  });

  it("al confirmar, llama a anularVenta y muestra el mensaje de éxito", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: true,
      sales: [{ id: 1, sale_date: "2026-01-15", status: "Confirmada", total: 701 }],
    });
    anularVenta.mockResolvedValue({
      success: true,
      message: "Venta anulada exitosamente",
      sale: { id: 1, status: "Anulada" },
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Anular" }));
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(anularVenta).toHaveBeenCalledWith(1);
    expect(
      await screen.findByText("Venta anulada exitosamente")
    ).toBeInTheDocument();
  });

  it("tras anular con éxito, vuelve a pedir la lista del mismo DNI", async () => {
    buscarVentasDeCliente
      .mockResolvedValueOnce({
        success: true,
        sales: [{ id: 1, sale_date: "2026-01-15", status: "Confirmada", total: 701 }],
      })
      .mockResolvedValueOnce({ success: true, sales: [] });
    anularVenta.mockResolvedValue({
      success: true,
      message: "Venta anulada exitosamente",
      sale: { id: 1, status: "Anulada" },
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Anular" }));
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    await screen.findByText("Venta anulada exitosamente");
    expect(buscarVentasDeCliente).toHaveBeenCalledTimes(2);
    expect(buscarVentasDeCliente).toHaveBeenLastCalledWith("30111222");
  });

  it("al cancelar, no llama a anularVenta y conserva la lista", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: true,
      sales: [{ id: 1, sale_date: "2026-01-15", status: "Confirmada", total: 701 }],
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Anular" }));
    await user.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(anularVenta).not.toHaveBeenCalled();
    expect(screen.getByText("701")).toBeInTheDocument();
  });

  it("si el backend rechaza al confirmar (condición de carrera), muestra ese mensaje en vez de éxito", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: true,
      sales: [{ id: 1, sale_date: "2026-01-15", status: "Confirmada", total: 701 }],
    });
    anularVenta.mockResolvedValue({
      success: false,
      errors: [{ field: "id", message: "La venta ya se encuentra anulada" }],
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Anular" }));
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(
      await screen.findByText("La venta ya se encuentra anulada")
    ).toBeInTheDocument();
    expect(screen.queryByText("Venta anulada exitosamente")).not.toBeInTheDocument();
  });
});
