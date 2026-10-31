/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de secciones
 * La lógica del formulario vive en `useSectionForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, Field, Input, PageHeader, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useSectionForm } from './useSectionForm'

export function SectionFormPage({ id }: { id?: string }) {
  return <SectionForm key={id ?? 'nueva'} id={id} />
}

function SectionForm({ id }: { id?: string }) {
  const { state, isEditing, isDemo, updateField, submit } = useSectionForm(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar sección' : 'Nueva sección'}
        subtitle="Definí el nombre, el subtítulo y el orden de la sección."
      />

      {isDemo && (
        <Alert tone="warning" title="Datos de demostración">
          Esta sección no existe en la API. Al guardar se creará una sección nueva.
        </Alert>
      )}

      {state.error && (
        <Alert tone="danger" title="No se pudo guardar la sección">
          {state.error}
        </Alert>
      )}

      {state.loading ? (
        <Card>
          <p className="muted">Cargando sección...</p>
        </Card>
      ) : (
        <form onSubmit={submit}>
          <Card
            footer={
              <>
                <Button onClick={() => navigate('/secciones')} disabled={state.saving}>
                  Cancelar
                </Button>
                <Button variant="primary" type="submit" disabled={state.saving}>
                  {state.saving ? 'Guardando...' : 'Guardar sección'}
                </Button>
              </>
            }
          >
            <div className="form-grid">
              <Field label="Nombre" required error={state.fieldErrors.nombre}>
                <Input
                  value={state.nombre}
                  onChange={(event) => updateField('nombre', event.target.value)}
                  placeholder="Nombre de la sección"
                  required
                />
              </Field>

              <Field
                label="Posición"
                required
                hint="Entero mayor o igual a 1."
                error={state.fieldErrors.posicion}
              >
                <Input
                  type="number"
                  min={1}
                  step={1}
                  value={state.posicion}
                  onChange={(event) => updateField('posicion', event.target.value)}
                  required
                />
              </Field>

              <Field label="Subtítulo" className="span-full" error={state.fieldErrors.subtitulo}>
                <Textarea
                  value={state.subtitulo}
                  onChange={(event) => updateField('subtitulo', event.target.value)}
                  placeholder="Descripción breve de la sección"
                />
              </Field>
            </div>
          </Card>
        </form>
      )}
    </>
  )
}
