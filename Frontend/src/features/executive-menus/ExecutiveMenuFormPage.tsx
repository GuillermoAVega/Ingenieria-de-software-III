/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de menús ejecutivos
 * La lógica del formulario vive en `useExecutiveMenuForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, Field, Input, PageHeader, Select, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useExecutiveMenuForm } from './useExecutiveMenuForm'

export function ExecutiveMenuFormPage({ id }: { id?: string }) {
  return <ExecutiveMenuForm key={id ?? 'nuevo'} id={id} />
}

function ExecutiveMenuForm({ id }: { id?: string }) {
  const { state, isEditing, updateField, submit } = useExecutiveMenuForm(id)

  const sinComponentes =
    !state.loading && (state.platos.length === 0 || state.postres.length === 0)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar menú ejecutivo' : 'Nuevo menú ejecutivo'}
        subtitle="Elegí el plato y el postre que componen el menú, y definí su precio."
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {state.error}
        </Alert>
      )}

      {sinComponentes && (
        <Alert tone="warning" title="Faltan componentes activos">
          Necesitás al menos un plato y un postre activos en la carta para crear un menú ejecutivo.
        </Alert>
      )}

      {state.loading ? (
        <Card>
          <p className="muted">Cargando menú ejecutivo...</p>
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
                  disabled={state.saving || state.loading || sinComponentes}
                >
                  {state.saving ? 'Guardando...' : 'Guardar menú ejecutivo'}
                </Button>
              </>
            }
          >
            <div className="form-grid">
              <Field label="Nombre" required error={state.fieldErrors.nombre}>
                <Input
                  value={state.nombre}
                  onChange={(event) => updateField('nombre', event.target.value)}
                  placeholder="Menú ejecutivo del mediodía"
                  required
                />
              </Field>

              <Field
                label="Precio"
                required
                hint="Precio propio del menú, independiente de sus componentes."
                error={state.fieldErrors.precio}
              >
                <Input
                  type="number"
                  min={0}
                  step="0.01"
                  value={state.precio}
                  onChange={(event) => updateField('precio', event.target.value)}
                  required
                />
              </Field>

              <Field label="Plato" required error={state.fieldErrors.plato_id}>
                <Select
                  value={state.platoId}
                  onChange={(event) => updateField('platoId', event.target.value)}
                  required
                >
                  <option value="">Elegí un plato</option>
                  {state.platos.map((plato) => (
                    <option key={plato.id} value={plato.id}>
                      {plato.nombre}
                    </option>
                  ))}
                </Select>
              </Field>

              <Field label="Postre" required error={state.fieldErrors.postre_id}>
                <Select
                  value={state.postreId}
                  onChange={(event) => updateField('postreId', event.target.value)}
                  required
                >
                  <option value="">Elegí un postre</option>
                  {state.postres.map((postre) => (
                    <option key={postre.id} value={postre.id}>
                      {postre.nombre}
                    </option>
                  ))}
                </Select>
              </Field>

              <Field label="Sección" error={state.fieldErrors.seccion_id}>
                <Select
                  value={state.seccionId}
                  onChange={(event) => updateField('seccionId', event.target.value)}
                >
                  <option value="">Sin sección</option>
                  {state.sections.map((section) => (
                    <option key={section.id} value={section.id}>
                      {section.nombre}
                    </option>
                  ))}
                </Select>
              </Field>

              <Field label="Descripción" className="span-full" error={state.fieldErrors.descripcion}>
                <Textarea
                  value={state.descripcion}
                  onChange={(event) => updateField('descripcion', event.target.value)}
                  placeholder="Detalle del menú ejecutivo"
                />
              </Field>
            </div>
          </Card>
        </form>
      )}
    </>
  )
}
