import type { PaymentMethod } from './types'

export const DEMO_PAYMENT_METHODS: PaymentMethod[] = [
  { id: 'payment-1', name: 'Efectivo', type: 'Efectivo', surcharge: 0, active: true },
  { id: 'payment-2', name: 'Tarjeta de débito', type: 'Tarjeta', surcharge: 0, active: true },
  { id: 'payment-3', name: 'Tarjeta de crédito', type: 'Tarjeta', surcharge: 10, active: true },
  { id: 'payment-4', name: 'Transferencia', type: 'Transferencia', surcharge: 0, active: true },
]
