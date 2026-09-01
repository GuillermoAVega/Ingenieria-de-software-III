import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { altaCliente } from "../../app/frontend/api/clientesApi.js";
import { ClienteForm } from "../../app/frontend/components/ClienteForm.jsx";

vi.mock("../../app/frontend/api/clientesApi.js", () => ({
  altaCliente: vi.fn(),
}));

const VALID_INPUT = {
  dni: "30111222",
  first_name: "Juan",
  last_name: "Perez",
  email: "juan@dominio.com",
  phone: "11-4444-5555",
};

async function fillForm(user, overrides = {}) {
  const values = { ...VALID_INPUT, ...overrides };
  await user.type(screen.getByLabelText("DNI"), values.dni);
  await user.type(screen.getByLabelText("Nombre"), values.first_name);
  await user.type(screen.getByLabelText("Apellido"), values.last_name);
  await user.type(screen.getByLabelText("Email"), values.email);
  await user.type(screen.getByLabelText("Teléfono"), values.phone);
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("ClienteForm", () => {
  it("renderiza los 5 campos de entrada", () => {
    render(<ClienteForm />);

    expect(screen.getByLabelText("DNI")).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre")).toBeInTheDocument();
    expect(screen.getByLabelText("Apellido")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Teléfono")).toBeInTheDocument();
  });

  it("muestra advertencias de campo obligatorio sin llamar a la API si el formulario está vacío", async () => {
    const user = userEvent.setup();
    render(<ClienteForm />);

    await user.click(screen.getByRole("button", { name: "Registrar cliente" }));

    expect(await screen.findAllByText("El campo es obligatorio")).toHaveLength(5);
    expect(altaCliente).not.toHaveBeenCalled();
  });

  it("muestra advertencias de formato del Frontend sin llamar a la API", async () => {
    const user = userEvent.setup();
    render(<ClienteForm />);

    await fillForm(user, { first_name: "Juan123", phone: "11-abcd" });
    await user.click(screen.getByRole("button", { name: "Registrar cliente" }));

    expect(
      await screen.findByText("El campo solo debe contener letras")
    ).toBeInTheDocument();
    expect(
      screen.getByText("El teléfono debe contener solo números y guiones")
    ).toBeInTheDocument();
    expect(altaCliente).not.toHaveBeenCalled();
  });

  it("muestra las advertencias que solo el backend puede detectar (ej. DNI duplicado)", async () => {
    altaCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "El cliente ya se encuentra registrado" }],
    });
    const user = userEvent.setup();
    render(<ClienteForm />);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Registrar cliente" }));

    expect(
      await screen.findByText("El cliente ya se encuentra registrado")
    ).toBeInTheDocument();
    expect(altaCliente).toHaveBeenCalledTimes(1);
  });

  it("un error del backend no desaparece al perder el foco sin haber escrito nada nuevo", async () => {
    altaCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "El cliente ya se encuentra registrado" }],
    });
    const user = userEvent.setup();
    render(<ClienteForm />);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Registrar cliente" }));
    await screen.findByText("El cliente ya se encuentra registrado");

    await user.click(screen.getByLabelText("DNI"));
    await user.click(screen.getByLabelText("Nombre"));

    expect(
      screen.getByText("El cliente ya se encuentra registrado")
    ).toBeInTheDocument();
  });

  it("conserva los valores ingresados tras un intento fallido en el backend", async () => {
    altaCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "El cliente ya se encuentra registrado" }],
    });
    const user = userEvent.setup();
    render(<ClienteForm />);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Registrar cliente" }));

    await screen.findByText("El cliente ya se encuentra registrado");
    expect(screen.getByLabelText("DNI")).toHaveValue(VALID_INPUT.dni);
    expect(screen.getByLabelText("Nombre")).toHaveValue(VALID_INPUT.first_name);
    expect(screen.getByLabelText("Apellido")).toHaveValue(VALID_INPUT.last_name);
    expect(screen.getByLabelText("Email")).toHaveValue(VALID_INPUT.email);
    expect(screen.getByLabelText("Teléfono")).toHaveValue(VALID_INPUT.phone);
  });

  it("avisa el formato inválido de un campo apenas se pierde el foco, sin enviar el formulario", async () => {
    const user = userEvent.setup();
    render(<ClienteForm />);

    await user.type(screen.getByLabelText("DNI"), "123");
    await user.click(screen.getByLabelText("Nombre"));

    expect(
      await screen.findByText("El DNI debe contener solo números (7 u 8 dígitos)")
    ).toBeInTheDocument();
    expect(altaCliente).not.toHaveBeenCalled();
  });

  it("no muestra ningún error al perder el foco de un campo vacío", async () => {
    const user = userEvent.setup();
    render(<ClienteForm />);

    await user.click(screen.getByLabelText("DNI"));
    await user.click(screen.getByLabelText("Nombre"));

    expect(
      screen.queryByText("El DNI debe contener solo números (7 u 8 dígitos)")
    ).not.toBeInTheDocument();
    expect(screen.queryByText("El campo es obligatorio")).not.toBeInTheDocument();
  });

  it("corregir el valor y volver a perder el foco limpia el error de blur", async () => {
    const user = userEvent.setup();
    render(<ClienteForm />);

    const dniInput = screen.getByLabelText("DNI");
    await user.type(dniInput, "123");
    await user.click(screen.getByLabelText("Nombre"));
    await screen.findByText("El DNI debe contener solo números (7 u 8 dígitos)");

    await user.clear(dniInput);
    await user.type(dniInput, "30111222");
    await user.click(screen.getByLabelText("Nombre"));

    expect(
      screen.queryByText("El DNI debe contener solo números (7 u 8 dígitos)")
    ).not.toBeInTheDocument();
  });

  it("muestra el mensaje de éxito y limpia el formulario", async () => {
    altaCliente.mockResolvedValue({
      success: true,
      message: "Cliente registrado exitosamente",
      customer: { ...VALID_INPUT, status: "Activo" },
    });
    const user = userEvent.setup();
    render(<ClienteForm />);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Registrar cliente" }));

    expect(
      await screen.findByText("Cliente registrado exitosamente")
    ).toBeInTheDocument();
    expect(screen.getByLabelText("DNI")).toHaveValue("");
    expect(screen.getByLabelText("Nombre")).toHaveValue("");
    expect(screen.getByLabelText("Apellido")).toHaveValue("");
    expect(screen.getByLabelText("Email")).toHaveValue("");
    expect(screen.getByLabelText("Teléfono")).toHaveValue("");
  });
});
