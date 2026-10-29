import type { Invoice } from './types'

export const DEMO_INVOICES: Invoice[] = [
  {
    id: 'inv-1',
    number: 'A-0001-00000021',
    issuedAt: '2026-10-16 21:12',
    customer: 'Consumidor final',
    orderId: '1041',
    paymentMethod: 'Tarjeta de crédito',
    total: 52600,
    status: 'emitida',
  },
  {
    id: 'inv-2',
    number: 'A-0001-00000020',
    issuedAt: '2026-10-16 20:55',
    customer: 'Federico Luna',
    orderId: '1039',
    paymentMethod: 'Efectivo',
    total: 28700,
    status: 'emitida',
  },
  {
    id: 'inv-3',
    number: 'A-0001-00000019',
    issuedAt: '2026-10-16 20:30',
    customer: 'Valentina Ortiz',
    orderId: '1038',
    paymentMethod: 'Transferencia',
    total: 41900,
    status: 'emitida',
  },
  {
    id: 'inv-4',
    number: 'A-0001-00000018',
    issuedAt: '2026-10-16 19:45',
    customer: 'Agustina Peralta',
    orderId: '1037',
    paymentMethod: 'Tarjeta de débito',
    total: 17300,
    status: 'anulada',
  },
  {
    id: 'inv-5',
    number: 'A-0001-00000017',
    issuedAt: '2026-10-16 19:20',
    customer: 'Camilo Sosa',
    orderId: '1036',
    paymentMethod: 'Efectivo',
    total: 65040,
    status: 'emitida',
  },
]

export const DEMO_BILLING_SUMMARY = {
  totalToday: 482300,
  invoiceCount: 21,
  averageTicket: 22967,
}
