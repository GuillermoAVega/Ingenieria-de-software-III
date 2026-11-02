import { NavLink, Route, Routes } from 'react-router-dom'
import Inicio from './pages/Inicio'
import Comandas from './pages/Comandas'
import ComandaDetalle from './pages/ComandaDetalle'
import Facturas from './pages/Facturas'
import FacturaDetalle from './pages/FacturaDetalle'
import MediosPago from './pages/MediosPago'
import NoEncontrada from './pages/NoEncontrada'

const NAV: { titulo: string; items: { to: string; label: string }[] }[] = [
  {
    titulo: 'OPERACIÓN',
    items: [
      { to: '/', label: 'Inicio' },
      { to: '/comandas', label: 'Comandas' },
      { to: '/facturacion', label: 'Facturación' },
    ],
  },
  {
    titulo: 'ADMINISTRACIÓN',
    items: [{ to: '/medios-pago', label: 'Medios de pago' }],
  },
]

export default function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <img src="/logo.png" alt="Sabor de Mar - Restaurante" />
        </div>
        {NAV.map((g) => (
          <nav key={g.titulo} className="nav-group">
            <div className="nav-title">{g.titulo}</div>
            {g.items.map((i) => (
              <NavLink
                key={i.to}
                to={i.to}
                end={i.to === '/'}
                className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
              >
                {i.label}
              </NavLink>
            ))}
          </nav>
        ))}
        <div className="user">
          <span className="avatar">AD</span>
          <div>
            Administrador
            <small>Encargado de salón</small>
          </div>
        </div>
      </aside>
      <main className="main">
        <div className="contenido">
          <Routes>
            <Route path="/" element={<Inicio />} />
            <Route path="/comandas" element={<Comandas />} />
            <Route path="/comandas/:id" element={<ComandaDetalle />} />
            <Route path="/facturacion" element={<Facturas />} />
            <Route path="/facturacion/:id" element={<FacturaDetalle />} />
            <Route path="/medios-pago" element={<MediosPago />} />
            <Route path="*" element={<NoEncontrada />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}
