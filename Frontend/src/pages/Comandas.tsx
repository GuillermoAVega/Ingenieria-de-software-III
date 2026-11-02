import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api, type Comanda } from '../api'
import { Badge, Campo, Cargando, Modal, PageHeader, hhmm, useAccion, useLoad } from '../ui'

const hoyISO = () => new Date().toLocaleDateString('sv-SE') // YYYY-MM-DD en hora local
const ahoraHHMM = () => new Date().toTimeString().slice(0, 5)

export default function Comandas() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const [estado, setEstado] = useState('')
  const { data, error, reload } = useLoad(() => api<Comanda[]>('/comandas?limit=500'))
  const accion = useAccion()
  const [form, setForm] = useState({ fecha: hoyISO(), hora: ahoraHHMM(), mesa_id: '', mozo_id: '', cliente_id: '', reserva_id: '' })
  const nueva = params.get('nueva') === '1'

  const abrirNueva = () => {
    setForm({ fecha: hoyISO(), hora: ahoraHHMM(), mesa_id: '', mozo_id: '', cliente_id: '', reserva_id: '' })
    setParams({ nueva: '1' })
  }

  const crear = async () => {
    let creada: Comanda | undefined
    const ok = await accion(async () => {
      creada = await api<Comanda>('/comandas', {
        method: 'POST',
        body: {
          fecha: form.fecha,
          hora: form.hora,
          mesa_id: Number(form.mesa_id),
          mozo_id: Number(form.mozo_id),
          cliente_id: form.cliente_id ? Number(form.cliente_id) : null,
          reserva_id: form.reserva_id ? Number(form.reserva_id) : null,
        },
      })
    }, 'Comanda creada')
    if (ok && creada) navigate(`/comandas/${creada.id}`)
  }

  const eliminar = async (c: Comanda) => {
    if (!confirm(`¿Eliminar la comanda #${c.id}?`)) return
    const ok = await accion(() => api(`/comandas/${c.id}`, { method: 'DELETE' }), 'Comanda eliminada')
    if (ok) reload()
  }

  const filtradas = (data ?? []).filter((c) => !estado || c.estado === estado).sort((a, b) => b.id - a.id)
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) => setForm({ ...form, [k]: e.target.value })

  return (
    <>
      <PageHeader
        titulo="Comandas"
        subtitulo="Pedidos de cada mesa, abiertos y cerrados"
        acciones={<button className="btn primary" onClick={abrirNueva}>Nueva comanda</button>}
      />
      {!data ? (
        <Cargando error={error} />
      ) : (
        <div className="card">
          <div className="filtros">
            <select value={estado} onChange={(e) => setEstado(e.target.value)}>
              <option value="">Todos los estados</option>
              <option value="abierta">Abiertas</option>
              <option value="cerrada">Cerradas</option>
            </select>
          </div>
          <table>
            <thead>
              <tr><th>N.º</th><th>Mesa</th><th>Mozo</th><th>Fecha</th><th>Hora</th><th>Ítems</th><th>Estado</th><th className="num">Acciones</th></tr>
            </thead>
            <tbody>
              {filtradas.map((c) => (
                <tr key={c.id} className="fila-link" onClick={() => navigate(`/comandas/${c.id}`)}>
                  <td>#{c.id}</td>
                  <td>Mesa {c.mesa_id}</td>
                  <td>Mozo {c.mozo_id}</td>
                  <td>{new Date(c.fecha + 'T00:00').toLocaleDateString('es-AR')}</td>
                  <td>{hhmm(c.hora)}</td>
                  <td>{c.detalles.length}</td>
                  <td><Badge tono={c.estado === 'abierta' ? 'azul' : 'gris'}>{c.estado === 'abierta' ? 'Abierta' : 'Cerrada'}</Badge></td>
                  <td className="num" onClick={(e) => e.stopPropagation()}>
                    <div className="row-actions">
                      <Link to={`/comandas/${c.id}`} className="link">Abrir</Link>
                      <button className="link danger" onClick={() => eliminar(c)}>Eliminar</button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtradas.length === 0 && <tr><td colSpan={8} className="vacio">No hay comandas para mostrar.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
      {nueva && (
        <Modal titulo="Nueva comanda" onClose={() => setParams({})} onSubmit={crear} submitLabel="Crear comanda">
          <div className="grid-2">
            <Campo label="Fecha *"><input type="date" value={form.fecha} onChange={set('fecha')} required /></Campo>
            <Campo label="Hora *"><input type="time" value={form.hora} onChange={set('hora')} required /></Campo>
            <Campo label="N.º de mesa *"><input type="number" min={1} value={form.mesa_id} onChange={set('mesa_id')} required /></Campo>
            <Campo label="N.º de mozo *"><input type="number" min={1} value={form.mozo_id} onChange={set('mozo_id')} required /></Campo>
            <Campo label="N.º de cliente" ayuda="Opcional."><input type="number" min={1} value={form.cliente_id} onChange={set('cliente_id')} /></Campo>
            <Campo label="N.º de reserva" ayuda="Opcional."><input type="number" min={1} value={form.reserva_id} onChange={set('reserva_id')} /></Campo>
          </div>
          <div className="nota">Mesa, mozo, cliente y reserva se cargan por número hasta que estén disponibles esas secciones.</div>
        </Modal>
      )}
    </>
  )
}
