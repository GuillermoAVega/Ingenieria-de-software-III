import type { Invoice } from '../orders/types'
import type { PaymentStatus } from '../payments/types'

export type BillingRow = Invoice & {
  paid: number
  paymentStatus: PaymentStatus
}
