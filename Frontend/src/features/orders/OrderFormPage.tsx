/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Alta de comanda
 * COMPLETAR:
 * 1. Cargar mesas, mozos y reservas desde la API.
 * 2. Implementar el selector de productos y el cálculo de totales.
 * 3. Guardar la comanda contra la API.
 */
import { Button, Card, EmptyState, Field, Input, PageHeader, Select, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_RESERVATIONS } from '../reservations/demo'
import { DEMO_SECTORS, DEMO_TABLES } from '../tables/demo'
import { DEMO_WAITERS } from '../waiters/demo'

export function OrderFormPage() {
  return (
    <>
      <PageHeader
        title="Nueva comanda"
        subtitle="Cargá la mesa, el mozo y los productos que forman parte del pedido."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-operacion): crear la comanda en la API.
        }}
      >
        <div className="stack">
          <Card title="Datos de la comanda">
            <div className="form-grid">
              <Field label="Mesa" required>
                <Select defaultValue="">
                  <option value="">Seleccioná una mesa</option>
                  {DEMO_SECTORS.map((sector) => (
                    <optgroup key={sector.id} label={sector.name}>
                      {DEMO_TABLES.filter((table) => table.sectorId === sector.id).map((table) => (
                        <option key={table.id} value={table.id}>
                          {table.number} · {table.seats} personas
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </Select>
              </Field>

              <Field label="Mozo" required>
                <Select defaultValue="">
                  <option value="">Seleccioná un mozo</option>
                  {DEMO_WAITERS.map((waiter) => (
                    <option key={waiter.id} value={waiter.id}>
                      {waiter.name}
                    </option>
                  ))}
                </Select>
              </Field>

              <Field label="Cliente">
                <Input placeholder="Nombre del cliente" />
              </Field>

              <Field label="Reserva">
                <Select defaultValue="">
                  <option value="">Sin reserva asociada</option>
                  {DEMO_RESERVATIONS.map((reservation) => (
                    <option key={reservation.id} value={reservation.id}>
                      {reservation.time} · {reservation.customer}
                    </option>
                  ))}
                </Select>
              </Field>

              <Field label="Notas" className="span-full">
                <Textarea placeholder="Observaciones de la comanda" />
              </Field>
            </div>
          </Card>

          <Card
            title="Productos de la comanda"
            footer={
              <>
                <Button onClick={() => navigate('/comandas')}>Cancelar</Button>
                <Button variant="primary" type="submit">
                  Guardar comanda
                </Button>
              </>
            }
          >
            <EmptyState
              title="Todavía no agregaste productos"
              action={
                <Button
                  variant="secondary"
                  onClick={() => {
                    // TODO(equipo-operacion): abrir el selector de productos de la carta.
                  }}
                >
                  Agregar producto
                </Button>
              }
            >
              Buscá productos de la carta para sumarlos a la comanda.
            </EmptyState>
          </Card>
        </div>
      </form>
    </>
  )
}
