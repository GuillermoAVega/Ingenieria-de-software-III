import { useState } from "react";

import { ClienteBajaForm } from "./components/ClienteBajaForm.jsx";
import { ClienteEdicionForm } from "./components/ClienteEdicionForm.jsx";
import { ClienteForm } from "./components/ClienteForm.jsx";
import { ClienteListado } from "./components/ClienteListado.jsx";
import "./App.css";

const TABS = /** @type {const} */ ({
  ALTA: "ALTA",
  BAJA: "BAJA",
  EDICION: "EDICION",
  LISTADO: "LISTADO",
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
      </nav>

      {activeTab === TABS.ALTA && <ClienteForm />}
      {activeTab === TABS.BAJA && <ClienteBajaForm />}
      {activeTab === TABS.EDICION && <ClienteEdicionForm />}
      {activeTab === TABS.LISTADO && <ClienteListado />}
    </main>
  );
}
