import { Link, useNavigate } from 'react-router-dom'
import { api, type Comanda, type Factura } from '../api'
import { Badge, Cargando, PageHeader, hhmm, money, useLoad } from '../ui'

export default function Inicio() {
  const navigate = useNavigate()
  const comandas = useLoad(() => api<Comanda[]>('/comandas?limit=500'))
  const facturas = useLoad(() => api<Factura[]>('/facturas?limit=500'))

  if (!comandas.data || !facturas.data) return <Cargando error={comandas.error || facturas.error} />

  const abiertas = comandas.data.filter((c) => c.estado === 'abierta')
  const pendientes = abiertas.filter((c) => c.detalles.some((d) => !d.entregado)).length
  const hoy = new Date().toDateString()
  const deHoy = facturas.data.filter((f) => new Date(f.fecha_hora_emision).toDateString() === hoy)
  const facturado = deHoy.reduce((s, f) => s + f.importe_total, 0)
  const recientes = [...comandas.data].sort((a, b) => b.id - a.id).slice(0, 6)

  return (
    <>
      <PageHeader
        titulo="Inicio"
        subtitulo={new Date().toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long' })}
        acciones={
          <Link to="/comandas?nueva=1" className="btn primary">
            Nueva comanda
          </Link>
        }
      />
      <div className="stats">
        <div className="card stat">
          <div className="label">Comandas abiertas</div>
          <div className="value">{abiertas.length}</div>
          <div className="muted">{pendientes} con productos pendientes</div>
        </div>
        <div className="card stat">
          <div className="label">Facturas de hoy</div>
          <div className="value">{deHoy.length}</div>
          <div className="muted">emitidas</div>
        </div>
        <div className="card stat">
          <div className="label">Facturado hoy</div>
          <div className="value">{money(facturado)}</div>
          <div className="muted">{deHoy.length} facturas</div>
        </div>
      </div>
      <div className="card">
        <div className="card-head">
          <div>
            <h2>Últimas comandas</h2>
          </div>
          <Link to="/comandas" className="link">Ver todas</Link>
        </div>
        <table>
          <thead>
            <tr><th>N.º</th><th>Mesa</th><th>Mozo</th><th>Hora</th><th>Estado</th></tr>
          </thead>
          <tbody>
            {recientes.map((c) => (
              <tr key={c.id} className="fila-link" onClick={() => navigate(`/comandas/${c.id}`)}>
                <td>#{c.id}</td>
                <td>Mesa {c.mesa_id}</td>
                <td>Mozo {c.mozo_id}</td>
                <td>{hhmm(c.hora)}</td>
                <td><Badge tono={c.estado === 'abierta' ? 'azul' : 'gris'}>{c.estado === 'abierta' ? 'Abierta' : 'Cerrada'}</Badge></td>
              </tr>
            ))}
            {recientes.length === 0 && <tr><td colSpan={5} className="vacio">Todavía no hay comandas.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  )
}
