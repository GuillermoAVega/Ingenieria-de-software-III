import { describe, expect, it } from "vitest";

import {
  ANULACION_STATE,
  evaluateClienteSalesParaAnular,
} from "../../app/frontend/ventaAnulacion.js";

describe("evaluateClienteSalesParaAnular", () => {
  it("devuelve CLIENT_NOT_FOUND cuando la búsqueda falla", () => {
    const result = evaluateClienteSalesParaAnular({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });

    expect(result.state).toBe(ANULACION_STATE.CLIENT_NOT_FOUND);
    expect(result.message).toBe("Cliente no encontrado");
  });

  it("devuelve NO_CONFIRMED_SALES cuando el cliente no tiene ventas", () => {
    const result = evaluateClienteSalesParaAnular({ success: true, sales: [] });

    expect(result.state).toBe(ANULACION_STATE.NO_CONFIRMED_SALES);
    expect(result.message).toBe("El cliente no tiene ventas confirmadas para anular");
  });

  it("devuelve NO_CONFIRMED_SALES cuando el cliente solo tiene ventas en otros estados", () => {
    const sales = [
      { id: 1, sale_date: "2026-01-01T00:00:00", status: "Borrador", total: 100 },
      { id: 2, sale_date: "2026-01-02T00:00:00", status: "Anulada", total: 200 },
    ];

    const result = evaluateClienteSalesParaAnular({ success: true, sales });

    expect(result.state).toBe(ANULACION_STATE.NO_CONFIRMED_SALES);
  });

  it("devuelve SALES_LIST solo con las ventas Confirmada", () => {
    const sales = [
      { id: 1, sale_date: "2026-01-01T00:00:00", status: "Borrador", total: 100 },
      { id: 2, sale_date: "2026-01-02T00:00:00", status: "Confirmada", total: 200 },
      { id: 3, sale_date: "2026-01-03T00:00:00", status: "Confirmada", total: 300 },
      { id: 4, sale_date: "2026-01-04T00:00:00", status: "Anulada", total: 400 },
    ];

    const result = evaluateClienteSalesParaAnular({ success: true, sales });

    expect(result.state).toBe(ANULACION_STATE.SALES_LIST);
    expect(result.sales.map((sale) => sale.id)).toEqual([2, 3]);
  });
});
