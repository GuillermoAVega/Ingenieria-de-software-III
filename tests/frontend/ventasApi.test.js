import { afterEach, describe, expect, it, vi } from "vitest";

import { registrarVenta } from "../../app/frontend/api/ventasApi.js";

const VALID_INPUT = {
  dni: "30111222",
  items: [{ sku: "ABC123", quantity: "2", unit_price: "350.50" }],
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("registrarVenta", () => {
  it("devuelve success y la venta creada ante una respuesta 201", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Venta registrada exitosamente",
        sale: { id: 1, total: 701.0, status: "Confirmada" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await registrarVenta(VALID_INPUT);

    expect(result).toEqual({
      success: true,
      message: "Venta registrada exitosamente",
      sale: { id: 1, total: 701.0, status: "Confirmada" },
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/ventas",
      expect.objectContaining({ method: "POST" })
    );
    expect(JSON.parse(mockFetch.mock.calls[0][1].body)).toEqual(VALID_INPUT);
  });

  it("devuelve success:false y la lista de errores ante una respuesta 422", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "dni", message: "Cliente no encontrado" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await registrarVenta(VALID_INPUT);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });
  });
});
