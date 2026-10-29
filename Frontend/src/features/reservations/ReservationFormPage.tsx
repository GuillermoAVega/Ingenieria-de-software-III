/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Alta y edición de reservas
 * COMPLETAR:
 * 1. Reemplazar DEMO_RESERVATIONS por la carga desde la API.
 * 2. Validar disponibilidad de mesa y comensales.
 * 3. Guardar la reserva contra la API.
 */
import { Button, Card, Field, Input, PageHeader, Select, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_TABLES } from '../tables/demo'
import { DEMO_RESERVATIONS } from './demo'

export function ReservationFormPage({ id }: { id?: string }) {
  const reservation = id ? DEMO_RESERVATIONS.find((candidate) => candidate.id === id) : undefined
  const isEditing = Boolean(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar reserva' : 'Nueva reserva'}
        subtitle={
          isEditing
            ? 'Actualizá los datos de la reserva seleccionada.'
            : 'Registrá una nueva reserva y asignale una mesa.'
        }
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-operacion): guardar la reserva en la API.
        }}
      >
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/reservas')}>Cancelar</Button>
              <Button variant="primary" type="submit">
                Guardar reserva
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Cliente" required>
              <Input defaultValue={reservation?.customer ?? ''} placeholder="Nombre y apellido" />
            </Field>

            <Field label="Teléfono" required>
              <Input defaultValue={reservation?.phone ?? ''} placeholder="280 455-0000" />
            </Field>

            <Field label="Fecha" required>
              <Input type="date" defaultValue={reservation?.date ?? '2026-10-16'} />
            </Field>

            <Field label="Hora" required>
              <Input type="time" defaultValue={reservation?.time ?? '21:00'} />
            </Field>

            <Field label="Comensales" required>
              <Input type="number" min={1} defaultValue={reservation?.guests ?? 2} />
            </Field>

            <Field label="Mesa">
              <Select defaultValue={reservation?.table ?? ''}>
                <option value="">Sin mesa asignada</option>
                {DEMO_TABLES.map((table) => (
                  <option key={table.id} value={table.number}>
                    {table.number} · {table.seats} personas
                  </option>
                ))}
              </Select>
            </Field>

            <Field label="Estado">
              <Select defaultValue={reservation?.status ?? 'confirmada'}>
                <option value="confirmada">Confirmada</option>
                <option value="con-comanda">Con comanda</option>
                <option value="cancelada">Cancelada</option>
                <option value="ausente">Ausente</option>
                <option value="pendiente">Pendiente</option>
              </Select>
            </Field>

            <Field label="Notas" className="span-full">
              <Textarea placeholder="Preferencias, ocasión especial u observaciones" />
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
