import { describe, expect, it } from "vitest";

import { validateProductoForm } from "../../app/frontend/validationProducto.js";

const VALID_VALUES = {
  sku: "ABC123",
  name: "Coca-Cola 500ml",
  brand: "Coca-Cola",
  description: "Botella descartable",
  unit_price: "350.50",
  stock: "100",
};

describe("validateProductoForm", () => {
  it("no devuelve errores para un formulario completo y válido", () => {
    expect(validateProductoForm(VALID_VALUES)).toEqual({});
  });

  it("no exige la descripción", () => {
    const errors = validateProductoForm({ ...VALID_VALUES, description: "" });

    expect(errors.description).toBeUndefined();
  });

  it("marca los 5 campos obligatorios cuando están vacíos", () => {
    const errors = validateProductoForm({
      sku: "",
      name: "",
      brand: "",
      description: "",
      unit_price: "",
      stock: "",
    });

    expect(Object.keys(errors).sort()).toEqual(
      ["brand", "name", "sku", "stock", "unit_price"].sort()
    );
    expect(errors.sku).toBe("El campo es obligatorio");
  });

  it("valida que unit_price sea un número positivo", () => {
    const errors = validateProductoForm({ ...VALID_VALUES, unit_price: "-5" });

    expect(errors.unit_price).toBe("El valor debe ser un número positivo");
  });

  it("valida que stock sea un entero positivo", () => {
    const errors = validateProductoForm({ ...VALID_VALUES, stock: "5.5" });

    expect(errors.stock).toBe("El valor debe ser un número positivo");
  });

  it("reporta múltiples errores en un mismo intento", () => {
    const errors = validateProductoForm({
      ...VALID_VALUES,
      unit_price: "abc",
      stock: "0",
    });

    expect(Object.keys(errors).sort()).toEqual(["stock", "unit_price"]);
  });
});
