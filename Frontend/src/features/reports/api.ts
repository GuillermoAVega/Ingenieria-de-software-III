import { apiFetch } from '../../api/client'
import type {
  ProductSalesReport,
  SalesComparisonParams,
  SalesComparisonReport,
  SalesCountResponse,
  WaiterOrderReport,
} from './types'

export function getSalesComparison({
  anio,
  mes,
}: SalesComparisonParams): Promise<SalesComparisonReport> {
  const params = new URLSearchParams({ anio: String(anio), mes: String(mes) })
  return apiFetch<SalesComparisonReport>(`/reportes/ventas-comparativa?${params}`)
}

export function getSalesCount(year: number): Promise<SalesCountResponse> {
  return apiFetch<SalesCountResponse>(`/reportes/ventas/cantidad?anio=${year}`)
}

export function getWaiterOrderReport(desde: string, hasta: string): Promise<WaiterOrderReport> {
  const params = new URLSearchParams({ desde, hasta })
  return apiFetch<WaiterOrderReport>(`/reportes/comandas-por-mozo?${params}`)
}

export function getProductSalesReport(
  desde: string,
  hasta: string,
  limite: number,
): Promise<ProductSalesReport> {
  const params = new URLSearchParams({ desde, hasta, limite: String(limite) })
  return apiFetch<ProductSalesReport>(`/reportes/productos-mas-vendidos?${params}`)
}
