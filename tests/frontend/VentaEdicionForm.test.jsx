import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  buscarProducto,
  buscarProductosParaVenta,
} from "../../app/frontend/api/productosApi.js";
import {
  buscarVenta,
  buscarVentasDeCliente,
  cerrarVenta,
  reemplazarDetalleVenta,
} from "../../app/frontend/api/ventasApi.js";
import { VentaEdicionForm } from "../../app/frontend/components/VentaEdicionForm.jsx";

vi.mock("../../app/frontend/api/productosApi.js", () => ({
  buscarProducto: vi.fn(),
  buscarProductosParaVenta: vi.fn(),
}));
vi.mock("../../app/frontend/api/ventasApi.js", () => ({
  buscarVenta: vi.fn(),
  buscarVentasDeCliente: vi.fn(),
  reemplazarDetalleVenta: vi.fn(),
  cerrarVenta: vi.fn(),
}));

const DRAFT_SALE_SUMMARY = { id: 1, sale_date: "2026-01-15", status: "Borrador", total: 701 };
const CONFIRMED_SALE_SUMMARY = { id: 2, sale_date: "2026-01-10", status: "Confirmada", total: 200 };

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
};

afterEach(() => {
  vi.clearAllMocks();
});

async function buscarCliente(user, dni = "30111222") {
  await user.type(screen.getByLabelText("DNI del cliente"), dni);
  await user.click(screen.getByRole("button", { name: "Buscar ventas" }));
}

async function abrirEdicionDeVentaBorrador(user) {
  buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
  await user.click(await screen.findByRole("button", { name: "Editar venta 1" }));
  await screen.findByLabelText("Producto");
}

async function elegirProducto(user, { criterio = "sprite", product = ACTIVE_PRODUCT } = {}) {
  await user.type(screen.getByLabelText("Producto"), criterio);
  const opcion = await screen.findByRole("button", {
    name: `${product.name} (${product.sku})`,
  });
  await user.click(opcion);
}

async function agregarItem(user, { criterio = "sprite", product = ACTIVE_PRODUCT, quantity = "3" } = {}) {
  await elegirProducto(user, { criterio, product });
  await user.type(screen.getByLabelText("Cantidad"), quantity);
  await user.click(screen.getByRole("button", { name: "Agregar" }));
}

describe("VentaEdicionForm — búsqueda por cliente", () => {
  it("muestra 'Cliente no encontrado' y no renderiza la lista", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);

    expect(await screen.findByText("Cliente no encontrado")).toBeInTheDocument();
    expect(screen.queryByLabelText("Producto")).not.toBeInTheDocument();
  });

  it("muestra el mensaje de sin ventas cuando el cliente no tiene ninguna", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [] });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);

    expect(
      await screen.findByText("El cliente no tiene ventas registradas")
    ).toBeInTheDocument();
  });

  it("lista todas las ventas del cliente, con el ícono de editar deshabilitado fuera de Borrador", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: true,
      sales: [DRAFT_SALE_SUMMARY, CONFIRMED_SALE_SUMMARY],
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);

    expect(await screen.findByText("Borrador")).toBeInTheDocument();
    expect(screen.getByText("Confirmada")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Editar venta 1" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Editar venta 2" })).toBeDisabled();
  });

  it("muestra la fecha en formato año-mes-día, sin hora", async () => {
    buscarVentasDeCliente.mockResolvedValue({
      success: true,
      sales: [{ id: 1, sale_date: "2026-01-15T10:00:00+00:00", status: "Borrador", total: 701 }],
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);

    expect(await screen.findByText("2026-01-15")).toBeInTheDocument();
    expect(screen.queryByText("2026-01-15T10:00:00+00:00")).not.toBeInTheDocument();
  });

  it("presionar editar sobre una venta en Borrador abre la vista de edición", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await user.click(await screen.findByRole("button", { name: "Editar venta 1" }));

    expect(await screen.findByLabelText("Producto")).toBeInTheDocument();
    expect(screen.getByText("Coca-Cola 500ml")).toBeInTheDocument();
  });

  it("si la venta ya no está en Borrador al presionar editar, advierte y no abre la edición", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    buscarVenta.mockResolvedValue({
      success: true,
      sale: { id: 1, status: "Confirmada", items: [] },
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await user.click(await screen.findByRole("button", { name: "Editar venta 1" }));

    expect(
      await screen.findByText("La venta ya no admite modificaciones")
    ).toBeInTheDocument();
    expect(screen.queryByLabelText("Producto")).not.toBeInTheDocument();
  });

  it("'Volver a la lista' regresa a la lista de ventas del cliente", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    buscarVenta.mockResolvedValue({ success: true, sale: DRAFT_SALE });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await user.click(await screen.findByRole("button", { name: "Editar venta 1" }));
    await screen.findByLabelText("Producto");

    await user.click(screen.getByRole("button", { name: "Volver a la lista" }));

    expect(await screen.findByRole("button", { name: "Editar venta 1" })).toBeInTheDocument();
    expect(screen.queryByLabelText("Producto")).not.toBeInTheDocument();
    expect(buscarVentasDeCliente).toHaveBeenLastCalledWith("30111222");
  });
});

describe("VentaEdicionForm — selección de producto (HU-VEN-05)", () => {
  it("muestra las opciones encontradas al escribir un criterio", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await user.type(screen.getByLabelText("Producto"), "sprite");

    expect(
      await screen.findByRole("button", { name: "Sprite 500ml (XYZ999)" })
    ).toBeInTheDocument();
  });

  it("muestra 'No se encontraron productos' sin coincidencias", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    buscarProductosParaVenta.mockResolvedValue({ products: [] });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await user.type(screen.getByLabelText("Producto"), "gaseosa");

    expect(await screen.findByText("No se encontraron productos")).toBeInTheDocument();
  });

  it("cambiar el texto tras elegir un producto descarta la selección (Agregar deshabilitado)", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await elegirProducto(user);
    await user.type(screen.getByLabelText("Cantidad"), "3");
    expect(screen.getByRole("button", { name: "Agregar" })).toBeEnabled();

    await user.type(screen.getByLabelText("Producto"), " x");

    expect(screen.getByRole("button", { name: "Agregar" })).toBeDisabled();
  });
});

describe("VentaEdicionForm — edición del detalle", () => {
  it("avisa cantidad inválida al perder el foco, antes de presionar Agregar", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await user.type(screen.getByLabelText("Cantidad"), "0");
    await user.click(screen.getByLabelText("Producto"));

    expect(
      await screen.findByText("El valor debe ser un número positivo")
    ).toBeInTheDocument();
    expect(buscarProducto).not.toHaveBeenCalled();
  });

  it("agrega un producto nuevo sin llamar a buscarProducto y recalcula el total", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await agregarItem(user, { quantity: "3" });

    expect(await screen.findByText("Sprite 500ml")).toBeInTheDocument();
    expect(screen.getByText("Total: 1301")).toBeInTheDocument();
    expect(buscarProducto).not.toHaveBeenCalled();
  });

  it("quita un producto del detalle y recalcula el total", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await user.click(screen.getByRole("button", { name: "Quitar" }));

    expect(screen.queryByText("Coca-Cola 500ml")).not.toBeInTheDocument();
    expect(screen.getByText("Total: 0")).toBeInTheDocument();
  });

  it("guardar cambios con múltiples errores del backend los muestra todos juntos", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    reemplazarDetalleVenta.mockResolvedValue({
      success: false,
      errors: [
        { field: "items[0].sku", message: "El producto no está disponible para la venta" },
        { field: "items[0].quantity", message: "No hay stock suficiente para completar la operación" },
      ],
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
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
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    reemplazarDetalleVenta.mockResolvedValue({
      success: true,
      message: "Detalle actualizado exitosamente",
      sale: { ...DRAFT_SALE, total: 701 },
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await user.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("Detalle actualizado exitosamente")
    ).toBeInTheDocument();
  });
});

describe("VentaEdicionForm — cierre", () => {
  it("cerrar exitosamente muestra el mensaje de éxito", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    cerrarVenta.mockResolvedValue({
      success: true,
      message: "Venta cerrada exitosamente",
      sale: { ...DRAFT_SALE, status: "Confirmada" },
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await user.click(screen.getByRole("button", { name: "Cerrar venta" }));
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(cerrarVenta).toHaveBeenCalledWith(1);
    expect(await screen.findByText("Venta cerrada exitosamente")).toBeInTheDocument();
  });

  it("si el backend rechaza el cierre (stock insuficiente), muestra ese mensaje en vez de éxito", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    cerrarVenta.mockResolvedValue({
      success: false,
      errors: [
        { field: "items", message: "No hay stock suficiente para completar la operación" },
      ],
    });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await user.click(screen.getByRole("button", { name: "Cerrar venta" }));
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(
      await screen.findByText("No hay stock suficiente para completar la operación")
    ).toBeInTheDocument();
    expect(screen.queryByText("Venta cerrada exitosamente")).not.toBeInTheDocument();
  });

  it("cancelar el cierre no llama a cerrarVenta", async () => {
    buscarVentasDeCliente.mockResolvedValue({ success: true, sales: [DRAFT_SALE_SUMMARY] });
    const user = userEvent.setup();
    render(<VentaEdicionForm />);

    await buscarCliente(user);
    await abrirEdicionDeVentaBorrador(user);
    await user.click(screen.getByRole("button", { name: "Cerrar venta" }));
    await user.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(cerrarVenta).not.toHaveBeenCalled();
  });
});
