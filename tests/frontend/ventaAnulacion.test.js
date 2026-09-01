import { describe, expect, it } from "vitest";

import { ANULACION_STATE, evaluateAnulacionResult } from "../../app/frontend/ventaAnulacion.js";

describe("evaluateAnulacionResult", () => {
  it("devuelve NOT_FOUND cuando la búsqueda no encuentra la venta", () => {
    const result = evaluateAnulacionResult({
      success: false,
      errors: [{ field: "id", message: "Venta no encontrada" }],
    });

    expect(result.state).toBe(ANULACION_STATE.NOT_FOUND);
    expect(result.message).toBe("Venta no encontrada");
  });

  it("devuelve REQUIRES_CONFIRMATION cuando la venta está Confirmada", () => {
    const sale = { id: 1, status: "Confirmada" };

    const result = evaluateAnulacionResult({ success: true, sale });

    expect(result.state).toBe(ANULACION_STATE.REQUIRES_CONFIRMATION);
    expect(result.sale).toEqual(sale);
  });

  it("devuelve ALREADY_CANCELLED cuando la venta ya está Anulada", () => {
    const sale = { id: 1, status: "Anulada" };

    const result = evaluateAnulacionResult({ success: true, sale });

    expect(result.state).toBe(ANULACION_STATE.ALREADY_CANCELLED);
    expect(result.message).toBe("La venta ya se encuentra anulada");
  });
});
