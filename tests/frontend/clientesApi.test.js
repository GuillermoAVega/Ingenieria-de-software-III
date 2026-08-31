import { afterEach, describe, expect, it, vi } from "vitest";

import { altaCliente } from "../../app/frontend/api/clientesApi.js";

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
