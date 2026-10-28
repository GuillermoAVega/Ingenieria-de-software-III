/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Alta y edición de mozos
 * COMPLETAR:
 * 1. Reemplazar DEMO_WAITERS por la carga desde la API.
 * 2. Validar teléfono y email.
 * 3. Guardar el mozo contra la API.
 */
import { Button, Card, Field, Input, PageHeader, Switch } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_WAITERS } from './demo'

export function WaiterFormPage({ id }: { id?: string }) {
  const waiter = id ? DEMO_WAITERS.find((candidate) => candidate.id === id) : undefined
  const isEditing = Boolean(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar mozo' : 'Nuevo mozo'}
        subtitle="Completá los datos de contacto y el estado del mozo."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-salon): guardar el mozo en la API.
        }}
      >
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/mozos')}>Cancelar</Button>
              <Button variant="primary" type="submit">
                Guardar mozo
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Nombre" required>
              <Input defaultValue={waiter?.name ?? ''} placeholder="Nombre y apellido" />
            </Field>

            <Field label="Teléfono" required>
              <Input defaultValue={waiter?.phone ?? ''} placeholder="280 455-0000" />
            </Field>

            <Field label="Email" required>
              <Input type="email" defaultValue={waiter?.email ?? ''} placeholder="nombre@resto.local" />
            </Field>

            <Field label="Activo" className="span-full">
              <Switch defaultChecked={waiter?.status !== 'inactivo'}>El mozo está activo</Switch>
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
