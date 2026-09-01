import { describe, expect, it } from "vitest";

import {
  DETALLE_STATE,
  evaluateDetalleVenta,
} from "../../app/frontend/ventaListado.js";

describe("evaluateDetalleVenta", () => {
  it("devuelve FOUND con la venta cuando la búsqueda es exitosa", () => {
    const sale = { id: 1, status: "Confirmada", items: [], total: 0 };

    const result = evaluateDetalleVenta({ success: true, sale });

    expect(result.state).toBe(DETALLE_STATE.FOUND);
    expect(result.sale).toBe(sale);
  });

  it("devuelve NOT_FOUND con el mensaje cuando la búsqueda falla", () => {
    const result = evaluateDetalleVenta({
      success: false,
      errors: [{ field: "id", message: "Venta no encontrada" }],
    });

    expect(result.state).toBe(DETALLE_STATE.NOT_FOUND);
    expect(result.message).toBe("Venta no encontrada");
  });
});
