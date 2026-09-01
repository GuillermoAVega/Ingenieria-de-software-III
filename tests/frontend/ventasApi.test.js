import { afterEach, describe, expect, it, vi } from "vitest";

import {
  anularVenta,
  buscarVenta,
  registrarVenta,
} from "../../app/frontend/api/ventasApi.js";

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

describe("buscarVenta", () => {
  it("devuelve success y la venta encontrada ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ sale: { id: 1, status: "Confirmada" } }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await buscarVenta(1);

    expect(result).toEqual({ success: true, sale: { id: 1, status: "Confirmada" } });
    expect(mockFetch).toHaveBeenCalledWith("/ventas/1");
  });

  it("devuelve success:false y la advertencia ante una respuesta 404", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "id", message: "Venta no encontrada" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await buscarVenta(999);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "id", message: "Venta no encontrada" }],
    });
  });
});

describe("anularVenta", () => {
  it("devuelve success y el mensaje ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Venta anulada exitosamente",
        sale: { id: 1, status: "Anulada" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await anularVenta(1);

    expect(result).toEqual({
      success: true,
      message: "Venta anulada exitosamente",
      sale: { id: 1, status: "Anulada" },
    });
    expect(mockFetch).toHaveBeenCalledWith("/ventas/1/anular", { method: "PATCH" });
  });

  it("devuelve success:false y la advertencia ante una respuesta 422", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "id", message: "La venta ya se encuentra anulada" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await anularVenta(1);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "id", message: "La venta ya se encuentra anulada" }],
    });
  });
});
