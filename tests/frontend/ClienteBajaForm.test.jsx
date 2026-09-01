import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { buscarCliente, darDeBajaCliente } from "../../app/frontend/api/clientesApi.js";
import { ClienteBajaForm } from "../../app/frontend/components/ClienteBajaForm.jsx";

vi.mock("../../app/frontend/api/clientesApi.js", () => ({
  buscarCliente: vi.fn(),
  darDeBajaCliente: vi.fn(),
}));

afterEach(() => {
  vi.clearAllMocks();
});

async function buscar(user, dni = "30111222") {
  await user.type(screen.getByLabelText("DNI"), dni);
  await user.click(screen.getByRole("button", { name: "Buscar cliente" }));
}

describe("ClienteBajaForm", () => {
  it("muestra 'cliente no encontrado' y no renderiza botones de confirmación", async () => {
    buscarCliente.mockResolvedValue({
      success: false,
      errors: [{ field: "dni", message: "Cliente no encontrado" }],
    });
    const user = userEvent.setup();
    render(<ClienteBajaForm />);

    await buscar(user);

    expect(await screen.findByText("Cliente no encontrado")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
  });

  it("muestra 'ya dado de baja' y no llama a darDeBajaCliente para un cliente Inactivo", async () => {
    buscarCliente.mockResolvedValue({
      success: true,
      customer: { dni: 30111222, first_name: "Juan", last_name: "Perez", status: "Inactivo" },
    });
    const user = userEvent.setup();
    render(<ClienteBajaForm />);

    await buscar(user);

    expect(
      await screen.findByText("El cliente ya se encuentra dado de baja")
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
    expect(darDeBajaCliente).not.toHaveBeenCalled();
  });

  it("muestra los datos del cliente y los botones Confirmar/Cancelar para un cliente Activo", async () => {
    buscarCliente.mockResolvedValue({
      success: true,
      customer: { dni: 30111222, first_name: "Juan", last_name: "Perez", status: "Activo" },
    });
    const user = userEvent.setup();
    render(<ClienteBajaForm />);

    await buscar(user);

    expect(await screen.findByText("Juan Perez — DNI 30111222")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Confirmar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cancelar" })).toBeInTheDocument();
  });

  it("al confirmar, llama a darDeBajaCliente y muestra el mensaje de éxito", async () => {
    buscarCliente.mockResolvedValue({
      success: true,
      customer: { dni: 30111222, first_name: "Juan", last_name: "Perez", status: "Activo" },
    });
    darDeBajaCliente.mockResolvedValue({
      success: true,
      message: "Cliente dado de baja exitosamente",
      customer: { dni: 30111222, status: "Inactivo" },
    });
    const user = userEvent.setup();
    render(<ClienteBajaForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    expect(darDeBajaCliente).toHaveBeenCalledWith("30111222");
    expect(
      await screen.findByText("Cliente dado de baja exitosamente")
    ).toBeInTheDocument();
  });

  it("al cancelar, no llama a darDeBajaCliente y oculta la confirmación", async () => {
    buscarCliente.mockResolvedValue({
      success: true,
      customer: { dni: 30111222, first_name: "Juan", last_name: "Perez", status: "Activo" },
    });
    const user = userEvent.setup();
    render(<ClienteBajaForm />);

    await buscar(user);
    await user.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(darDeBajaCliente).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
  });
});
