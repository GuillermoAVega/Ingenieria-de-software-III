import { Alert, Button, Field, Input, KeyValue, Modal, Select } from '../../../ui/ui'
import type { ApiFieldErrors } from '../../../api/client'
import { formatCurrency } from '../../../utils/format'
import type { PaymentMethod } from '../../payment-methods/types'
import type { PaymentFormField } from '../usePaymentVouchers'

export type PaymentVoucherModalProps = {
  open: boolean
  methods: PaymentMethod[]
  medioPagoId: string
  importe: string
  balance: number
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
  onChange: (field: PaymentFormField, value: string) => void
  onSubmit: () => void
  onClose: () => void
}

export function PaymentVoucherModal({
  open,
  methods,
  medioPagoId,
  importe,
  balance,
  saving,
  error,
  fieldErrors,
  onChange,
  onSubmit,
  onClose,
}: PaymentVoucherModalProps) {
  return (
    <Modal
      open={open}
      title="Registrar pago"
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={onSubmit} disabled={saving}>
            {saving ? 'Registrando...' : 'Registrar pago'}
          </Button>
        </>
      }
    >
      {error && (
        <Alert tone="danger" title="No se pudo registrar el pago">
          {error}
        </Alert>
      )}
      {methods.length === 0 && (
        <Alert tone="warning" title="No hay medios de pago">
          Cargá al menos un medio de pago en la sección Medios de pago para poder cobrar.
        </Alert>
      )}
      <KeyValue label="Saldo pendiente" value={formatCurrency(balance)} total />
      <Field label="Medio de pago" required error={fieldErrors.medioPagoId}>
        <Select value={medioPagoId} onChange={(event) => onChange('medioPagoId', event.target.value)}>
          <option value="">Elegí un medio de pago</option>
          {methods.map((method) => (
            <option key={method.id} value={method.id}>
              {method.descripcion}
            </option>
          ))}
        </Select>
      </Field>
      <Field label="Importe" required hint="Podés pagar de a partes: hasta el saldo pendiente." error={fieldErrors.importe}>
        <Input
          type="number"
          min={0}
          step="0.01"
          value={importe}
          onChange={(event) => onChange('importe', event.target.value)}
        />
      </Field>
    </Modal>
  )
}
