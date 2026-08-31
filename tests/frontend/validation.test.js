import { describe, expect, it } from "vitest";

import { validateClienteForm } from "../../app/frontend/validation.js";

const VALID_VALUES = {
  dni: "30111222",
  first_name: "Juan",
  last_name: "Perez",
  email: "juan@dominio.com",
  phone: "11-4444-5555",
};

describe("validateClienteForm", () => {
  it("no devuelve errores para un formulario completo y válido", () => {
    expect(validateClienteForm(VALID_VALUES)).toEqual({});
  });

  it("marca los 5 campos como obligatorios cuando están vacíos", () => {
    const errors = validateClienteForm({
      dni: "",
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
    });

    expect(Object.keys(errors).sort()).toEqual(
      ["dni", "email", "first_name", "last_name", "phone"].sort()
    );
    expect(errors.dni).toBe("El campo es obligatorio");
  });

  it("trata un campo con solo espacios como obligatorio", () => {
    const errors = validateClienteForm({ ...VALID_VALUES, first_name: "   " });

    expect(errors.first_name).toBe("El campo es obligatorio");
  });

  it("valida el formato de nombre y apellido", () => {
    const errors = validateClienteForm({ ...VALID_VALUES, first_name: "Juan123" });

    expect(errors.first_name).toBe("El campo solo debe contener letras");
  });

  it("valida el formato de email exigiendo un TLD", () => {
    const errors = validateClienteForm({ ...VALID_VALUES, email: "juan@dominio" });

    expect(errors.email).toBe("El email es inválido");
  });

  it("acepta un email con TLD como válido", () => {
    const errors = validateClienteForm({ ...VALID_VALUES, email: "juan@dominio.com" });

    expect(errors.email).toBeUndefined();
  });

  it("valida el formato de teléfono", () => {
    const errors = validateClienteForm({ ...VALID_VALUES, phone: "11-abcd" });

    expect(errors.phone).toBe("El formato del teléfono es incorrecto");
  });

  it("valida el formato de DNI", () => {
    const errors = validateClienteForm({ ...VALID_VALUES, dni: "301112" });

    expect(errors.dni).toBe("El formato del DNI es inválido");
  });

  it("reporta múltiples errores de formato en un mismo intento", () => {
    const errors = validateClienteForm({
      ...VALID_VALUES,
      first_name: "Juan123",
      phone: "11-abcd",
    });

    expect(Object.keys(errors).sort()).toEqual(["first_name", "phone"]);
  });
});
