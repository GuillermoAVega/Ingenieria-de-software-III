/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de secciones
 * COMPLETAR:
 * 1. Reemplazar DEMO_SECTIONS por la carga desde la API.
 * 2. Validar que el nombre de la sección no se repita.
 * 3. Guardar la sección contra la API.
 */
import { Button, Card, Field, Input, PageHeader, Select, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_SECTIONS } from './demo'

export function SectionFormPage({ id }: { id?: string }) {
  const section = id ? DEMO_SECTIONS.find((candidate) => candidate.id === id) : undefined
  const isEditing = Boolean(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar sección' : 'Nueva sección'}
        subtitle="Definí el nombre, la ubicación y las condiciones de la sección."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-carta): guardar la sección en la API.
        }}
      >
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/secciones')}>Cancelar</Button>
              <Button variant="primary" type="submit">
                Guardar sección
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Nombre" required>
              <Input defaultValue={section?.name ?? ''} placeholder="Nombre de la sección" />
            </Field>

            <Field label="Planta">
              <Select defaultValue={section?.floor ?? 'Planta baja'}>
                <option value="Planta baja">Planta baja</option>
                <option value="Planta alta">Planta alta</option>
                <option value="Terraza">Terraza</option>
              </Select>
            </Field>

            <Field label="Condición">
              <Select defaultValue={section?.condition ?? 'No fumadores'}>
                <option value="No fumadores">No fumadores</option>
                <option value="Apto fumadores">Apto fumadores</option>
              </Select>
            </Field>

            <Field label="Descripción" className="span-full">
              <Textarea
                defaultValue={section?.description ?? ''}
                placeholder="Descripción breve de la sección"
              />
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
