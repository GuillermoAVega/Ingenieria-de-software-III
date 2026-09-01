import { describe, expect, it } from "vitest";

import { EDICION_STATE, evaluateEdicionResult } from "../../app/frontend/ventaEdicion.js";

describe("evaluateEdicionResult", () => {
  it("devuelve NOT_FOUND cuando la búsqueda falla", () => {
    const result = evaluateEdicionResult({
      success: false,
      errors: [{ field: "id", message: "Venta no encontrada" }],
    });

    expect(result.state).toBe(EDICION_STATE.NOT_FOUND);
    expect(result.message).toBe("Venta no encontrada");
  });

  it("devuelve NOT_DRAFT cuando la venta está Confirmada", () => {
    const sale = { id: 1, status: "Confirmada" };

    const result = evaluateEdicionResult({ success: true, sale });

    expect(result.state).toBe(EDICION_STATE.NOT_DRAFT);
    expect(result.message).toBe("La venta ya no admite modificaciones");
    expect(result.sale).toBe(sale);
  });

  it("devuelve NOT_DRAFT cuando la venta está Anulada", () => {
    const sale = { id: 1, status: "Anulada" };

    const result = evaluateEdicionResult({ success: true, sale });

    expect(result.state).toBe(EDICION_STATE.NOT_DRAFT);
  });

  it("devuelve EDITABLE cuando la venta está en Borrador", () => {
    const sale = { id: 1, status: "Borrador" };

    const result = evaluateEdicionResult({ success: true, sale });

    expect(result.state).toBe(EDICION_STATE.EDITABLE);
    expect(result.sale).toBe(sale);
  });
});
