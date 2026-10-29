/**
 * EQUIPO: Administración
 * FUNCIONALIDAD: Alta y edición de medios de pago
 * COMPLETAR:
 * 1. Reemplazar DEMO_PAYMENT_METHODS por la carga desde la API.
 * 2. Validar el recargo y la unicidad del nombre.
 * 3. Guardar el medio de pago contra la API.
 */
import { Button, Card, Field, Input, PageHeader, Select, Switch } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_PAYMENT_METHODS } from './demo'

export function PaymentMethodFormPage({ id }: { id?: string }) {
  const method = id ? DEMO_PAYMENT_METHODS.find((candidate) => candidate.id === id) : undefined
  const isEditing = Boolean(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar medio de pago' : 'Nuevo medio de pago'}
        subtitle="Definí el nombre, el tipo y el recargo que se aplica al cobrar."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-administracion): guardar el medio de pago en la API.
        }}
      >
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/medios-de-pago')}>Cancelar</Button>
              <Button variant="primary" type="submit">
                Guardar medio de pago
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Nombre" required>
              <Input defaultValue={method?.name ?? ''} placeholder="Nombre del medio de pago" />
            </Field>

            <Field label="Tipo" required>
              <Select defaultValue={method?.type ?? 'Efectivo'}>
                <option value="Efectivo">Efectivo</option>
                <option value="Tarjeta">Tarjeta</option>
                <option value="Transferencia">Transferencia</option>
                <option value="Otro">Otro</option>
              </Select>
            </Field>

            <Field label="Recargo (%)" hint="Porcentaje que se suma al total.">
              <Input type="number" min={0} defaultValue={method?.surcharge ?? 0} placeholder="0" />
            </Field>

            <Field label="Activo" className="span-full">
              <Switch defaultChecked={method?.active ?? true}>El medio de pago está activo</Switch>
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
