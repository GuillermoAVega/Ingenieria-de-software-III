/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta de un menú del día
 * La lógica del formulario vive en `useDailyMenuForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, Field, Input, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useDailyMenuForm } from './useDailyMenuForm'

export function DailyMenuFormPage() {
  const { state, updateField, submit, reset } = useDailyMenuForm()

  const platoCreado = state.platos.find((plato) => plato.id === state.created?.producto_id)
  const sinPlatos = !state.loading && state.platos.length === 0

  return (
    <>
      <PageHeader
        title="Nuevo menú del día"
        subtitle="Elegí una fecha y el plato que se ofrece como menú ese día."
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {state.error}
        </Alert>
      )}

      {state.created && (
        <Alert tone="success" title="Menú del día creado">
          <p className="muted">
            {platoCreado?.nombre ?? `Plato #${state.created.producto_id}`} · {state.created.fecha}
          </p>
          <div className="row">
            <Button onClick={reset}>Crear otro</Button>
            <Button variant="primary" onClick={() => navigate('/productos')}>
              Volver a productos
            </Button>
          </div>
        </Alert>
      )}

      {sinPlatos && (
        <Alert tone="warning" title="No hay platos activos">
          Cargá un plato en la carta antes de crear un menú del día.
        </Alert>
      )}

      <form onSubmit={submit}>
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/productos')} disabled={state.saving}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                type="submit"
                disabled={state.saving || state.loading || sinPlatos}
              >
                {state.saving ? 'Guardando...' : 'Guardar menú del día'}
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field
              label="Fecha"
              required
              hint="La fecha de hoy viene seleccionada por defecto. Una fecha sólo admite un menú."
              error={state.fieldErrors.fecha}
            >
              <Input
                type="date"
                value={state.fecha}
                onChange={(event) => updateField('fecha', event.target.value)}
                disabled={state.saving}
                required
              />
            </Field>

            <Field
              label="Plato"
              required
              hint="Sólo se listan los platos activos de la carta."
              error={state.fieldErrors.producto_id}
            >
              <Select
                value={state.productoId}
                onChange={(event) => updateField('productoId', event.target.value)}
                disabled={state.loading || state.saving || sinPlatos}
                required
              >
                <option value="">{state.loading ? 'Cargando platos...' : 'Elegí un plato'}</option>
                {state.platos.map((plato) => (
                  <option key={plato.id} value={plato.id}>
                    {plato.nombre}
                  </option>
                ))}
              </Select>
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
