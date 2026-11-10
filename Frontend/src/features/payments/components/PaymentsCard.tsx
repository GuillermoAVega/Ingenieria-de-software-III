import { Alert, Badge, Button, Card, DeleteButton, KeyValue } from '../../../ui/ui'
import { formatCurrency, formatDateTime } from '../../../utils/format'
import { PAYMENT_STATUS_LABEL, PAYMENT_STATUS_TONE } from '../status'
import type { PaymentStatus, PaymentVoucherRow } from '../types'

export type PaymentsCardProps = {
  rows: PaymentVoucherRow[]
  total: number
  paid: number
  balance: number
  status: PaymentStatus
  loading: boolean
  error: string | null
  deletingId: number | null
  onRegister: () => void
  onRemove: (id: number) => void
}

export function PaymentsCard({
  rows,
  total,
  paid,
  balance,
  status,
  loading,
  error,
  deletingId,
  onRegister,
  onRemove,
}: PaymentsCardProps) {
  return (
    <Card
      title="Pagos"
      actions={<Badge tone={PAYMENT_STATUS_TONE[status]}>{PAYMENT_STATUS_LABEL[status]}</Badge>}
    >
      {error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {error}
        </Alert>
      )}

      {loading ? (
        <p className="muted">Cargando pagos...</p>
      ) : (
        <>
          <KeyValue label="Total" value={formatCurrency(total)} />
          <KeyValue label="Pagado" value={formatCurrency(paid)} />
          <KeyValue label="Saldo" value={formatCurrency(balance)} total />

          {rows.length === 0 ? (
            <p className="hint">Todavía no se registró ningún pago.</p>
          ) : (
            rows.map((voucher) => (
              <div className="row" key={voucher.id}>
                <KeyValue
                  label={
                    <span>
                      {voucher.medioPagoNombre}
                      <small className="muted"> · {formatDateTime(voucher.fecha_hora_emision)}</small>
                    </span>
                  }
                  value={formatCurrency(voucher.importe)}
                />
                <DeleteButton
                  label="Anular"
                  title="Anular pago"
                  confirmLabel="Anular pago"
                  onConfirm={() => {
                    onRemove(voucher.id)
                  }}
                >
                  ¿Querés anular el pago de <strong>{formatCurrency(voucher.importe)}</strong> con{' '}
                  {voucher.medioPagoNombre}? El importe vuelve al saldo pendiente.
                </DeleteButton>
              </div>
            ))
          )}

          <Button
            variant="primary"
            block
            disabled={balance <= 0 || deletingId !== null}
            onClick={onRegister}
          >
            {balance <= 0 ? 'Factura pagada' : 'Registrar pago'}
          </Button>
        </>
      )}
    </Card>
  )
}
