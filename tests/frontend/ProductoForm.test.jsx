import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { altaProducto } from "../../app/frontend/api/productosApi.js";
import { ProductoForm } from "../../app/frontend/components/ProductoForm.jsx";

vi.mock("../../app/frontend/api/productosApi.js", () => ({
  altaProducto: vi.fn(),
}));

const VALID_INPUT = {
  sku: "ABC123",
  name: "Coca-Cola 500ml",
  brand: "Coca-Cola",
  description: "Botella descartable",
  unit_price: "350.50",
  stock: "100",
};

async function fillForm(user, overrides = {}) {
  const values = { ...VALID_INPUT, ...overrides };
  await user.type(screen.getByLabelText("Código/SKU"), values.sku);
  await user.type(screen.getByLabelText("Nombre"), values.name);
  await user.type(screen.getByLabelText("Marca"), values.brand);
  if (values.description) {
    await user.type(screen.getByLabelText("Descripción (opcional)"), values.description);
  }
  await user.type(screen.getByLabelText("Precio unitario"), values.unit_price);
  await user.type(screen.getByLabelText("Stock inicial"), values.stock);
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("ProductoForm", () => {
  it("renderiza los 6 campos de entrada", () => {
    render(<ProductoForm />);

    expect(screen.getByLabelText("Código/SKU")).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre")).toBeInTheDocument();
    expect(screen.getByLabelText("Marca")).toBeInTheDocument();
    expect(screen.getByLabelText("Descripción (opcional)")).toBeInTheDocument();
    expect(screen.getByLabelText("Precio unitario")).toBeInTheDocument();
    expect(screen.getByLabelText("Stock inicial")).toBeInTheDocument();
  });

  it("muestra advertencias de campo obligatorio sin llamar a la API si el formulario está vacío", async () => {
    const user = userEvent.setup();
    render(<ProductoForm />);

    await user.click(screen.getByRole("button", { name: "Registrar producto" }));

    expect(await screen.findAllByText("El campo es obligatorio")).toHaveLength(5);
    expect(altaProducto).not.toHaveBeenCalled();
  });

  it("muestra el mensaje de éxito y limpia el formulario", async () => {
    altaProducto.mockResolvedValue({
      success: true,
      message: "Producto registrado exitosamente",
      product: { ...VALID_INPUT },
    });
    const user = userEvent.setup();
    render(<ProductoForm />);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Registrar producto" }));

    expect(
      await screen.findByText("Producto registrado exitosamente")
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Código/SKU")).toHaveValue("");
    expect(screen.getByLabelText("Nombre")).toHaveValue("");
  });

  it("avisa el formato inválido de un campo apenas se pierde el foco, sin enviar el formulario", async () => {
    const user = userEvent.setup();
    render(<ProductoForm />);

    await user.type(screen.getByLabelText("Precio unitario"), "abc");
    await user.click(screen.getByLabelText("Stock inicial"));

    expect(
      await screen.findByText("El valor debe ser un número positivo")
    ).toBeInTheDocument();
    expect(altaProducto).not.toHaveBeenCalled();
  });

  it("no muestra error al perder el foco de un campo vacío", async () => {
    const user = userEvent.setup();
    render(<ProductoForm />);

    await user.click(screen.getByLabelText("Precio unitario"));
    await user.click(screen.getByLabelText("Stock inicial"));

    expect(
      screen.queryByText("El valor debe ser un número positivo")
    ).not.toBeInTheDocument();
  });

  it("corregir el valor y volver a perder el foco limpia el error de blur", async () => {
    const user = userEvent.setup();
    render(<ProductoForm />);

    const precioInput = screen.getByLabelText("Precio unitario");
    await user.type(precioInput, "abc");
    await user.click(screen.getByLabelText("Stock inicial"));
    await screen.findByText("El valor debe ser un número positivo");

    await user.clear(precioInput);
    await user.type(precioInput, "350.50");
    await user.click(screen.getByLabelText("Stock inicial"));

    expect(
      screen.queryByText("El valor debe ser un número positivo")
    ).not.toBeInTheDocument();
  });

  it("muestra la advertencia del backend (SKU duplicado) y conserva los valores ingresados", async () => {
    altaProducto.mockResolvedValue({
      success: false,
      errors: [{ field: "sku", message: "El código de producto está duplicado" }],
    });
    const user = userEvent.setup();
    render(<ProductoForm />);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Registrar producto" }));

    expect(
      await screen.findByText("El código de producto está duplicado")
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Código/SKU")).toHaveValue(VALID_INPUT.sku);
    expect(screen.getByLabelText("Nombre")).toHaveValue(VALID_INPUT.name);
  });

  it("un error del backend no desaparece al perder el foco sin haber escrito nada nuevo", async () => {
    altaProducto.mockResolvedValue({
      success: false,
      errors: [{ field: "sku", message: "El código de producto está duplicado" }],
    });
    const user = userEvent.setup();
    render(<ProductoForm />);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Registrar producto" }));
    await screen.findByText("El código de producto está duplicado");

    await user.click(screen.getByLabelText("Código/SKU"));
    await user.click(screen.getByLabelText("Nombre"));

    expect(
      screen.getByText("El código de producto está duplicado")
    ).toBeInTheDocument();
  });
});
