/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Alta y edición de clientes
 * COMPLETAR:
 * 1. Reemplazar DEMO_CUSTOMERS por la carga desde la API.
 * 2. Validar teléfono y email, y detectar clientes duplicados.
 * 3. Guardar el cliente contra la API.
 */
import { Button, Card, Field, Input, PageHeader, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_CUSTOMERS } from './demo'

export function CustomerFormPage({ id }: { id?: string }) {
  const customer = id ? DEMO_CUSTOMERS.find((candidate) => candidate.id === id) : undefined
  const isEditing = Boolean(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar cliente' : 'Nuevo cliente'}
        subtitle="Completá los datos de contacto para futuras reservas y comandas."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-salon): guardar el cliente en la API.
        }}
      >
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/clientes')}>Cancelar</Button>
              <Button variant="primary" type="submit">
                Guardar cliente
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Nombre" required>
              <Input defaultValue={customer?.name ?? ''} placeholder="Nombre y apellido" />
            </Field>

            <Field label="Teléfono" required>
              <Input defaultValue={customer?.phone ?? ''} placeholder="280 455-0000" />
            </Field>

            <Field label="Email">
              <Input type="email" defaultValue={customer?.email ?? ''} placeholder="nombre@example.com" />
            </Field>

            <Field label="Notas" className="span-full">
              <Textarea placeholder="Preferencias, alergias u observaciones" />
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
