import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { buscarProducto } from "../../app/frontend/api/productosApi.js";
import { buscarVenta, cerrarVenta, reemplazarDetalleVenta } from "../../app/frontend/api/ventasApi.js";
import { VentaEdicionForm } from "../../app/frontend/components/VentaEdicionForm.jsx";

vi.mock("../../app/frontend/api/productosApi.js", () => ({
  buscarProducto: vi.fn(),
}));
vi.mock("../../app/frontend/api/ventasApi.js", () => ({
  buscarVenta: vi.fn(),
  reemplazarDetalleVenta: vi.fn(),
  cerrarVenta: vi.fn(),
}));

const DRAFT_SALE = {
  id: 1,
  status: "Borrador",
  total: 701,
  items: [
    { sku: "ABC123", name: "Coca-Cola 500ml", quantity: 2, unit_price: 350.5, subtotal: 701 },
  ],
};

const ACTIVE_PRODUCT = {
  sku: "XYZ999",
  name: "Sprite 500ml",
  unit_price: 200,
  stock: 10,
  status: "Activo",
};

afterEach(() => {
  vi.clearAllMocks();
});

async function buscar(user, id = "1") {
  await user.type(screen.getByLabelText("ID de la venta"), id);
  await user.click(screen.getByRole("button", { name: "Buscar venta" }));
}

describe("VentaEdicionForm — búsqueda", () => {
  it("muestra 'Venta no encontrada' y no renderiza el editor", async () => {
    buscarVenta.mockResolvedValue({
      success: false,
      errors: [{ field: "id", message: "Venta no encontrada" }],
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);

    expect(await screen.findByText("Venta no encontrada")).toBeInTheDocument();
    expect(screen.queryByLabelText("SKU")).not.toBeInTheDocument();
  });

  it("muestra 'no admite modificaciones' para una venta Confirmada, sin controles de edición", async () => {
    buscarVenta.mockResolvedValue({
      success: true,
      sale: { id: 1, status: "Confirmada", total: 701, items: [] },
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);

    expect(
      await screen.findByText("La venta ya no admite modificaciones")
    ).toBeInTheDocument();
    expect(screen.queryByLabelText("SKU")).not.toBeInTheDocument();
  });

  it("muestra el detalle editable para una venta en Borrador", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);

    expect(await screen.findByLabelText("SKU")).toBeInTheDocument();
    expect(screen.getByText("Coca-Cola 500ml")).toBeInTheDocument();
    expect(screen.getByText("701")).toBeInTheDocument();
  });
});

describe("VentaEdicionForm — edición del detalle", () => {
  it("avisa cantidad inválida al perder el foco, antes de presionar Agregar", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);
    await screen.findByLabelText("SKU");
    await user.type(screen.getByLabelText("Cantidad"), "0");
    await user.click(screen.getByLabelText("SKU"));

    expect(
      await screen.findByText("El valor debe ser un número positivo")
    ).toBeInTheDocument();
    expect(buscarProducto).not.toHaveBeenCalled();
  });

  it("un error de SKU vigente no se borra al perder el foco de Cantidad con un valor válido", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    buscarProducto.mockResolvedValue({
      success: false,
      errors: [{ field: "sku", message: "Producto no encontrado" }],
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);
    await screen.findByLabelText("SKU");
    await user.type(screen.getByLabelText("SKU"), "NOEXISTE");
    await user.type(screen.getByLabelText("Cantidad"), "1");
    await user.click(screen.getByRole("button", { name: "Agregar" }));
    await screen.findByText("Producto no encontrado");

    const cantidadInput = screen.getByLabelText("Cantidad");
    await user.clear(cantidadInput);
    await user.type(cantidadInput, "3");
    await user.click(screen.getByLabelText("SKU"));

    expect(screen.getByText("Producto no encontrado")).toBeInTheDocument();
  });

  it("agrega un producto nuevo y recalcula el total", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    buscarProducto.mockResolvedValue({ success: true, product: ACTIVE_PRODUCT });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);
    await screen.findByLabelText("SKU");
    await user.type(screen.getByLabelText("SKU"), "XYZ999");
    await user.type(screen.getByLabelText("Cantidad"), "3");
    await user.click(screen.getByRole("button", { name: "Agregar" }));

    expect(await screen.findByText("Sprite 500ml")).toBeInTheDocument();
    expect(screen.getByText("Total: 1301")).toBeInTheDocument();
  });

  it("quita un producto del detalle y recalcula el total", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);
    await screen.findByText("Coca-Cola 500ml");
    await user.click(screen.getByRole("button", { name: "Quitar" }));

    expect(screen.queryByText("Coca-Cola 500ml")).not.toBeInTheDocument();
    expect(screen.getByText("Total: 0")).toBeInTheDocument();
  });

  it("guardar cambios con múltiples errores del backend los muestra todos juntos", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    reemplazarDetalleVenta.mockResolvedValue({
      success: false,
      errors: [
        { field: "items[0].sku", message: "El producto no está disponible para la venta" },
        { field: "items[0].quantity", message: "No hay stock suficiente para completar la operación" },
      ],
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);
    await screen.findByText("Coca-Cola 500ml");
    await user.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("El producto no está disponible para la venta")
    ).toBeInTheDocument();
    expect(
      screen.getByText("No hay stock suficiente para completar la operación")
    ).toBeInTheDocument();
    expect(screen.getByText("Coca-Cola 500ml")).toBeInTheDocument();
  });

  it("guardar cambios exitoso muestra el mensaje de éxito", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    reemplazarDetalleVenta.mockResolvedValue({
      success: true,
      message: "Detalle actualizado exitosamente",
      sale: { ...DRAFT_SALE, total: 701 },
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);
    await screen.findByText("Coca-Cola 500ml");
    await user.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("Detalle actualizado exitosamente")
    ).toBeInTheDocument();
  });
});

describe("VentaEdicionForm — cierre", () => {
  it("cerrar exitosamente muestra el mensaje de éxito", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    cerrarVenta.mockResolvedValue({
      success: true,
      message: "Venta cerrada exitosamente",
      sale: { ...DRAFT_SALE, status: "Confirmada" },
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);
    await screen.findByText("Coca-Cola 500ml");
    await user.click(screen.getByRole("button", { name: "Cerrar venta" }));
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(cerrarVenta).toHaveBeenCalledWith(1);
    expect(await screen.findByText("Venta cerrada exitosamente")).toBeInTheDocument();
  });

  it("si el backend rechaza el cierre (stock insuficiente), muestra ese mensaje en vez de éxito", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    cerrarVenta.mockResolvedValue({
      success: false,
      errors: [
        { field: "items", message: "No hay stock suficiente para completar la operación" },
      ],
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);
    await screen.findByText("Coca-Cola 500ml");
    await user.click(screen.getByRole("button", { name: "Cerrar venta" }));
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(
      await screen.findByText("No hay stock suficiente para completar la operación")
    ).toBeInTheDocument();
    expect(screen.queryByText("Venta cerrada exitosamente")).not.toBeInTheDocument();
  });

  it("cancelar el cierre no llama a cerrarVenta", async () => {
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscar(user);
    await screen.findByText("Coca-Cola 500ml");
    await user.click(screen.getByRole("button", { name: "Cerrar venta" }));
    await user.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(cerrarVenta).not.toHaveBeenCalled();
  });
});
