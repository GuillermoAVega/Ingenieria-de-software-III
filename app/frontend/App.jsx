import { useState } from "react";

import { ClienteBajaForm } from "./components/ClienteBajaForm.jsx";
import { ClienteEdicionForm } from "./components/ClienteEdicionForm.jsx";
import { ClienteForm } from "./components/ClienteForm.jsx";
import { ClienteListado } from "./components/ClienteListado.jsx";
import { ProductoBajaForm } from "./components/ProductoBajaForm.jsx";
import { ProductoEdicionForm } from "./components/ProductoEdicionForm.jsx";
import { ProductoForm } from "./components/ProductoForm.jsx";
import { ProductoListado } from "./components/ProductoListado.jsx";
import { VentaAnulacionForm } from "./components/VentaAnulacionForm.jsx";
import { VentaEdicionForm } from "./components/VentaEdicionForm.jsx";
import { VentaForm } from "./components/VentaForm.jsx";
import { VentasListado } from "./components/VentasListado.jsx";
import "./App.css";

const TABS = /** @type {const} */ ({
  ALTA: "ALTA",
  BAJA: "BAJA",
  EDICION: "EDICION",
  LISTADO: "LISTADO",
  ALTA_PRODUCTO: "ALTA_PRODUCTO",
  BAJA_PRODUCTO: "BAJA_PRODUCTO",
  EDICION_PRODUCTO: "EDICION_PRODUCTO",
  LISTADO_PRODUCTO: "LISTADO_PRODUCTO",
  ALTA_VENTA: "ALTA_VENTA",
  ANULAR_VENTA: "ANULAR_VENTA",
  MODIFICAR_VENTA: "MODIFICAR_VENTA",
  LISTADO_VENTA: "LISTADO_VENTA",
});

/** @returns {import("react").JSX.Element} */
export function App() {
  const [activeTab, setActiveTab] = useState(/** @type {string} */ (TABS.ALTA));

  return (
    <main className="app-page">
      <nav className="app-page__tabs">
        <button
          type="button"
          className={activeTab === TABS.ALTA ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.ALTA)}
        >
          Alta de Cliente
        </button>
        <button
          type="button"
          className={activeTab === TABS.BAJA ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.BAJA)}
        >
          Baja de Cliente
        </button>
        <button
          type="button"
          className={activeTab === TABS.EDICION ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.EDICION)}
        >
          Editar Cliente
        </button>
        <button
          type="button"
          className={activeTab === TABS.LISTADO ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.LISTADO)}
        >
          Listar Clientes
        </button>
        <button
          type="button"
          className={activeTab === TABS.ALTA_PRODUCTO ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.ALTA_PRODUCTO)}
        >
          Alta de Producto
        </button>
        <button
          type="button"
          className={activeTab === TABS.BAJA_PRODUCTO ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.BAJA_PRODUCTO)}
        >
          Baja de Producto
        </button>
        <button
          type="button"
          className={activeTab === TABS.EDICION_PRODUCTO ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.EDICION_PRODUCTO)}
        >
          Editar Producto
        </button>
        <button
          type="button"
          className={activeTab === TABS.LISTADO_PRODUCTO ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.LISTADO_PRODUCTO)}
        >
          Listar Productos
        </button>
        <button
          type="button"
          className={activeTab === TABS.ALTA_VENTA ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.ALTA_VENTA)}
        >
          Registrar Venta
        </button>
        <button
          type="button"
          className={activeTab === TABS.ANULAR_VENTA ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.ANULAR_VENTA)}
        >
          Anular Venta
        </button>
        <button
          type="button"
          className={activeTab === TABS.MODIFICAR_VENTA ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.MODIFICAR_VENTA)}
        >
          Modificar Venta
        </button>
        <button
          type="button"
          className={activeTab === TABS.LISTADO_VENTA ? "app-page__tab--active" : undefined}
          onClick={() => setActiveTab(TABS.LISTADO_VENTA)}
        >
          Listar Ventas
        </button>
      </nav>

      {activeTab === TABS.ALTA && <ClienteForm />}
      {activeTab === TABS.BAJA && <ClienteBajaForm />}
      {activeTab === TABS.EDICION && <ClienteEdicionForm />}
      {activeTab === TABS.LISTADO && <ClienteListado />}
      {activeTab === TABS.ALTA_PRODUCTO && <ProductoForm />}
      {activeTab === TABS.BAJA_PRODUCTO && <ProductoBajaForm />}
      {activeTab === TABS.EDICION_PRODUCTO && <ProductoEdicionForm />}
      {activeTab === TABS.LISTADO_PRODUCTO && <ProductoListado />}
      {activeTab === TABS.ALTA_VENTA && <VentaForm />}
      {activeTab === TABS.ANULAR_VENTA && <VentaAnulacionForm />}
      {activeTab === TABS.MODIFICAR_VENTA && <VentaEdicionForm />}
      {activeTab === TABS.LISTADO_VENTA && <VentasListado />}
    </main>
  );
}
