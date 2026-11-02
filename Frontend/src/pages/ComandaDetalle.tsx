import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, type Comanda, type DetalleComanda, type Factura } from '../api'
import { Badge, Campo, Cargando, Modal, PageHeader, hhmm, useAccion, useLoad } from '../ui'

type FormDetalle = { producto_id: string; cantidad: string; observaciones: string }

export default function ComandaDetalle() {
  const id = Number(useParams().id)
  const navigate = useNavigate()
  const accion = useAccion()
  const comanda = useLoad(() => api<Comanda>(`/comandas/${id}`), [id])
  const facturas = useLoad(() => api<Factura[]>(`/facturas?comanda_id=${id}`), [id])
  const [modalItem, setModalItem] = useState<DetalleComanda | 'nuevo' | null>(null)
  const [item, setItem] = useState<FormDetalle>({ producto_id: '', cantidad: '1', observaciones: '' })
  const [facturando, setFacturando] = useState<Record<number, string> | null>(null)

  const c = comanda.data
  if (!c) return <Cargando error={comanda.error} />

  const factura = facturas.data?.[0]
  const abierta = c.estado === 'abierta'
  const pendientes = c.detalles.filter((d) => !d.entregado).length
  const refrescar = () => {
    comanda.reload()
    facturas.reload()
  }

  const abrirItem = (d: DetalleComanda | 'nuevo') => {
    setItem(
      d === 'nuevo'
        ? { producto_id: '', cantidad: '1', observaciones: '' }
        : { producto_id: String(d.producto_id), cantidad: String(d.cantidad), observaciones: d.observaciones ?? '' },
    )
    setModalItem(d)
  }

  const guardarItem = async () => {
    const body = {
      producto_id: Number(item.producto_id),
      cantidad: Number(item.cantidad),
      observaciones: item.observaciones.trim() || null,
    }
    const nuevo = modalItem === 'nuevo'
    const ok = await accion(
      () =>
        nuevo
          ? api('/detalles-comanda', { method: 'POST', body: { ...body, comanda_id: id } })
          : api(`/detalles-comanda/${(modalItem as DetalleComanda).id}`, { method: 'PUT', body }),
      nuevo ? 'Producto agregado' : 'Producto actualizado',
    )
    if (ok) {
      setModalItem(null)
      comanda.reload()
    }
  }

  const quitar = async (d: DetalleComanda) => {
    if (!confirm('¿Quitar este producto de la comanda?')) return
    if (await accion(() => api(`/detalles-comanda/${d.id}`, { method: 'DELETE' }), 'Producto quitado')) comanda.reload()
  }

  const alternarEntrega = async (d: DetalleComanda) => {
    if (await accion(() => api(`/detalles-comanda/${d.id}`, { method: 'PUT', body: { entregado: !d.entregado } }))) comanda.reload()
  }

  const cambiarEstado = async (estado: 'abierta' | 'cerrada') => {
    const ok = await accion(
      () => api(`/comandas/${id}`, { method: 'PUT', body: { estado } }),
      estado === 'cerrada' ? 'Comanda cerrada' : 'Comanda reabierta',
    )
    if (ok) comanda.reload()
  }

  const eliminar = async () => {
    if (!confirm(`¿Eliminar la comanda #${id}?`)) return
    if (await accion(() => api(`/comandas/${id}`, { method: 'DELETE' }), 'Comanda eliminada')) navigate('/comandas')
  }

  const generarFactura = async () => {
    if (!facturando) return
    let facturaId = 0
    const ok = await accion(async () => {
      const f = await api<Factura>('/facturas', { method: 'POST', body: { comanda_id: id } })
      facturaId = f.id
      for (const d of c.detalles) {
        await api('/detalles-factura', {
          method: 'POST',
          body: {
            factura_id: f.id,
            detalle_comanda_id: d.id,
            precio_unitario: Number(facturando[d.id]),
            cantidad: d.cantidad,
          },
        })
      }
    }, 'Factura generada')
    if (ok) navigate(`/facturacion/${facturaId}`)
    else refrescar()
  }

  return (
    <>
      <PageHeader
        migas={<><Link to="/comandas">Comandas</Link> / #{c.id}</>}
        titulo={<>Comanda #{c.id} <Badge tono={abierta ? 'azul' : 'gris'}>{abierta ? 'Abierta' : 'Cerrada'}</Badge></>}
        subtitulo={`Mesa ${c.mesa_id} · ${new Date(c.fecha + 'T00:00').toLocaleDateString('es-AR')} · abierta a las ${hhmm(c.hora)}`}
        acciones={<button className="link danger" onClick={eliminar}>Eliminar comanda</button>}
      />
      <div className="cols">
        <div className="stack">
          <DatosComanda key={`${c.id}-${c.mesa_id}-${c.mozo_id}-${c.cliente_id}-${c.reserva_id}`} c={c} bloqueada={!abierta} onSaved={comanda.reload} />

          <div className="card">
            <div className="card-head">
              <div>
                <h2>Productos pedidos</h2>
                <p className="sub">{c.detalles.length} ítems · {pendientes} pendientes de entrega</p>
              </div>
              <button className="btn" disabled={!abierta} onClick={() => abrirItem('nuevo')}>Agregar producto</button>
            </div>
            <table>
              <thead>
                <tr><th>Producto</th><th className="num">Cant.</th><th>Observaciones</th><th>Entrega</th><th className="num">Acciones</th></tr>
              </thead>
              <tbody>
                {c.detalles.map((d) => (
                  <tr key={d.id}>
                    <td>Producto #{d.producto_id}</td>
                    <td className="num">{d.cantidad}</td>
                    <td>{d.observaciones || '—'}</td>
                    <td>
                      <button className="link" title="Cambiar estado de entrega" onClick={() => alternarEntrega(d)}>
                        <Badge tono={d.entregado ? 'verde' : 'ambar'}>{d.entregado ? 'Entregado' : 'Pendiente'}</Badge>
                      </button>
                    </td>
                    <td className="num">
                      <div className="row-actions">
                        <button className="link" disabled={!abierta} onClick={() => abrirItem(d)}>Editar</button>
                        <button className="link danger" disabled={!abierta} onClick={() => quitar(d)}>Quitar</button>
                      </div>
                    </td>
                  </tr>
                ))}
                {c.detalles.length === 0 && <tr><td colSpan={5} className="vacio">Todavía no se agregaron productos.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="card">
          <div className="card-head"><h2>Resumen</h2></div>
          <div className="card-body">
            <div className="resumen-linea"><span className="muted">Ítems</span><span>{c.detalles.reduce((s, d) => s + d.cantidad, 0)} unidades</span></div>
            <div className="resumen-linea"><span className="muted">Pendientes</span><span>{pendientes}</span></div>
            {factura && <div className="resumen-linea"><span className="muted">Factura</span><Link className="link" to={`/facturacion/${factura.id}`}>#{factura.id}</Link></div>}
          </div>
          <div className="resumen-foot">
            {abierta ? (
              <button className="btn primary block" disabled={c.detalles.length === 0} onClick={() => cambiarEstado('cerrada')}>Cerrar comanda</button>
            ) : (
              <button className="btn block" disabled={!!factura} onClick={() => cambiarEstado('abierta')}>Reabrir comanda</button>
            )}
            {factura ? (
              <button className="btn block" onClick={() => navigate(`/facturacion/${factura.id}`)}>Ver factura</button>
            ) : (
              <button
                className="btn block"
                disabled={abierta}
                onClick={() => setFacturando(Object.fromEntries(c.detalles.map((d) => [d.id, ''])))}
              >
                Generar factura
              </button>
            )}
            {!factura && abierta && <small>La factura se genera una vez cerrada la comanda.</small>}
          </div>
        </aside>
      </div>

      {modalItem && (
        <Modal titulo={modalItem === 'nuevo' ? 'Agregar producto' : 'Editar producto'} onClose={() => setModalItem(null)} onSubmit={guardarItem}>
          <Campo label="N.º de producto *" ayuda="Se carga por número hasta que esté disponible la sección Productos.">
            <input type="number" min={1} value={item.producto_id} onChange={(e) => setItem({ ...item, producto_id: e.target.value })} required autoFocus />
          </Campo>
          <Campo label="Cantidad *">
            <input type="number" min={1} value={item.cantidad} onChange={(e) => setItem({ ...item, cantidad: e.target.value })} required />
          </Campo>
          <Campo label="Observaciones">
            <input value={item.observaciones} maxLength={255} onChange={(e) => setItem({ ...item, observaciones: e.target.value })} placeholder="Ej.: Sin jamón" />
          </Campo>
        </Modal>
      )}

      {facturando && (
        <Modal titulo="Generar factura" onClose={() => setFacturando(null)} onSubmit={generarFactura} submitLabel="Generar factura">
          <div className="nota">Ingresá el precio unitario de cada producto. Cuando esté la sección Productos, se tomará automáticamente de la carta.</div>
          {c.detalles.map((d) => (
            <Campo key={d.id} label={`Producto #${d.producto_id} × ${d.cantidad}`}>
              <input
                type="number"
                min={0}
                step="0.01"
                placeholder="Precio unitario"
                value={facturando[d.id]}
                onChange={(e) => setFacturando({ ...facturando, [d.id]: e.target.value })}
                required
              />
            </Campo>
          ))}
        </Modal>
      )}
    </>
  )
}

function DatosComanda({ c, bloqueada, onSaved }: { c: Comanda; bloqueada: boolean; onSaved: () => void }) {
  const accion = useAccion()
  const [f, setF] = useState({
    mesa_id: String(c.mesa_id),
    mozo_id: String(c.mozo_id),
    cliente_id: c.cliente_id ? String(c.cliente_id) : '',
    reserva_id: c.reserva_id ? String(c.reserva_id) : '',
  })
  const set = (k: keyof typeof f) => (e: { target: { value: string } }) => setF({ ...f, [k]: e.target.value })
  const cambio =
    f.mesa_id !== String(c.mesa_id) ||
    f.mozo_id !== String(c.mozo_id) ||
    f.cliente_id !== (c.cliente_id ? String(c.cliente_id) : '') ||
    f.reserva_id !== (c.reserva_id ? String(c.reserva_id) : '')

  const guardar = async () => {
    const ok = await accion(
      () =>
        api(`/comandas/${c.id}`, {
          method: 'PUT',
          body: {
            mesa_id: Number(f.mesa_id),
            mozo_id: Number(f.mozo_id),
            cliente_id: f.cliente_id ? Number(f.cliente_id) : null,
            reserva_id: f.reserva_id ? Number(f.reserva_id) : null,
          },
        }),
      'Datos guardados',
    )
    if (ok) onSaved()
  }

  return (
    <div className="card">
      <div className="card-head">
        <h2>Datos de la comanda</h2>
        <button className="btn" disabled={bloqueada || !cambio || !f.mesa_id || !f.mozo_id} onClick={guardar}>Guardar cambios</button>
      </div>
      <div className="card-body grid-2">
        <Campo label="Mesa (N.º)"><input type="number" min={1} value={f.mesa_id} onChange={set('mesa_id')} disabled={bloqueada} /></Campo>
        <Campo label="Mozo (N.º)"><input type="number" min={1} value={f.mozo_id} onChange={set('mozo_id')} disabled={bloqueada} /></Campo>
        <Campo label="Cliente (N.º)" ayuda="Opcional. Vacío = sin cliente asociado."><input type="number" min={1} value={f.cliente_id} onChange={set('cliente_id')} disabled={bloqueada} /></Campo>
        <Campo label="Reserva (N.º)" ayuda="Opcional. Vacío = sin reserva."><input type="number" min={1} value={f.reserva_id} onChange={set('reserva_id')} disabled={bloqueada} /></Campo>
      </div>
    </div>
  )
}
