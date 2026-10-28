/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Alta y edición de sectores
 * COMPLETAR:
 * 1. Reemplazar DEMO_SECTORS por la carga desde la API.
 * 2. Validar el nombre y la capacidad del sector.
 * 3. Guardar el sector contra la API.
 */
import { Button, Card, Field, Input, PageHeader, Select, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_SECTORS } from './demo'

export function SectorFormPage({ id }: { id?: string }) {
  const sector = id ? DEMO_SECTORS.find((candidate) => candidate.id === id) : undefined
  const isEditing = Boolean(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar sector' : 'Nuevo sector'}
        subtitle="Definí el nombre, la ubicación y las condiciones del sector."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-salon): guardar el sector en la API.
        }}
      >
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/mesas')}>Cancelar</Button>
              <Button variant="primary" type="submit">
                Guardar sector
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Nombre" required>
              <Input defaultValue={sector?.name ?? ''} placeholder="Nombre del sector" />
            </Field>

            <Field label="Planta">
              <Select defaultValue={sector?.floor ?? 'Planta baja'}>
                <option value="Planta baja">Planta baja</option>
                <option value="Planta alta">Planta alta</option>
                <option value="Terraza">Terraza</option>
              </Select>
            </Field>

            <Field label="Condición">
              <Select defaultValue={sector?.condition ?? 'No fumadores'}>
                <option value="No fumadores">No fumadores</option>
                <option value="Apto fumadores">Apto fumadores</option>
              </Select>
            </Field>

            <Field label="Descripción" className="span-full">
              <Textarea
                defaultValue={sector?.description ?? ''}
                placeholder="Descripción breve del sector"
              />
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
