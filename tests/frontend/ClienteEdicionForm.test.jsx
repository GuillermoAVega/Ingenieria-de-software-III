import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { buscarCliente, editarCliente } from "../../app/frontend/api/clientesApi.js";
import { ClienteEdicionForm } from "../../app/frontend/components/ClienteEdicionForm.jsx";

vi.mock("../../app/frontend/api/clientesApi.js", () => ({
  buscarCliente: vi.fn(),
  editarCliente: vi.fn(),
}));

const EXISTING_CUSTOMER = {
  dni: 30111222,
  first_name: "Juan",
  last_name: "Perez",
  email: "juan@dominio.com",
  phone: "11-4444-5555",
  status: "Activo",
};

afterEach(() => {
  vi.clearAllMocks();
});

async function buscar(user, dni = "30111222") {
  await user.type(screen.getByLabelText("DNI", { selector: "#edicion-search-dni" }), dni);
  await user.click(screen.getByRole("button", { name: "Buscar cliente" }));
}

describe("ClienteEdicionForm", () => {
  it("muestra 'cliente no encontrado' y no renderiza el formulario de edición", async () => {
    buscarCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);

    expect(await screen.findByText("Cliente no encontrado")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Guardar cambios" })).not.toBeInTheDocument();
  });

  it("muestra el formulario pre-cargado con los datos del cliente encontrado", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: EXISTING_CUSTOMER });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);

    expect(await screen.findByRole("button", { name: "Guardar cambios" })).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre")).toHaveValue("Juan");
    expect(screen.getByLabelText("Apellido")).toHaveValue("Perez");
    expect(screen.getByLabelText("Email")).toHaveValue("juan@dominio.com");
    expect(screen.getByLabelText("Teléfono")).toHaveValue("11-4444-5555");
  });

  it("muestra advertencias de formato inválido de inmediato, sin confirmar ni llamar a editarCliente", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: EXISTING_CUSTOMER });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);
    const nombreInput = await screen.findByLabelText("Nombre");
    await user.clear(nombreInput);
    await user.type(nombreInput, "Juan123");
    await user.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("El campo solo debe contener letras")
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
    expect(editarCliente).not.toHaveBeenCalled();
  });

  it("avisa el formato inválido de un campo apenas se pierde el foco, sin confirmar", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: EXISTING_CUSTOMER });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);
    const dniInput = await screen.findByLabelText("DNI", { selector: "#edicion-dni" });
    await user.clear(dniInput);
    await user.type(dniInput, "123");
    await user.click(screen.getByLabelText("Nombre"));

    expect(
      await screen.findByText("El DNI debe contener solo números (7 u 8 dígitos)")
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
    expect(editarCliente).not.toHaveBeenCalled();
  });

  it("no muestra error al perder el foco de un campo vacío", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: EXISTING_CUSTOMER });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);
    const dniInput = await screen.findByLabelText("DNI", { selector: "#edicion-dni" });
    await user.clear(dniInput);
    await user.click(screen.getByLabelText("Nombre"));

    expect(
      screen.queryByText("El DNI debe contener solo números (7 u 8 dígitos)")
    ).not.toBeInTheDocument();
  });

  it("corregir el valor y volver a perder el foco limpia el error de blur", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: EXISTING_CUSTOMER });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);
    const dniInput = await screen.findByLabelText("DNI", { selector: "#edicion-dni" });
    await user.clear(dniInput);
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

  it("guarda directamente al presionar 'Guardar cambios', sin ningún modal de confirmación", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: EXISTING_CUSTOMER });
    editarCliente.mockResolvedValue({
      success: true,
      message: "Cliente modificado exitosamente",
      customer: { ...EXISTING_CUSTOMER, first_name: "Juan Ignacio" },
    });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Guardar cambios" }));

    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
    expect(editarCliente).toHaveBeenCalledWith("30111222", expect.any(Object));
    expect(
      await screen.findByText("Cliente modificado exitosamente")
    ).toBeInTheDocument();
  });

  it("si el backend rechaza por DNI duplicado, muestra la advertencia y conserva los valores", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: EXISTING_CUSTOMER });
    editarCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "El DNI ya está en uso" }],
    });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Guardar cambios" }));

    expect(await screen.findByText("El DNI ya está en uso")).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre")).toHaveValue("Juan");
  });

  it("un error del backend no desaparece al perder el foco sin haber escrito nada nuevo", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: EXISTING_CUSTOMER });
    editarCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "El DNI ya está en uso" }],
    });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Guardar cambios" }));
    await screen.findByText("El DNI ya está en uso");

    await user.click(screen.getByLabelText("DNI", { selector: "#edicion-dni" }));
    await user.click(screen.getByLabelText("Nombre"));

    expect(screen.getByText("El DNI ya está en uso")).toBeInTheDocument();
  });

  it("con un campo inválido, 'Guardar cambios' muestra los errores y no llama a editarCliente", async () => {
    buscarCliente.mockResolvedValue({ success: true, customer: EXISTING_CUSTOMER });
    const user = userEvent.setup();
    render(<ClienteEdicionForm />);

    await buscar(user);
    const nombreInput = await screen.findByLabelText("Nombre");
    await user.clear(nombreInput);
    await user.type(nombreInput, "Juan123");
    await user.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("El campo solo debe contener letras")
    ).toBeInTheDocument();
    expect(editarCliente).not.toHaveBeenCalled();
  });
});
