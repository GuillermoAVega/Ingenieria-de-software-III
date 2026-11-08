/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Alta de comanda
 * La lógica del formulario vive en `useOrderForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, DateInput, Field, Input, PageHeader } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useOrderForm } from './useOrderForm'

export function OrderFormPage() {
  const { state, updateField, submit } = useOrderForm()

  return (
    <>
      <PageHeader
        title="Nueva comanda"
        subtitle="Cargá la mesa, el mozo y los datos generales del pedido."
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo crear la comanda">
          {state.error}
        </Alert>
      )}

      <form onSubmit={submit}>
        <Card
          title="Datos de la comanda"
          footer={
            <>
              <Button onClick={() => navigate('/comandas')} disabled={state.saving}>
                Cancelar
              </Button>
              <Button variant="primary" type="submit" disabled={state.saving}>
                {state.saving ? 'Guardando...' : 'Crear comanda'}
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Fecha" required error={state.fieldErrors.fecha}>
              <DateInput
                value={state.fecha}
                onChange={(value) => updateField('fecha', value)}
                required
              />
            </Field>

            <Field label="Hora" required error={state.fieldErrors.hora}>
              <Input
                type="time"
                value={state.hora}
                onChange={(event) => updateField('hora', event.target.value)}
                required
              />
            </Field>

            <Field
              label="Mesa"
              required
              hint="Número de mesa."
              error={state.fieldErrors.mesa_id}
            >
              <Input
                type="number"
                min={1}
                value={state.mesaId}
                onChange={(event) => updateField('mesaId', event.target.value)}
                required
              />
            </Field>

            <Field
              label="Mozo"
              required
              hint="Número de mozo."
              error={state.fieldErrors.mozo_id}
            >
              <Input
                type="number"
                min={1}
                value={state.mozoId}
                onChange={(event) => updateField('mozoId', event.target.value)}
                required
              />
            </Field>

            <Field
              label="Cliente"
              hint="Opcional. Número de cliente."
              error={state.fieldErrors.cliente_id}
            >
              <Input
                type="number"
                min={1}
                value={state.clienteId}
                onChange={(event) => updateField('clienteId', event.target.value)}
              />
            </Field>

            <Field
              label="Reserva"
              hint="Opcional. Número de reserva."
              error={state.fieldErrors.reserva_id}
            >
              <Input
                type="number"
                min={1}
                value={state.reservaId}
                onChange={(event) => updateField('reservaId', event.target.value)}
              />
            </Field>
          </div>

          <p className="hint">Después de crear la comanda vas a poder agregar sus productos.</p>
        </Card>
      </form>
    </>
  )
}
