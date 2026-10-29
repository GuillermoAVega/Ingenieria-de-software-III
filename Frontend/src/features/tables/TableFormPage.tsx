/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Alta y edición de mesas
 * COMPLETAR:
 * 1. Reemplazar DEMO_TABLES y DEMO_SECTORS por la carga desde la API.
 * 2. Validar la capacidad y el estado de la mesa.
 * 3. Guardar la mesa contra la API.
 */
import { Button, Card, Field, Input, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_SECTORS, DEMO_TABLES } from './demo'

export function TableFormPage({ id }: { id?: string }) {
  const table = id ? DEMO_TABLES.find((candidate) => candidate.id === id) : undefined
  const isEditing = Boolean(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar mesa' : 'Nueva mesa'}
        subtitle="Asigná la mesa a un sector y definí su capacidad."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-salon): guardar la mesa en la API.
        }}
      >
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/mesas')}>Cancelar</Button>
              <Button variant="primary" type="submit">
                Guardar mesa
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Sector" required>
              <Select defaultValue={table?.sectorId ?? ''}>
                <option value="">Seleccioná un sector</option>
                {DEMO_SECTORS.map((sector) => (
                  <option key={sector.id} value={sector.id}>
                    {sector.name}
                  </option>
                ))}
              </Select>
            </Field>

            <Field label="Número" required>
              <Input defaultValue={table?.number ?? ''} placeholder="Mesa 1" />
            </Field>

            <Field label="Personas" required>
              <Input type="number" min={1} defaultValue={table?.seats ?? 2} />
            </Field>

            <Field label="Estado">
              <Select defaultValue={table?.status ?? 'disponible'}>
                <option value="disponible">Disponible</option>
                <option value="ocupada">Ocupada</option>
                <option value="reservada">Reservada</option>
              </Select>
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
