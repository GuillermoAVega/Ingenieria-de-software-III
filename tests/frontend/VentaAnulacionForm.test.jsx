import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { anularVenta, buscarVenta } from "../../app/frontend/api/ventasApi.js";
import { VentaAnulacionForm } from "../../app/frontend/components/VentaAnulacionForm.jsx";

vi.mock("../../app/frontend/api/ventasApi.js", () => ({
  buscarVenta: vi.fn(),
  anularVenta: vi.fn(),
}));

afterEach(() => {
  vi.clearAllMocks();
});

async function buscar(user, id = "1") {
  await user.type(screen.getByLabelText("ID de la venta"), id);
  await user.click(screen.getByRole("button", { name: "Buscar venta" }));
}

describe("VentaAnulacionForm", () => {
  it("muestra 'venta no encontrada' y no renderiza botones de confirmación", async () => {
    buscarVenta.mockResolvedValue({
      success: false,
      errors: [{ field: "id", message: "Venta no encontrada" }],
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);

    expect(await screen.findByText("Venta no encontrada")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
  });

  it("muestra 'ya se encuentra anulada' y no llama a anularVenta para una venta Anulada", async () => {
    buscarVenta.mockResolvedValue({
      success: true,
      sale: { id: 1, total: 701, status: "Anulada" },
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);

    expect(
      await screen.findByText("La venta ya se encuentra anulada")
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
    expect(anularVenta).not.toHaveBeenCalled();
  });

  it("muestra el detalle de la venta y los botones Confirmar/Cancelar para una venta Confirmada", async () => {
    buscarVenta.mockResolvedValue({
      success: true,
      sale: { id: 1, total: 701, status: "Confirmada" },
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);

    expect(await screen.findByText("Venta #1 — Total 701")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Confirmar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cancelar" })).toBeInTheDocument();
  });

  it("al confirmar, llama a anularVenta y muestra el mensaje de éxito", async () => {
    buscarVenta.mockResolvedValue({
      success: true,
      sale: { id: 1, total: 701, status: "Confirmada" },
    });
    anularVenta.mockResolvedValue({
      success: true,
      message: "Venta anulada exitosamente",
      sale: { id: 1, total: 701, status: "Anulada" },
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(anularVenta).toHaveBeenCalledWith("1");
    expect(
      await screen.findByText("Venta anulada exitosamente")
    ).toBeInTheDocument();
  });

  it("al cancelar, no llama a anularVenta y oculta la confirmación", async () => {
    buscarVenta.mockResolvedValue({
      success: true,
      sale: { id: 1, total: 701, status: "Confirmada" },
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(anularVenta).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
  });

  it("si el backend rechaza al confirmar (ya anulada por otra vía), muestra ese mensaje en vez de éxito", async () => {
    buscarVenta.mockResolvedValue({
      success: true,
      sale: { id: 1, total: 701, status: "Confirmada" },
    });
    anularVenta.mockResolvedValue({
      success: false,
      errors: [{ field: "id", message: "La venta ya se encuentra anulada" }],
    });
    const user = userEvent.setup();
    render(<VentaAnulacionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(
      await screen.findByText("La venta ya se encuentra anulada")
    ).toBeInTheDocument();
    expect(screen.queryByText("Venta anulada exitosamente")).not.toBeInTheDocument();
  });
});
