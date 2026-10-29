export type InvoiceStatus = 'emitida' | 'anulada' | 'pendiente'

export type Invoice = {
  id: string
  number: string
  issuedAt: string
  customer: string
  orderId: string
  paymentMethod: string
  total: number
  status: InvoiceStatus
}
