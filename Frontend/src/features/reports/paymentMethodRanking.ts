import type { PaymentMethodUsageRow } from './types'

export function sortByImporte(rows: PaymentMethodUsageRow[]): PaymentMethodUsageRow[] {
  return [...rows].sort(
    (a, b) =>
      b.importe - a.importe ||
      b.cantidad_comprobantes - a.cantidad_comprobantes ||
      a.descripcion.localeCompare(b.descripcion, 'es'),
  )
}

export function sortByAverage(rows: PaymentMethodUsageRow[]): PaymentMethodUsageRow[] {
  return [...rows].sort(
    (a, b) =>
      b.importe_promedio - a.importe_promedio ||
      b.importe - a.importe ||
      a.descripcion.localeCompare(b.descripcion, 'es'),
  )
}
