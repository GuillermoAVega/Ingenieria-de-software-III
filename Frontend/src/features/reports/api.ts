import { apiFetch } from '../../api/client'
import type { SalesComparisonParams, SalesComparisonReport } from './types'

export function getSalesComparison({
  anio,
  mes,
}: SalesComparisonParams): Promise<SalesComparisonReport> {
  const params = new URLSearchParams({ anio: String(anio), mes: String(mes) })
  return apiFetch<SalesComparisonReport>(`/reportes/ventas-comparativa?${params}`)
}
