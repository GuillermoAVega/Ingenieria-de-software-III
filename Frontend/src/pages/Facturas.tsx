import { Link, useNavigate } from 'react-router-dom'
import { api, type Factura } from '../api'
import { Cargando, PageHeader, fechaCorta, money, useAccion, useLoad } from '../ui'

export default function Facturas() {
  const navigate = useNavigate()
  const { data, error, reload } = useLoad(() => api<Factura[]>('/facturas?limit=500'))
  const accion = useAccion()

  const eliminar = async (f: Factura) => {
    if (!confirm(`¿Eliminar la factura #${f.id}?`)) return
    if (await accion(() => api(`/facturas/${f.id}`, { method: 'DELETE' }), 'Factura eliminada')) reload()
  }

  return (
    <>
      <PageHeader
        titulo="Facturación"
        subtitulo="Las facturas se generan desde una comanda cerrada"
        acciones={<Link to="/comandas" className="btn">Ir a comandas</Link>}
      />
      {!data ? (
        <Cargando error={error} />
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr><th>N.º</th><th>Comanda</th><th>Emisión</th><th className="num">Importe total</th><th className="num">Acciones</th></tr>
            </thead>
            <tbody>
              {[...data].sort((a, b) => b.id - a.id).map((f) => (
                <tr key={f.id} className="fila-link" onClick={() => navigate(`/facturacion/${f.id}`)}>
                  <td>#{f.id}</td>
                  <td>#{f.comanda_id}</td>
                  <td>{fechaCorta(f.fecha_hora_emision)}</td>
                  <td className="num">{money(f.importe_total)}</td>
                  <td className="num" onClick={(e) => e.stopPropagation()}>
                    <div className="row-actions">
                      <Link to={`/facturacion/${f.id}`} className="link">Abrir</Link>
                      <button className="link danger" onClick={() => eliminar(f)}>Eliminar</button>
                    </div>
                  </td>
                </tr>
              ))}
              {data.length === 0 && <tr><td colSpan={5} className="vacio">Todavía no hay facturas.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
