/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de platos
 * La lógica del formulario vive en `useProductForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, Field, Input, InputGroup, PageHeader, Select, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useProductForm } from './useProductForm'

export function ProductFormPage({ id }: { id?: string }) {
  return <ProductForm key={id ?? 'nuevo'} id={id} />
}

function ProductForm({ id }: { id?: string }) {
  const { state, isEditing, isDemo, updateField, submit } = useProductForm(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar plato' : 'Nuevo plato'}
        subtitle="Completá los datos que se van a mostrar en la carta."
      />

      {isDemo && (
        <Alert tone="warning" title="Datos de demostración">
          Este plato no existe en la API. Al guardar se creará un plato nuevo.
        </Alert>
      )}

      {state.error && (
        <Alert tone="danger" title="No se pudo guardar el plato">
          {state.error}
        </Alert>
      )}

      {state.loading ? (
        <Card>
          <p className="muted">Cargando plato...</p>
        </Card>
      ) : (
        <form onSubmit={submit}>
          <Card
            footer={
              <>
                <Button onClick={() => navigate('/productos')} disabled={state.saving}>
                  Cancelar
                </Button>
                <Button variant="primary" type="submit" disabled={state.saving}>
                  {state.saving ? 'Guardando...' : 'Guardar plato'}
                </Button>
              </>
            }
          >
            <div className="form-grid">
              <Field label="Nombre" required error={state.fieldErrors.nombre}>
                <Input
                  value={state.nombre}
                  onChange={(event) => updateField('nombre', event.target.value)}
                  placeholder="Nombre del plato"
                  required
                />
              </Field>

              <Field
                label="Sección"
                hint="Opcional. Elegí la sección donde se muestra el plato."
                error={state.fieldErrors.seccion_id ?? state.sectionsError ?? undefined}
              >
                <Select
                  value={state.seccionId}
                  onChange={(event) => updateField('seccionId', event.target.value)}
                  disabled={state.sectionsLoading}
                >
                  <option value="">
                    {state.sectionsLoading ? 'Cargando secciones...' : 'Sin sección'}
                  </option>
                  {state.sections.map((section) => (
                    <option key={section.id} value={section.id}>
                      {section.nombre}
                    </option>
                  ))}
                </Select>
              </Field>

              <Field label="Precio" required error={state.fieldErrors.precio}>
                <InputGroup prefix="$">
                  <Input
                    type="number"
                    min={0.01}
                    step="0.01"
                    value={state.precio}
                    onChange={(event) => updateField('precio', event.target.value)}
                    placeholder="0"
                    required
                  />
                </InputGroup>
              </Field>

              <Field
                label="Cantidad de personas"
                required
                hint="Entero mayor o igual a 1."
                error={state.fieldErrors.cant_personas}
              >
                <Input
                  type="number"
                  min={1}
                  step={1}
                  value={state.cantPersonas}
                  onChange={(event) => updateField('cantPersonas', event.target.value)}
                  required
                />
              </Field>

              <Field label="Descripción" className="span-full" error={state.fieldErrors.descripcion}>
                <Textarea
                  value={state.descripcion}
                  onChange={(event) => updateField('descripcion', event.target.value)}
                  placeholder="Descripción breve del plato"
                />
              </Field>
            </div>
          </Card>
        </form>
      )}
    </>
  )
}
