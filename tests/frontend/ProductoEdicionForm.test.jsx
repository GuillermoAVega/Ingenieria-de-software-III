import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { buscarProducto, editarProducto } from "../../app/frontend/api/productosApi.js";
import { ProductoEdicionForm } from "../../app/frontend/components/ProductoEdicionForm.jsx";

vi.mock("../../app/frontend/api/productosApi.js", () => ({
  buscarProducto: vi.fn(),
  editarProducto: vi.fn(),
}));

const EXISTING_PRODUCT = {
  sku: "ABC123",
  name: "Coca-Cola 500ml",
  brand: "Coca-Cola",
  description: "Botella descartable",
  unit_price: 350.5,
  stock: 100,
  status: "Activo",
};

afterEach(() => {
  vi.clearAllMocks();
});

async function buscar(user, sku = "ABC123") {
  await user.type(screen.getByLabelText("SKU", { selector: "#edicion-search-sku" }), sku);
  await user.click(screen.getByRole("button", { name: "Buscar producto" }));
}

describe("ProductoEdicionForm", () => {
  it("muestra 'producto no encontrado' y no renderiza el formulario de edición", async () => {
    buscarProducto.mockResolvedValue({
      success: false,
      errors: [{ field: "sku", message: "Producto no encontrado" }],
    });
    const user = userEvent.setup();
    render(<ProductoEdicionForm />);

    await buscar(user);

    expect(await screen.findByText("Producto no encontrado")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Guardar cambios" })).not.toBeInTheDocument();
  });

  it("muestra el formulario pre-cargado con el SKU como texto de solo lectura", async () => {
    buscarProducto.mockResolvedValue({ success: true, product: EXISTING_PRODUCT });
    const user = userEvent.setup();
    render(<ProductoEdicionForm />);

    await buscar(user);

    expect(await screen.findByRole("button", { name: "Guardar cambios" })).toBeInTheDocument();
    expect(screen.getByText("ABC123")).toBeInTheDocument();
    expect(screen.queryByLabelText("Código/SKU")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Nombre")).toHaveValue("Coca-Cola 500ml");
    expect(screen.getByLabelText("Stock inicial")).toHaveValue("100");
  });

  it("muestra advertencias de inmediato ante un campo inválido, sin llamar a editarProducto", async () => {
    buscarProducto.mockResolvedValue({ success: true, product: EXISTING_PRODUCT });
    const user = userEvent.setup();
    render(<ProductoEdicionForm />);

    await buscar(user);
    const precioInput = await screen.findByLabelText("Precio unitario");
    await user.clear(precioInput);
    await user.type(precioInput, "-5");
    await user.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("El valor debe ser un número positivo")
    ).toBeInTheDocument();
    expect(editarProducto).not.toHaveBeenCalled();
  });

  it("al enviar datos válidos, guarda directo, muestra éxito y vuelve al estado de búsqueda", async () => {
    buscarProducto.mockResolvedValue({ success: true, product: EXISTING_PRODUCT });
    editarProducto.mockResolvedValue({
      success: true,
      message: "Producto modificado exitosamente",
      product: { ...EXISTING_PRODUCT, name: "Coca-Cola 1L" },
    });
    const user = userEvent.setup();
    render(<ProductoEdicionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Guardar cambios" }));

    expect(editarProducto).toHaveBeenCalledWith("ABC123", expect.any(Object));
    expect(
      await screen.findByText("Producto modificado exitosamente")
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Guardar cambios" })).not.toBeInTheDocument();
  });
});
