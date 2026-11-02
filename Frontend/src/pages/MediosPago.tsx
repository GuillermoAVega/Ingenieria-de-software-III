import { useState } from 'react'
import { api, type MedioPago } from '../api'
import { Campo, Cargando, Modal, PageHeader, useAccion, useLoad } from '../ui'

export default function MediosPago() {
  const { data, error, reload } = useLoad(() => api<MedioPago[]>('/medios-pago'))
  const [editando, setEditando] = useState<MedioPago | 'nuevo' | null>(null)
  const [descripcion, setDescripcion] = useState('')
  const accion = useAccion()

  const abrir = (m: MedioPago | 'nuevo') => {
    setDescripcion(m === 'nuevo' ? '' : m.descripcion)
    setEditando(m)
  }

  const guardar = async () => {
    const nuevo = editando === 'nuevo'
    const ok = await accion(
      () =>
        nuevo
          ? api('/medios-pago', { method: 'POST', body: { descripcion } })
          : api(`/medios-pago/${(editando as MedioPago).id}`, { method: 'PUT', body: { descripcion } }),
      nuevo ? 'Medio de pago creado' : 'Medio de pago actualizado',
    )
    if (ok) {
      setEditando(null)
      reload()
    }
  }

  const eliminar = async (m: MedioPago) => {
    if (!confirm(`¿Eliminar "${m.descripcion}"?`)) return
    const ok = await accion(() => api(`/medios-pago/${m.id}`, { method: 'DELETE' }), 'Medio de pago eliminado')
    if (ok) reload()
  }

  return (
    <>
      <PageHeader
        titulo="Medios de pago"
        subtitulo="Formas de pago disponibles para los comprobantes"
        acciones={<button className="btn primary" onClick={() => abrir('nuevo')}>Nuevo medio de pago</button>}
      />
      {!data ? (
        <Cargando error={error} />
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr><th>Descripción</th><th className="num">Acciones</th></tr>
            </thead>
            <tbody>
              {data.map((m) => (
                <tr key={m.id}>
                  <td>{m.descripcion}</td>
                  <td className="num">
                    <div className="row-actions">
                      <button className="link" onClick={() => abrir(m)}>Editar</button>
                      <button className="link danger" onClick={() => eliminar(m)}>Eliminar</button>
                    </div>
                  </td>
                </tr>
              ))}
              {data.length === 0 && <tr><td colSpan={2} className="vacio">No hay medios de pago cargados.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
      {editando && (
        <Modal
          titulo={editando === 'nuevo' ? 'Nuevo medio de pago' : 'Editar medio de pago'}
          onClose={() => setEditando(null)}
          onSubmit={guardar}
        >
          <Campo label="Descripción *" ayuda="Ej.: Efectivo, Tarjeta de débito, Transferencia. No puede repetirse.">
            <input value={descripcion} onChange={(e) => setDescripcion(e.target.value)} required maxLength={100} autoFocus />
          </Campo>
        </Modal>
      )}
    </>
  )
}
