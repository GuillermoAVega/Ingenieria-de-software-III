import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, type ComprobantePago, type DetalleFactura, type Factura, type MedioPago } from '../api'
import { Badge, Campo, Cargando, Modal, PageHeader, fechaCorta, money, useAccion, useLoad } from '../ui'

type FormLinea = { precio_unitario: string; cantidad: string; promocion_id: string; precio_final: string }
type FormPago = { medio_pago_id: string; importe: string }

export default function FacturaDetalle() {
  const id = Number(useParams().id)
  const navigate = useNavigate()
  const accion = useAccion()
  const factura = useLoad(() => api<Factura>(`/facturas/${id}`), [id])
  const lineas = useLoad(() => api<DetalleFactura[]>(`/facturas/${id}/detalles`), [id])
  const pagos = useLoad(() => api<ComprobantePago[]>(`/facturas/${id}/comprobantes`), [id])
  const medios = useLoad(() => api<MedioPago[]>('/medios-pago'))

  const [modalLinea, setModalLinea] = useState<DetalleFactura | 'nuevo' | null>(null)
  const [linea, setLinea] = useState<FormLinea>({ precio_unitario: '', cantidad: '1', promocion_id: '', precio_final: '' })
  const [modalPago, setModalPago] = useState<ComprobantePago | 'nuevo' | null>(null)
  const [pago, setPago] = useState<FormPago>({ medio_pago_id: '', importe: '' })

  const f = factura.data
  if (!f || !lineas.data || !pagos.data || !medios.data) {
    return <Cargando error={factura.error || lineas.error || pagos.error || medios.error} />
  }

  const pagado = pagos.data.reduce((s, p) => s + p.importe, 0)
  const saldo = Math.max(f.importe_total - pagado, 0)
  const nombreMedio = (mid: number) => medios.data!.find((m) => m.id === mid)?.descripcion ?? `Medio #${mid}`
  const refrescar = () => {
    factura.reload()
    lineas.reload()
    pagos.reload()
  }

  // ---- Líneas ----
  const abrirLinea = (d: DetalleFactura | 'nuevo') => {
    setLinea(
      d === 'nuevo'
        ? { precio_unitario: '', cantidad: '1', promocion_id: '', precio_final: '' }
        : {
            precio_unitario: String(d.precio_unitario),
            cantidad: String(d.cantidad),
            promocion_id: d.promocion_id ? String(d.promocion_id) : '',
            precio_final: '',
          },
    )
    setModalLinea(d)
  }

  const guardarLinea = async () => {
    const nuevo = modalLinea === 'nuevo'
    const body: Record<string, unknown> = {
      precio_unitario: Number(linea.precio_unitario),
      cantidad: Number(linea.cantidad),
      promocion_id: linea.promocion_id ? Number(linea.promocion_id) : null,
    }
    if (linea.precio_final) body.precio_final = Number(linea.precio_final)
    const ok = await accion(
      () =>
        nuevo
          ? api('/detalles-factura', { method: 'POST', body: { ...body, factura_id: id } })
          : api(`/detalles-factura/${(modalLinea as DetalleFactura).id}`, { method: 'PUT', body }),
      nuevo ? 'Línea agregada' : 'Línea actualizada',
    )
    if (ok) {
      setModalLinea(null)
      refrescar()
    }
  }

  const quitarLinea = async (d: DetalleFactura) => {
    if (!confirm('¿Quitar esta línea de la factura?')) return
    if (await accion(() => api(`/detalles-factura/${d.id}`, { method: 'DELETE' }), 'Línea quitada')) refrescar()
  }

  // ---- Comprobantes ----
  const abrirPago = (p: ComprobantePago | 'nuevo') => {
    setPago(
      p === 'nuevo'
        ? { medio_pago_id: medios.data![0] ? String(medios.data![0].id) : '', importe: saldo ? String(saldo) : '' }
        : { medio_pago_id: String(p.medio_pago_id), importe: String(p.importe) },
    )
    setModalPago(p)
  }

  const guardarPago = async () => {
    const nuevo = modalPago === 'nuevo'
    const body = { medio_pago_id: Number(pago.medio_pago_id), importe: Number(pago.importe) }
    const ok = await accion(
      () =>
        nuevo
          ? api('/comprobantes-pago', { method: 'POST', body: { ...body, factura_id: id } })
          : api(`/comprobantes-pago/${(modalPago as ComprobantePago).id}`, { method: 'PUT', body }),
      nuevo ? 'Pago registrado' : 'Pago actualizado',
    )
    if (ok) {
      setModalPago(null)
      refrescar()
    }
  }

  const quitarPago = async (p: ComprobantePago) => {
    if (!confirm('¿Anular este comprobante de pago?')) return
    if (await accion(() => api(`/comprobantes-pago/${p.id}`, { method: 'DELETE' }), 'Comprobante anulado')) refrescar()
  }

  const eliminar = async () => {
    if (!confirm(`¿Eliminar la factura #${id}? Anulá antes sus comprobantes de pago.`)) return
    if (await accion(() => api(`/facturas/${id}`, { method: 'DELETE' }), 'Factura eliminada')) navigate('/facturacion')
  }

  const estadoPago = saldo === 0 && f.importe_total > 0 ? <Badge tono="verde">Pagada</Badge> : pagado > 0 ? <Badge tono="ambar">Pago parcial</Badge> : <Badge tono="azul">Pendiente de pago</Badge>

  return (
    <>
      <PageHeader
        migas={<><Link to="/facturacion">Facturación</Link> / #{f.id}</>}
        titulo={<>Factura #{f.id} {estadoPago}</>}
        subtitulo={<>Emitida el {fechaCorta(f.fecha_hora_emision)} · <Link className="link" to={`/comandas/${f.comanda_id}`}>Comanda #{f.comanda_id}</Link></>}
        acciones={<button className="link danger" onClick={eliminar}>Eliminar factura</button>}
      />
      <div className="cols">
        <div className="stack">
          <div className="card">
            <div className="card-head">
              <h2>Detalle de la factura</h2>
              <button className="btn" onClick={() => abrirLinea('nuevo')}>Agregar línea</button>
            </div>
            <table>
              <thead>
                <tr><th>Concepto</th><th className="num">Cant.</th><th className="num">P. unitario</th><th className="num">P. final</th><th className="num">Acciones</th></tr>
              </thead>
              <tbody>
                {lineas.data.map((d) => (
                  <tr key={d.id}>
                    <td>
                      {d.detalle_comanda_id ? `Ítem de comanda #${d.detalle_comanda_id}` : 'Ítem manual'}
                      {d.promocion_id && <small>Promoción #{d.promocion_id}</small>}
                    </td>
                    <td className="num">{d.cantidad}</td>
                    <td className="num">{money(d.precio_unitario)}</td>
                    <td className="num">{money(d.precio_final)}</td>
                    <td className="num">
                      <div className="row-actions">
                        <button className="link" onClick={() => abrirLinea(d)}>Editar</button>
                        <button className="link danger" onClick={() => quitarLinea(d)}>Quitar</button>
                      </div>
                    </td>
                  </tr>
                ))}
                {lineas.data.length === 0 && <tr><td colSpan={5} className="vacio">La factura no tiene líneas.</td></tr>}
              </tbody>
            </table>
          </div>

          <div className="card">
            <div className="card-head">
              <h2>Comprobantes de pago</h2>
              <button className="btn" disabled={saldo === 0} onClick={() => abrirPago('nuevo')}>Registrar pago</button>
            </div>
            <table>
              <thead>
                <tr><th>N.º</th><th>Medio de pago</th><th>Fecha</th><th className="num">Importe</th><th className="num">Acciones</th></tr>
              </thead>
              <tbody>
                {pagos.data.map((p) => (
                  <tr key={p.id}>
                    <td>#{p.id}</td>
                    <td>{nombreMedio(p.medio_pago_id)}</td>
                    <td>{fechaCorta(p.fecha_hora_emision)}</td>
                    <td className="num">{money(p.importe)}</td>
                    <td className="num">
                      <div className="row-actions">
                        <button className="link" onClick={() => abrirPago(p)}>Editar</button>
                        <button className="link danger" onClick={() => quitarPago(p)}>Anular</button>
                      </div>
                    </td>
                  </tr>
                ))}
                {pagos.data.length === 0 && <tr><td colSpan={5} className="vacio">Todavía no se registraron pagos.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="card">
          <div className="card-head"><h2>Resumen</h2></div>
          <div className="card-body">
            <div className="resumen-linea"><span className="muted">Total</span><span>{money(f.importe_total)}</span></div>
            <div className="resumen-linea"><span className="muted">Pagado</span><span>{money(pagado)}</span></div>
            <div className="resumen-total"><span>Saldo</span><span>{money(saldo)}</span></div>
          </div>
        </aside>
      </div>

      {modalLinea && (
        <Modal titulo={modalLinea === 'nuevo' ? 'Agregar línea' : 'Editar línea'} onClose={() => setModalLinea(null)} onSubmit={guardarLinea}>
          <div className="grid-2">
            <Campo label="Precio unitario *"><input type="number" min={0} step="0.01" value={linea.precio_unitario} onChange={(e) => setLinea({ ...linea, precio_unitario: e.target.value })} required autoFocus /></Campo>
            <Campo label="Cantidad *"><input type="number" min={1} value={linea.cantidad} onChange={(e) => setLinea({ ...linea, cantidad: e.target.value })} required /></Campo>
            <Campo label="Promoción (N.º)" ayuda="Opcional."><input type="number" min={1} value={linea.promocion_id} onChange={(e) => setLinea({ ...linea, promocion_id: e.target.value })} /></Campo>
            <Campo label="Precio final" ayuda="Vacío = unitario × cantidad."><input type="number" min={0} step="0.01" value={linea.precio_final} onChange={(e) => setLinea({ ...linea, precio_final: e.target.value })} /></Campo>
          </div>
        </Modal>
      )}

      {modalPago && (
        <Modal titulo={modalPago === 'nuevo' ? 'Registrar pago' : 'Editar comprobante'} onClose={() => setModalPago(null)} onSubmit={guardarPago}>
          <Campo label="Medio de pago *" ayuda={medios.data.length === 0 ? 'Primero cargá un medio de pago en Administración.' : undefined}>
            <select value={pago.medio_pago_id} onChange={(e) => setPago({ ...pago, medio_pago_id: e.target.value })} required>
              <option value="" disabled>Seleccioná un medio</option>
              {medios.data.map((m) => <option key={m.id} value={m.id}>{m.descripcion}</option>)}
            </select>
          </Campo>
          <Campo label="Importe *" ayuda={`No puede superar el saldo (${money(modalPago === 'nuevo' ? saldo : saldo + modalPago.importe)}).`}>
            <input type="number" min={0.01} step="0.01" value={pago.importe} onChange={(e) => setPago({ ...pago, importe: e.target.value })} required />
          </Campo>
        </Modal>
      )}
    </>
  )
}
