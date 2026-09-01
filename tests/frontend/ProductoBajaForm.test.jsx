import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { buscarProducto, darDeBajaProducto } from "../../app/frontend/api/productosApi.js";
import { ProductoBajaForm } from "../../app/frontend/components/ProductoBajaForm.jsx";

vi.mock("../../app/frontend/api/productosApi.js", () => ({
  buscarProducto: vi.fn(),
  darDeBajaProducto: vi.fn(),
}));

afterEach(() => {
  vi.clearAllMocks();
});

async function buscar(user, sku = "ABC123") {
  await user.type(screen.getByLabelText("SKU"), sku);
  await user.click(screen.getByRole("button", { name: "Buscar producto" }));
}

describe("ProductoBajaForm", () => {
  it("muestra 'producto no encontrado' y no renderiza botones de confirmación", async () => {
    buscarProducto.mockResolvedValue({
      success: false,
      errors: [{ field: "sku", message: "Producto no encontrado" }],
    });
    const user = userEvent.setup();
    render(<ProductoBajaForm />);

    await buscar(user);

    expect(await screen.findByText("Producto no encontrado")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
  });

  it("muestra 'ya dado de baja' y no llama a darDeBajaProducto para un producto Inactivo", async () => {
    buscarProducto.mockResolvedValue({
      success: true,
      product: { sku: "ABC123", name: "Coca-Cola 500ml", status: "Inactivo" },
    });
    const user = userEvent.setup();
    render(<ProductoBajaForm />);

    await buscar(user);

    expect(
      await screen.findByText("El producto ya se encuentra dado de baja")
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
    expect(darDeBajaProducto).not.toHaveBeenCalled();
  });

  it("muestra los datos del producto y los botones Confirmar/Cancelar para un producto Activo", async () => {
    buscarProducto.mockResolvedValue({
      success: true,
      product: { sku: "ABC123", name: "Coca-Cola 500ml", status: "Activo" },
    });
    const user = userEvent.setup();
    render(<ProductoBajaForm />);

    await buscar(user);

    expect(await screen.findByText("Coca-Cola 500ml — SKU ABC123")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Confirmar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cancelar" })).toBeInTheDocument();
  });

  it("al confirmar, llama a darDeBajaProducto y muestra el mensaje de éxito", async () => {
    buscarProducto.mockResolvedValue({
      success: true,
      product: { sku: "ABC123", name: "Coca-Cola 500ml", status: "Activo" },
    });
    darDeBajaProducto.mockResolvedValue({
      success: true,
      message: "Producto dado de baja exitosamente",
      product: { sku: "ABC123", status: "Inactivo" },
    });
    const user = userEvent.setup();
    render(<ProductoBajaForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(darDeBajaProducto).toHaveBeenCalledWith("ABC123");
    expect(
      await screen.findByText("Producto dado de baja exitosamente")
    ).toBeInTheDocument();
  });

  it("al cancelar, no llama a darDeBajaProducto y oculta la confirmación", async () => {
    buscarProducto.mockResolvedValue({
      success: true,
      product: { sku: "ABC123", name: "Coca-Cola 500ml", status: "Activo" },
    });
    const user = userEvent.setup();
    render(<ProductoBajaForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(darDeBajaProducto).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
  });
});
