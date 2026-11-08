/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de un menú del día
 * La lógica del formulario vive en `useDailyMenuForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, DateInput, Field, Input, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { getTodayInputValue, useDailyMenuForm } from './useDailyMenuForm'

export function DailyMenuFormPage({ id }: { id?: string }) {
  return <DailyMenuForm key={id ?? 'nuevo'} id={id} />
}

function DailyMenuForm({ id }: { id?: string }) {
  const { state, isEditing, updateField, submit } = useDailyMenuForm(id)

  const sinMenus = !isEditing && !state.menusDelDiaLoading && state.menusDelDia.length === 0
  const menuInactivo = state.registro?.menu_del_dia_dado_de_baja ?? false

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar asignación de menú del día' : 'Asignar menú del día'}
        subtitle={
          isEditing
            ? 'Cambiá la fecha de la asignación. El menú del día asociado no se puede modificar.'
            : 'Elegí una fecha y el menú del día que se ofrece ese día.'
        }
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {state.error}
        </Alert>
      )}

      {sinMenus && (
        <Alert tone="warning" title="No hay menús del día activos">
          Creá un menú del día en Productos antes de asignarlo a una fecha.
        </Alert>
      )}

      {menuInactivo && (
        <Alert tone="warning" title="El menú del día está dado de baja">
          Podés eliminarlo, pero no cambiarle la fecha mientras esté dado de baja.
        </Alert>
      )}

      {state.loading ? (
        <Card>
          <p className="muted">Cargando menú del día...</p>
        </Card>
      ) : (
        <form onSubmit={submit} noValidate>
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
                    state.saving || state.loading || sinMenus || (!isEditing && state.menusDelDiaLoading)
                  }
                >
                  {state.saving ? 'Guardando...' : 'Guardar asignación'}
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
                <DateInput
                  min={getTodayInputValue()}
                  value={state.fecha}
                  invalid={Boolean(state.fieldErrors.fecha)}
                  onChange={(value) => updateField('fecha', value)}
                  disabled={state.saving}
                  required
                />
              </Field>

              {isEditing ? (
                <Field label="Menú del día" hint="El menú del día no se puede cambiar.">
                  <Input
                    value={state.registro?.menu_del_dia_nombre ?? '—'}
                    readOnly
                    disabled
                  />
                </Field>
              ) : (
                <Field
                  label="Menú del día"
                  required
                  hint="Sólo se listan los menús del día activos."
                  error={state.fieldErrors.menu_del_dia_id}
                >
                  <Select
                    value={state.menuDelDiaId}
                    onChange={(event) => updateField('menuDelDiaId', event.target.value)}
                    disabled={state.saving || state.menusDelDiaLoading || sinMenus}
                    required
                  >
                    <option value="">
                      {state.menusDelDiaLoading ? 'Cargando menús del día...' : 'Elegí un menú del día'}
                    </option>
                    {state.menusDelDia.map((menu) => (
                      <option key={menu.id} value={menu.id}>
                        {menu.nombre}
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
