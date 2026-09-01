import { describe, expect, it } from "vitest";

import {
  CLIENTE_SALES_STATE,
  EDICION_STATE,
  evaluateClienteSalesParaModificar,
  evaluateEdicionResult,
} from "../../app/frontend/ventaEdicion.js";

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

describe("evaluateClienteSalesParaModificar", () => {
  it("devuelve CLIENT_NOT_FOUND cuando la búsqueda falla", () => {
    const result = evaluateClienteSalesParaModificar({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });

    expect(result.state).toBe(CLIENTE_SALES_STATE.CLIENT_NOT_FOUND);
    expect(result.message).toBe("Cliente no encontrado");
  });

  it("devuelve NO_SALES cuando el cliente no tiene ninguna venta", () => {
    const result = evaluateClienteSalesParaModificar({ success: true, sales: [] });

    expect(result.state).toBe(CLIENTE_SALES_STATE.NO_SALES);
    expect(result.message).toBe("El cliente no tiene ventas registradas");
  });

  it("devuelve SALES_LIST con todas las ventas, conservando su status", () => {
    const sales = [
      { id: 1, sale_date: "2026-01-01T00:00:00", status: "Borrador", total: 100 },
      { id: 2, sale_date: "2026-01-02T00:00:00", status: "Confirmada", total: 200 },
      { id: 3, sale_date: "2026-01-03T00:00:00", status: "Anulada", total: 300 },
    ];

    const result = evaluateClienteSalesParaModificar({ success: true, sales });

    expect(result.state).toBe(CLIENTE_SALES_STATE.SALES_LIST);
    expect(result.sales).toEqual(sales);
  });
});
