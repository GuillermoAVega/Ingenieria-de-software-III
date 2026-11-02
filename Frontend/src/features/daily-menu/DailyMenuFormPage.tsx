/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de un menú del día
 * La lógica del formulario vive en `useDailyMenuForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, Field, Input, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useDailyMenuForm } from './useDailyMenuForm'

export function DailyMenuFormPage({ id }: { id?: string }) {
  return <DailyMenuForm key={id ?? 'nuevo'} id={id} />
}

function DailyMenuForm({ id }: { id?: string }) {
  const { state, isEditing, updateField, submit } = useDailyMenuForm(id)

  const sinPlatos = !isEditing && !state.platosLoading && state.platos.length === 0
  const productoInactivo = state.producto?.producto_dado_de_baja ?? false

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar menú del día' : 'Nuevo menú del día'}
        subtitle={
          isEditing
            ? 'Cambiá la fecha del menú. El producto asociado no se puede modificar.'
            : 'Elegí una fecha y el plato que se ofrece como menú ese día.'
        }
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {state.error}
        </Alert>
      )}

      {sinPlatos && (
        <Alert tone="warning" title="No hay platos activos">
          Cargá un plato en la carta antes de crear un menú del día.
        </Alert>
      )}

      {productoInactivo && (
        <Alert tone="warning" title="El producto está dado de baja">
          Podés eliminarlo, pero no cambiarle la fecha mientras esté dado de baja.
        </Alert>
      )}

      {state.loading ? (
        <Card>
          <p className="muted">Cargando menú del día...</p>
        </Card>
      ) : (
        <form onSubmit={submit}>
          <Card
            footer={
              <>
                <Button onClick={() => navigate('/menus')} disabled={state.saving}>
                  Cancelar
                </Button>
                <Button
                  variant="primary"
                  type="submit"
                  disabled={
                    state.saving || state.loading || sinPlatos || (!isEditing && state.platosLoading)
                  }
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
                hint="Una fecha sólo admite un menú del día."
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

              {isEditing ? (
                <Field label="Plato" hint="El producto no se puede cambiar.">
                  <Input
                    value={state.producto?.producto_nombre ?? '—'}
                    readOnly
                    disabled
                  />
                </Field>
              ) : (
                <Field
                  label="Plato"
                  required
                  hint="Sólo se listan los platos activos de la carta."
                  error={state.fieldErrors.producto_id}
                >
                  <Select
                    value={state.productoId}
                    onChange={(event) => updateField('productoId', event.target.value)}
                    disabled={state.saving || state.platosLoading || sinPlatos}
                    required
                  >
                    <option value="">
                      {state.platosLoading ? 'Cargando platos...' : 'Elegí un plato'}
                    </option>
                    {state.platos.map((plato) => (
                      <option key={plato.id} value={plato.id}>
                        {plato.nombre}
                      </option>
                    ))}
                  </Select>
                </Field>
              )}
            </div>
          </Card>
        </form>
      )}
    </>
  )
}
