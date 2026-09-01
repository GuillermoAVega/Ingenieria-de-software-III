import { describe, expect, it } from "vitest";

import { EDICION_STATE, evaluateEdicionBusqueda } from "../../app/frontend/productoEdicion.js";

describe("evaluateEdicionBusqueda (producto)", () => {
  it("devuelve NOT_FOUND cuando la búsqueda no encuentra al producto", () => {
    const result = evaluateEdicionBusqueda({
      success: false,
      errors: [{ field: "sku", message: "Producto no encontrado" }],
    });

    expect(result.state).toBe(EDICION_STATE.NOT_FOUND);
    expect(result.message).toBe("Producto no encontrado");
  });

  it("devuelve FOUND con los datos del producto encontrado", () => {
    const product = {
      sku: "ABC123",
      name: "Coca-Cola 500ml",
      brand: "Coca-Cola",
      description: "Botella descartable",
      unit_price: 350.5,
      stock: 100,
      status: "Activo",
    };

    const result = evaluateEdicionBusqueda({ success: true, product });

    expect(result.state).toBe(EDICION_STATE.FOUND);
    expect(result.product).toEqual(product);
  });
});
