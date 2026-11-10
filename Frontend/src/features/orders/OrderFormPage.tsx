/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Alta de comanda
 * La lógica del formulario vive en `useOrderForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, Field, Input, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useOrderForm } from './useOrderForm'

export function OrderFormPage({ reservationId }: { reservationId?: string }) {
  const { state, updateField, submit } = useOrderForm(reservationId)

  return (
    <>
      <PageHeader
        title={reservationId ? 'Nueva comanda desde reserva' : 'Nueva comanda'}
        subtitle={reservationId ? `Se utilizarán los datos de la reserva #${reservationId}.` : 'Seleccioná la mesa y, si corresponde, vinculá una reserva.'}
      />
      {state.error && <Alert tone="danger" title="No se pudo crear la comanda">{state.error}</Alert>}
      <form onSubmit={submit}>
        <Card
          title="Datos de la comanda"
          footer={<><Button onClick={() => navigate('/comandas')} disabled={state.saving}>Cancelar</Button><Button variant="primary" type="submit" disabled={state.saving}>{state.saving ? 'Guardando...' : 'Crear comanda'}</Button></>}
        >
          {reservationId ? (
            <div className="reservation-selection">
              <span>
                <strong>Reserva #{reservationId}</strong>
                <small className="muted">La mesa, el cliente y los productos se copiarán desde la reserva.</small>
              </span>
            </div>
          ) : (
            <div className="form-grid">
              <Field label="Comensales" required hint="Cantidad de personas que van a ocupar las mesas.">
                <Input type="number" min={1} value={state.comensales} onChange={(event) => updateField('comensales', event.target.value)} required />
              </Field>
              <Field label="Mesas asignadas" required hint={state.tablesLoading ? 'Cargando mesas...' : 'Se asignan automáticamente según la capacidad.'} error={state.fieldErrors.mesa_id}>
                <div className="table-assignment-list">
                  {state.mesaIds.length ? state.mesaIds.map((id) => {
                    const table = state.tables.find((candidate) => candidate.id === id)
                    return <span className="table-assignment-chip" key={id}>Mesa {id}<small>{table?.capacidad ?? 0} personas</small></span>
                  }) : <span className="muted">Sin combinación disponible</span>}
                </div>
                {state.comensales && !state.tablesLoading && !state.tablesError && state.mesaIds.length === 0 && (
                  <span className="error-text">No hay mesas disponibles con capacidad suficiente para {state.comensales} comensales.</span>
                )}
              </Field>
              <Field label="Cliente" hint="Opcional. Podés asociar un cliente." error={state.fieldErrors.cliente_id}>
                <Select value={state.clienteId} onChange={(event) => updateField('clienteId', event.target.value)}>
                  <option value="">Sin cliente</option>
                  {state.customers.map((customer) => <option key={customer.id} value={customer.id}>{customer.nombre} {customer.apellido}</option>)}
                </Select>
              </Field>
              <Field label="Reserva" hint="Opcional. Solo reservas disponibles ahora." error={state.fieldErrors.reserva_id}>
                <Select value={state.reservaId} onChange={(event) => updateField('reservaId', event.target.value)}>
                  <option value="">Sin reserva</option>
                  {state.reservations.filter((reservation) => {
                    if (reservation.estado !== 'pendiente') return false
                    const now = new Date()
                    const reservationTime = new Date(`${reservation.fecha}T${reservation.hora}`)
                    const difference = (now.getTime() - reservationTime.getTime()) / 60000
                    return difference >= -15 && difference <= 30
                  }).map((reservation) => {
                    const customer = state.customers.find((candidate) => candidate.id === reservation.cliente_id)
                    return <option key={reservation.id} value={reservation.id}>Reserva #{reservation.id} · {reservation.hora.slice(0, 5)} · {customer ? `${customer.nombre} ${customer.apellido}` : `Cliente #${reservation.cliente_id}`}</option>
                  })}
                </Select>
              </Field>
            </div>
          )}
          {!reservationId && <p className={state.tablesError ? 'error-text' : 'hint'}>{state.tablesError ?? 'Después de crear la comanda vas a poder agregar sus productos.'}</p>}
        </Card>
      </form>
    </>
  )
}
