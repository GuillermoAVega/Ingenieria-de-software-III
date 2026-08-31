import { ClienteForm } from "./components/ClienteForm.jsx";
import "./App.css";

/** @returns {import("react").JSX.Element} */
export function App() {
  return (
    <main className="app-page">
      <h1 className="app-page__title">Alta de Cliente</h1>
      <ClienteForm />
    </main>
  );
}
