import { afterEach, describe, expect, it, vi } from "vitest";

import {
  altaProducto,
  buscarProducto,
  buscarProductosParaVenta,
  darDeBajaProducto,
  editarProducto,
  listarProductos,
} from "../../app/frontend/api/productosApi.js";

const VALID_INPUT = {
  sku: "ABC123",
  name: "Coca-Cola 500ml",
  brand: "Coca-Cola",
  description: "Botella descartable",
  unit_price: "350.50",
  stock: "100",
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("altaProducto", () => {
  it("devuelve success y el producto creado ante una respuesta 201", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Producto registrado exitosamente",
        product: { sku: "ABC123", unit_price: 350.5, stock: 100 },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await altaProducto(VALID_INPUT);

    expect(result).toEqual({
      success: true,
      message: "Producto registrado exitosamente",
      product: { sku: "ABC123", unit_price: 350.5, stock: 100 },
    });
    expect(JSON.parse(mockFetch.mock.calls[0][1].body)).toEqual(VALID_INPUT);
  });

  it("devuelve success:false y la lista de errores ante una respuesta 422", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "sku", message: "El código de producto está duplicado" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await altaProducto(VALID_INPUT);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "sku", message: "El código de producto está duplicado" }],
    });
  });
});

describe("buscarProducto", () => {
  it("devuelve success y el producto encontrado ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ product: { sku: "ABC123", status: "Activo" } }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await buscarProducto("ABC123");

    expect(result).toEqual({ success: true, product: { sku: "ABC123", status: "Activo" } });
    expect(mockFetch).toHaveBeenCalledWith("/productos/ABC123");
  });

  it("devuelve success:false y la advertencia ante una respuesta 404", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "sku", message: "Producto no encontrado" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await buscarProducto("ABC123");

    expect(result).toEqual({
      success: false,
      errors: [{ field: "sku", message: "Producto no encontrado" }],
    });
  });
});

describe("darDeBajaProducto", () => {
  it("devuelve success y el mensaje ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Producto dado de baja exitosamente",
        product: { sku: "ABC123", status: "Inactivo" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await darDeBajaProducto("ABC123");

    expect(result).toEqual({
      success: true,
      message: "Producto dado de baja exitosamente",
      product: { sku: "ABC123", status: "Inactivo" },
    });
    expect(mockFetch).toHaveBeenCalledWith("/productos/ABC123/baja", { method: "PATCH" });
  });

  it("devuelve success:false y la advertencia ante una respuesta 404", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "sku", message: "Producto no encontrado" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await darDeBajaProducto("ABC123");

    expect(result).toEqual({
      success: false,
      errors: [{ field: "sku", message: "Producto no encontrado" }],
    });
  });
});

describe("editarProducto", () => {
  const EDICION_INPUT = {
    name: "Coca-Cola 1L",
    brand: "Coca-Cola",
    description: "Botella retornable",
    unit_price: "399.90",
    stock: "80",
  };

  it("devuelve success y el producto actualizado ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Producto modificado exitosamente",
        product: { sku: "ABC123", status: "Activo" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await editarProducto("ABC123", EDICION_INPUT);

    expect(result).toEqual({
      success: true,
      message: "Producto modificado exitosamente",
      product: { sku: "ABC123", status: "Activo" },
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/productos/ABC123/editar",
      expect.objectContaining({ method: "PUT" })
    );
    expect(JSON.parse(mockFetch.mock.calls[0][1].body)).toEqual(EDICION_INPUT);
  });

  it("devuelve success:false y la advertencia ante una respuesta 422", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "unit_price", message: "El valor debe ser un número positivo" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await editarProducto("ABC123", EDICION_INPUT);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "unit_price", message: "El valor debe ser un número positivo" }],
    });
  });
});

describe("listarProductos", () => {
  it("llama a /productos sin parámetros cuando no se pasa q ni page", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        products: [{ sku: "ABC123", status: "Activo" }],
        page: 1,
        has_next: false,
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await listarProductos();

    expect(result).toEqual({
      products: [{ sku: "ABC123", status: "Activo" }],
      page: 1,
      hasNext: false,
    });
    expect(mockFetch).toHaveBeenCalledWith("/productos");
  });

  it("llama a /productos con q y page cuando se pasan", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ products: [], page: 2, has_next: false }),
    });
    vi.stubGlobal("fetch", mockFetch);

    await listarProductos({ q: "coca", page: 2 });

    expect(mockFetch).toHaveBeenCalledWith("/productos?q=coca&page=2");
  });
});

describe("buscarProductosParaVenta", () => {
  it("llama a /productos/buscar-venta con q y devuelve products", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        products: [{ sku: "ABC123", name: "Coca-Cola 500ml", unit_price: 350.5, stock: 100 }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await buscarProductosParaVenta("coca");

    expect(result).toEqual({
      products: [{ sku: "ABC123", name: "Coca-Cola 500ml", unit_price: 350.5, stock: 100 }],
    });
    expect(mockFetch).toHaveBeenCalledWith("/productos/buscar-venta?q=coca");
  });

  it("devuelve products: [] cuando no hay coincidencias", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ products: [] }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await buscarProductosParaVenta("gaseosa");

    expect(result).toEqual({ products: [] });
  });
});
