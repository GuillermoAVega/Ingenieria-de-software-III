import { describe, expect, it } from "vitest";

import { BAJA_STATE, evaluateBajaResult } from "../../app/frontend/bajaCliente.js";

describe("evaluateBajaResult", () => {
  it("devuelve NOT_FOUND cuando la búsqueda no encuentra al cliente", () => {
    const result = evaluateBajaResult({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });

    expect(result.state).toBe(BAJA_STATE.NOT_FOUND);
    expect(result.message).toBe("Cliente no encontrado");
  });

  it("devuelve REQUIRES_CONFIRMATION cuando el cliente encontrado está Activo", () => {
    const customer = { dni: 30111222, status: "Activo" };

    const result = evaluateBajaResult({ success: true, customer });

    expect(result.state).toBe(BAJA_STATE.REQUIRES_CONFIRMATION);
    expect(result.customer).toEqual(customer);
  });

  it("devuelve ALREADY_INACTIVE cuando el cliente encontrado ya está Inactivo", () => {
    const customer = { dni: 30111222, status: "Inactivo" };

    const result = evaluateBajaResult({ success: true, customer });

    expect(result.state).toBe(BAJA_STATE.ALREADY_INACTIVE);
    expect(result.message).toBe("El cliente ya se encuentra dado de baja");
  });
});
