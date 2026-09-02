import { describe, expect, it } from "vitest";

import { EDICION_STATE, evaluateEdicionBusqueda } from "../../app/frontend/clienteEdicion.js";

describe("evaluateEdicionBusqueda", () => {
  it("devuelve NOT_FOUND cuando la búsqueda no encuentra al cliente", () => {
    const result = evaluateEdicionBusqueda({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });

    expect(result.state).toBe(EDICION_STATE.NOT_FOUND);
    expect(result.message).toBe("Cliente no encontrado");
  });

  it("devuelve FOUND con los datos del cliente encontrado", () => {
    const customer = {
      dni: 30111222,
      first_name: "Juan",
      last_name: "Perez",
      email: "juan@dominio.com",
      phone: "11-4444-5555",
      status: "Activo",
    };

    const result = evaluateEdicionBusqueda({ success: true, customer });

    expect(result.state).toBe(EDICION_STATE.FOUND);
    expect(result.customer).toEqual(customer);
  });

  it("devuelve INACTIVE cuando el cliente encontrado está Inactivo", () => {
    const customer = {
      dni: 30111222,
      first_name: "Juan",
      last_name: "Perez",
      email: "juan@dominio.com",
      phone: "11-4444-5555",
      status: "Inactivo",
    };

    const result = evaluateEdicionBusqueda({ success: true, customer });

    expect(result.state).toBe(EDICION_STATE.INACTIVE);
    expect(result.message).toBe("El cliente está inactivo y no puede modificarse");
    expect(result.customer).toEqual(customer);
  });
});
