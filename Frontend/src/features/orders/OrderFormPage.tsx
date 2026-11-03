import { Alert, Button, Card, Field, Input, PageHeader } from '../../ui/ui'
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
              <Field label="Mesa" required hint="Número de mesa." error={state.fieldErrors.mesa_id}>
                <Input type="number" min={1} value={state.mesaId} onChange={(event) => updateField('mesaId', event.target.value)} required />
              </Field>
              <Field label="Cliente" hint="Opcional. Número de cliente." error={state.fieldErrors.cliente_id}>
                <Input type="number" min={1} value={state.clienteId} onChange={(event) => updateField('clienteId', event.target.value)} />
              </Field>
              <Field label="Reserva" hint="Opcional. Número de reserva." error={state.fieldErrors.reserva_id}>
                <Input type="number" min={1} value={state.reservaId} onChange={(event) => updateField('reservaId', event.target.value)} />
              </Field>
            </div>
          )}
          {!reservationId && <p className="hint">Después de crear la comanda vas a poder agregar sus productos.</p>}
        </Card>
      </form>
    </>
  )
}
