import { afterEach, describe, expect, it, vi } from "vitest";

import {
  altaCliente,
  buscarCliente,
  darDeBajaCliente,
  editarCliente,
  listarClientes,
} from "../../app/frontend/api/clientesApi.js";

const VALID_INPUT = {
  dni: "30111222",
  first_name: "Juan",
  last_name: "Perez",
  email: "juan@dominio.com",
  phone: "11-4444-5555",
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("altaCliente", () => {
  it("devuelve success y el cliente creado ante una respuesta 201", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Cliente registrado exitosamente",
        customer: { dni: 30111222, status: "Activo" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await altaCliente(VALID_INPUT);

    expect(result).toEqual({
      success: true,
      message: "Cliente registrado exitosamente",
      customer: { dni: 30111222, status: "Activo" },
    });
    expect(JSON.parse(mockFetch.mock.calls[0][1].body)).toEqual(VALID_INPUT);
  });

  it("devuelve success:false y la lista de errores ante una respuesta 422", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "dni", message: "El campo es obligatorio" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await altaCliente(VALID_INPUT);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "dni", message: "El campo es obligatorio" }],
    });
  });
});

describe("buscarCliente", () => {
  it("devuelve success y el cliente encontrado ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ customer: { dni: 30111222, status: "Activo" } }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await buscarCliente("30111222");

    expect(result).toEqual({
      success: true,
      customer: { dni: 30111222, status: "Activo" },
    });
    expect(mockFetch).toHaveBeenCalledWith("/clientes/30111222");
  });

  it("devuelve success:false y la advertencia ante una respuesta 404", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "dni", message: "Cliente no encontrado" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await buscarCliente("30111222");

    expect(result).toEqual({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });
  });
});

describe("darDeBajaCliente", () => {
  it("devuelve success y el mensaje ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Cliente dado de baja exitosamente",
        customer: { dni: 30111222, status: "Inactivo" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await darDeBajaCliente("30111222");

    expect(result).toEqual({
      success: true,
      message: "Cliente dado de baja exitosamente",
      customer: { dni: 30111222, status: "Inactivo" },
    });
    expect(mockFetch).toHaveBeenCalledWith("/clientes/30111222/baja", {
      method: "PATCH",
    });
  });

  it("devuelve success:false y la advertencia ante una respuesta 404", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "dni", message: "Cliente no encontrado" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await darDeBajaCliente("30111222");

    expect(result).toEqual({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });
  });
});

describe("editarCliente", () => {
  it("devuelve success y el cliente actualizado ante una respuesta 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "Cliente modificado exitosamente",
        customer: { dni: 30111222, status: "Activo" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await editarCliente("30111222", VALID_INPUT);

    expect(result).toEqual({
      success: true,
      message: "Cliente modificado exitosamente",
      customer: { dni: 30111222, status: "Activo" },
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/clientes/30111222/editar",
      expect.objectContaining({ method: "PUT" })
    );
    expect(JSON.parse(mockFetch.mock.calls[0][1].body)).toEqual(VALID_INPUT);
  });

  it("devuelve success:false y la advertencia ante una respuesta 422", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        errors: [{ field: "dni", message: "El DNI ya está en uso" }],
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await editarCliente("30111222", VALID_INPUT);

    expect(result).toEqual({
      success: false,
      errors: [{ field: "dni", message: "El DNI ya está en uso" }],
    });
  });
});

describe("listarClientes", () => {
  it("llama a /clientes sin parámetros cuando no se pasa q ni page", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        customers: [{ dni: 30111222, status: "Activo" }],
        page: 1,
        has_next: false,
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await listarClientes();

    expect(result).toEqual({
      customers: [{ dni: 30111222, status: "Activo" }],
      page: 1,
      hasNext: false,
    });
    expect(mockFetch).toHaveBeenCalledWith("/clientes");
  });

  it("llama a /clientes con q y page cuando se pasan", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ customers: [], page: 2, has_next: false }),
    });
    vi.stubGlobal("fetch", mockFetch);

    await listarClientes({ q: "perez", page: 2 });

    expect(mockFetch).toHaveBeenCalledWith("/clientes?q=perez&page=2");
  });
});
