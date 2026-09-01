import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { buscarCliente } from "../../app/frontend/api/clientesApi.js";
import {
  buscarProducto,
  buscarProductosParaVenta,
} from "../../app/frontend/api/productosApi.js";
import { registrarVenta } from "../../app/frontend/api/ventasApi.js";
import { VentaForm } from "../../app/frontend/components/VentaForm.jsx";

vi.mock("../../app/frontend/api/clientesApi.js", () => ({
  buscarCliente: vi.fn(),
}));
vi.mock("../../app/frontend/api/productosApi.js", () => ({
  buscarProducto: vi.fn(),
  buscarProductosParaVenta: vi.fn(),
}));
vi.mock("../../app/frontend/api/ventasApi.js", () => ({
  registrarVenta: vi.fn(),
}));

const ACTIVE_CUSTOMER = {
  dni: 30111222,
  first_name: "Juan",
  last_name: "Perez",
  status: "Activo",
};

const INACTIVE_CUSTOMER = { ...ACTIVE_CUSTOMER, status: "Inactivo" };

const ACTIVE_PRODUCT = {
  sku: "ABC123",
  name: "Coca-Cola 500ml",
  unit_price: 350.5,
  stock: 10,
};

afterEach(() => {
  vi.clearAllMocks();
});

async function buscarClienteActivo(user) {
  await user.type(screen.getByLabelText("DNI del cliente"), "30111222");
  await user.click(screen.getByRole("button", { name: "Buscar cliente" }));
  await screen.findByText("Juan Perez");
}

/**
 * Escribe en el campo "Producto", espera las opciones devueltas por
 * `buscarProductosParaVenta` (mockeado) y elige la indicada.
 */
async function elegirProducto(user, { criterio = "coca", product = ACTIVE_PRODUCT } = {}) {
  await user.type(screen.getByLabelText("Producto"), criterio);
  const opcion = await screen.findByRole("button", {
    name: `${product.name} (${product.sku})`,
  });
  await user.click(opcion);
}

async function agregarItem(user, { criterio = "coca", product = ACTIVE_PRODUCT, quantity = "2" } = {}) {
  await elegirProducto(user, { criterio, product });
  await user.type(screen.getByLabelText("Cantidad"), quantity);
  await user.click(screen.getByRole("button", { name: "Agregar" }));
}

describe("VentaForm — búsqueda de cliente", () => {
  it("muestra 'cliente no encontrado' y no habilita agregar ítems", async () => {
    buscarCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });
    const user = userEvent.setup();
    render(<VentaForm />);

    await user.type(screen.getByLabelText("DNI del cliente"), "30111222");
    await user.click(screen.getByRole("button", { name: "Buscar cliente" }));

    expect(await screen.findByText("Cliente no encontrado")).toBeInTheDocument();
    expect(screen.queryByLabelText("Producto")).not.toBeInTheDocument();
  });

  it("muestra advertencia para un cliente Inactivo y no habilita agregar ítems", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: INACTIVE_CUSTOMER });
    const user = userEvent.setup();
    render(<VentaForm />);

    await user.type(screen.getByLabelText("DNI del cliente"), "30111222");
    await user.click(screen.getByRole("button", { name: "Buscar cliente" }));

    expect(
      await screen.findByText("No se pueden emitir ventas a clientes dados de baja")
    ).toBeInTheDocument();
    expect(screen.queryByLabelText("Producto")).not.toBeInTheDocument();
  });

  it("con un cliente Activo, habilita agregar ítems", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);

    expect(screen.getByLabelText("Producto")).toBeInTheDocument();
  });
});

describe("VentaForm — selección de producto (HU-VEN-05)", () => {
  it("muestra las opciones encontradas al escribir un criterio", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await user.type(screen.getByLabelText("Producto"), "coca");

    expect(
      await screen.findByRole("button", { name: "Coca-Cola 500ml (ABC123)" })
    ).toBeInTheDocument();
    expect(buscarProductosParaVenta).toHaveBeenCalledWith("coca");
  });

  it("muestra 'No se encontraron productos' sin coincidencias", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await user.type(screen.getByLabelText("Producto"), "gaseosa");

    expect(await screen.findByText("No se encontraron productos")).toBeInTheDocument();
  });

  it("elegir una opción completa el ítem sin llamar a buscarProducto", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await agregarItem(user, { quantity: "2" });

    expect(await screen.findByText("Coca-Cola 500ml")).toBeInTheDocument();
    expect(buscarProducto).not.toHaveBeenCalled();
  });

  it("cambiar el texto tras elegir un producto descarta la selección (Agregar deshabilitado)", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await elegirProducto(user);
    await user.type(screen.getByLabelText("Cantidad"), "2");
    expect(screen.getByRole("button", { name: "Agregar" })).toBeEnabled();

    await user.type(screen.getByLabelText("Producto"), " x");

    expect(screen.getByRole("button", { name: "Agregar" })).toBeDisabled();
  });
});

describe("VentaForm — agregar ítems al detalle", () => {
  it("muestra advertencia de cantidad inválida", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await agregarItem(user, { quantity: "0" });

    expect(
      await screen.findByText("El valor debe ser un número positivo")
    ).toBeInTheDocument();
  });

  it("avisa cantidad inválida al perder el foco, antes de presionar Agregar", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await user.type(screen.getByLabelText("Cantidad"), "0");
    await user.click(screen.getByLabelText("Producto"));

    expect(
      await screen.findByText("El valor debe ser un número positivo")
    ).toBeInTheDocument();
    expect(buscarProducto).not.toHaveBeenCalled();
  });

  it("no muestra error al perder el foco de Cantidad vacía", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await user.click(screen.getByLabelText("Cantidad"));
    await user.click(screen.getByLabelText("Producto"));

    expect(
      screen.queryByText("El valor debe ser un número positivo")
    ).not.toBeInTheDocument();
  });

  it("muestra advertencia de stock insuficiente", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await agregarItem(user, { quantity: "50" });

    expect(
      await screen.findByText("No hay stock suficiente para completar la operación")
    ).toBeInTheDocument();
  });

  it("agregar el mismo producto dos veces consolida la línea", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await agregarItem(user, { quantity: "2" });
    await screen.findByText("Coca-Cola 500ml");
    await agregarItem(user, { quantity: "3" });

    expect(await screen.findAllByText("Coca-Cola 500ml")).toHaveLength(1);
    expect(screen.getByText("5")).toBeInTheDocument();
  });
});

describe("VentaForm — total, confirmación y registro", () => {
  it("muestra el total correcto según los ítems agregados", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await agregarItem(user, { quantity: "2" });

    expect(await screen.findByText("701")).toBeInTheDocument();
  });

  it("'Registrar venta' muestra el diálogo de confirmación sin llamar a registrarVenta todavía", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await agregarItem(user, { quantity: "2" });
    await user.click(screen.getByRole("button", { name: "Registrar venta" }));

    expect(await screen.findByRole("button", { name: "Confirmar" })).toBeInTheDocument();
    expect(registrarVenta).not.toHaveBeenCalled();
  });

  it("Confirmar llama a registrarVenta y muestra el mensaje de éxito, reiniciando el formulario", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    registrarVenta.mockResolvedValue({
      success: true,
      message: "Venta registrada exitosamente",
      sale: { id: 1, total: 701, status: "Confirmada" },
    });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await agregarItem(user, { quantity: "2" });
    await user.click(screen.getByRole("button", { name: "Registrar venta" }));
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(registrarVenta).toHaveBeenCalledWith({
      dni: "30111222",
      items: [{ sku: "ABC123", quantity: "2", unit_price: "350.5" }],
    });
    expect(
      await screen.findByText("Venta registrada exitosamente")
    ).toBeInTheDocument();
    expect(screen.queryByLabelText("Producto")).not.toBeInTheDocument();
  });

  it("Cancelar no llama a registrarVenta y conserva el detalle armado", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: ACTIVE_CUSTOMER });
    buscarProductosParaVenta.mockResolvedValue({ products: [ACTIVE_PRODUCT] });
    const user = userEvent.setup();
    render(<VentaForm />);

    await buscarClienteActivo(user);
    await agregarItem(user, { quantity: "2" });
    await user.click(screen.getByRole("button", { name: "Registrar venta" }));
    await user.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(registrarVenta).not.toHaveBeenCalled();
    expect(screen.getByText("Coca-Cola 500ml")).toBeInTheDocument();
  });
});
