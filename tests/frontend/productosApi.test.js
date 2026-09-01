import { afterEach, describe, expect, it, vi } from "vitest";

import { altaProducto } from "../../app/frontend/api/productosApi.js";

const VALID_INPUT = {
  sku: "ABC123",
  name: "Coca-Cola 500ml",
  brand: "Coca-Cola",
  description: "Botella descartable",
  unit_price: "350.50",
  stock: "100",
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("altaProducto", () => {
  it("devuelve success y el producto creado ante una respuesta 201", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Producto registrado exitosamente",
        product: { sku: "ABC123", unit_price: 350.5, stock: 100 },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await altaProducto(VALID_INPUT);

    expect(result).toEqual({
      success: true,
      message: "Producto registrado exitosamente",
      product: { sku: "ABC123", unit_price: 350.5, stock: 100 },
    });
    expect(JSON.parse(mockFetch.mock.calls[0][1].body)).toEqual(VALID_INPUT);
  });

  it("devuelve success:false y la lista de errores ante una respuesta 422", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "sku", message: "El código de producto está duplicado" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await altaProducto(VALID_INPUT);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "sku", message: "El código de producto está duplicado" }],
    });
  });
});
