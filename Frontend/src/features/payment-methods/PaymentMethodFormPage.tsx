/**
 * EQUIPO: Administración
 * FUNCIONALIDAD: Alta y edición de medios de pago
 * La lógica del formulario vive en `usePaymentMethodForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, Field, Input, PageHeader } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { usePaymentMethodForm } from './usePaymentMethodForm'

export function PaymentMethodFormPage({ id }: { id?: string }) {
  return <PaymentMethodForm key={id ?? 'nuevo'} id={id} />
}

function PaymentMethodForm({ id }: { id?: string }) {
  const { state, isEditing, updateField, submit } = usePaymentMethodForm(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar medio de pago' : 'Nuevo medio de pago'}
        subtitle="Definí la descripción con la que se registra el cobro."
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo guardar el medio de pago">
          {state.error}
        </Alert>
      )}

      {state.loading ? (
        <Card>
          <p className="muted">Cargando medio de pago...</p>
        </Card>
      ) : (
        <form onSubmit={submit}>
          <Card
            footer={
              <>
                <Button onClick={() => navigate('/medios-de-pago')} disabled={state.saving}>
                  Cancelar
                </Button>
                <Button variant="primary" type="submit" disabled={state.saving}>
                  {state.saving ? 'Guardando...' : 'Guardar medio de pago'}
                </Button>
              </>
            }
          >
            <div className="form-grid">
              <Field label="Descripción" required error={state.fieldErrors.descripcion}>
                <Input
                  value={state.descripcion}
                  onChange={(event) => updateField('descripcion', event.target.value)}
                  placeholder="Ej: Efectivo, Tarjeta de débito"
                  maxLength={100}
                  required
                />
              </Field>
            </div>
          </Card>
        </form>
      )}
    </>
  )
}
