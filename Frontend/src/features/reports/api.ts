import { apiFetch } from '../../api/client'
import type { SalesCountResponse } from './types'

export function getSalesCount(year: number): Promise<SalesCountResponse> {
  return apiFetch<SalesCountResponse>(`/reportes/ventas/cantidad?anio=${year}`)
}
