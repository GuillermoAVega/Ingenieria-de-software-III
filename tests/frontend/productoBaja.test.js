import { describe, expect, it } from "vitest";

import { BAJA_STATE, evaluateBajaResult } from "../../app/frontend/productoBaja.js";

describe("evaluateBajaResult (producto)", () => {
  it("devuelve NOT_FOUND cuando la búsqueda no encuentra al producto", () => {
    const result = evaluateBajaResult({
      success: false,
      errors: [{ field: "sku", message: "Producto no encontrado" }],
    });

    expect(result.state).toBe(BAJA_STATE.NOT_FOUND);
    expect(result.message).toBe("Producto no encontrado");
  });

  it("devuelve REQUIRES_CONFIRMATION cuando el producto encontrado está Activo", () => {
    const product = { sku: "ABC123", status: "Activo" };

    const result = evaluateBajaResult({ success: true, product });

    expect(result.state).toBe(BAJA_STATE.REQUIRES_CONFIRMATION);
    expect(result.product).toEqual(product);
  });

  it("devuelve ALREADY_INACTIVE cuando el producto encontrado ya está Inactivo", () => {
    const product = { sku: "ABC123", status: "Inactivo" };

    const result = evaluateBajaResult({ success: true, product });

    expect(result.state).toBe(BAJA_STATE.ALREADY_INACTIVE);
    expect(result.message).toBe("El producto ya se encuentra dado de baja");
  });
});
