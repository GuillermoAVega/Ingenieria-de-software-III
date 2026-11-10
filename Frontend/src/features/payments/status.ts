import type { BadgeTone } from '../../ui/ui'
import { toCents } from './money'
import type { PaymentStatus } from './types'

export const PAYMENT_STATUS_LABEL: Record<PaymentStatus, string> = {
  pagada: 'Pagada',
  parcial: 'Pago parcial',
  sin_pagar: 'Sin pagar',
}

export const PAYMENT_STATUS_TONE: Record<PaymentStatus, BadgeTone> = {
  pagada: 'success',
  parcial: 'warning',
  sin_pagar: 'neutral',
}

export function getPaymentStatus(total: number, paid: number): PaymentStatus {
  const totalCents = toCents(total)
  const paidCents = toCents(paid)
  if (paidCents <= 0) return 'sin_pagar'
  return paidCents >= totalCents ? 'pagada' : 'parcial'
}
