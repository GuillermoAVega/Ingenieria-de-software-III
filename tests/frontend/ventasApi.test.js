import { afterEach, describe, expect, it, vi } from "vitest";

import {
  anularVenta,
  buscarVenta,
  cerrarVenta,
  listarVentas,
  registrarVenta,
  reemplazarDetalleVenta,
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

describe("reemplazarDetalleVenta", () => {
  const ITEMS = [{ sku: "ABC123", quantity: "3", unit_price: "350.50" }];

  it("devuelve success y la venta actualizada ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Detalle actualizado exitosamente",
        sale: { id: 1, status: "Borrador", total: 1051.5 },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await reemplazarDetalleVenta(1, ITEMS);

    expect(result).toEqual({
      success: true,
      message: "Detalle actualizado exitosamente",
      sale: { id: 1, status: "Borrador", total: 1051.5 },
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/ventas/1/detalle",
      expect.objectContaining({ method: "PUT" })
    );
    expect(JSON.parse(mockFetch.mock.calls[0][1].body)).toEqual({ items: ITEMS });
  });

  it("devuelve success:false y la lista de errores ante una respuesta 422", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "id", message: "La venta ya no admite modificaciones" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await reemplazarDetalleVenta(1, ITEMS);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "id", message: "La venta ya no admite modificaciones" }],
    });
  });

  it("devuelve success:false ante una respuesta 404", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "id", message: "Venta no encontrada" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await reemplazarDetalleVenta(999, ITEMS);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "id", message: "Venta no encontrada" }],
    });
  });
});

describe("cerrarVenta", () => {
  it("devuelve success y el mensaje ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Venta cerrada exitosamente",
        sale: { id: 1, status: "Confirmada" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await cerrarVenta(1);

    expect(result).toEqual({
      success: true,
      message: "Venta cerrada exitosamente",
      sale: { id: 1, status: "Confirmada" },
    });
    expect(mockFetch).toHaveBeenCalledWith("/ventas/1/cerrar", { method: "PATCH" });
  });

  it("devuelve success:false ante una respuesta 422 de stock insuficiente", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [
          { field: "items", message: "No hay stock suficiente para completar la operación" },
        ],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await cerrarVenta(1);

    expect(result).toEqual({
      success: false,
      errors: [
        { field: "items", message: "No hay stock suficiente para completar la operación" },
      ],
    });
  });

  it("devuelve success:false ante una respuesta 404", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "id", message: "Venta no encontrada" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await cerrarVenta(999);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "id", message: "Venta no encontrada" }],
    });
  });
});

describe("listarVentas", () => {
  it("llama a /ventas sin parámetros cuando no se pasa ningún filtro", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        sales: [{ id: 1, total: 701, customer: { dni: 30111222 } }],
        page: 1,
        has_next: false,
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await listarVentas();

    expect(result).toEqual({
      success: true,
      sales: [{ id: 1, total: 701, customer: { dni: 30111222 } }],
      page: 1,
      hasNext: false,
    });
    expect(mockFetch).toHaveBeenCalledWith("/ventas");
  });

  it("llama a /ventas con dni, dateFrom, dateTo y page cuando se pasan", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ sales: [], page: 2, has_next: false }),
    });
    vi.stubGlobal("fetch", mockFetch);

    await listarVentas({ dni: "3011", dateFrom: "2026-01-01", dateTo: "2026-01-31", page: 2 });

    expect(mockFetch).toHaveBeenCalledWith(
      "/ventas?dni=3011&date_from=2026-01-01&date_to=2026-01-31&page=2"
    );
  });

  it("devuelve success:false y la advertencia ante una respuesta 422 de rango inválido", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "date_range", message: "El rango de fechas es inválido" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await listarVentas({ dateFrom: "2026-02-01", dateTo: "2026-01-01" });

    expect(result).toEqual({
      success: false,
      errors: [{ field: "date_range", message: "El rango de fechas es inválido" }],
    });
  });
});
