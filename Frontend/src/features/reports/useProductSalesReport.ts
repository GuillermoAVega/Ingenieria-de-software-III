import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { getProductSalesReport } from './api'
import type { ProductSalesReport } from './types'

export const PRODUCT_SALES_LIMITS = [5, 10, 20] as const

type ProductSalesReportState = {
  desde: string
  hasta: string
  limite: number
  data: ProductSalesReport | null
  loading: boolean
  error: string | null
}

function localDateToIso(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function getInitialPeriod(): Pick<ProductSalesReportState, 'desde' | 'hasta'> {
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  return { desde: localDateToIso(firstDay), hasta: localDateToIso(today) }
}

function getPeriodError(desde: string, hasta: string): string | null {
  if (!desde || !hasta) return 'Seleccioná ambas fechas para consultar el reporte.'
  if (desde > hasta) return 'La fecha Desde debe ser anterior o igual a la fecha Hasta.'
  return null
}

export function useProductSalesReport() {
  const [state, setState] = useState<ProductSalesReportState>(() => ({
    ...getInitialPeriod(),
    limite: 10,
    data: null,
    loading: true,
    error: null,
  }))

  useEffect(() => {
    let cancelled = false

    async function loadReport() {
      try {
        const data = await getProductSalesReport(state.desde, state.hasta, state.limite)
        if (!cancelled) setState((previous) => ({ ...previous, data, loading: false, error: null }))
      } catch (requestError) {
        if (!cancelled) {
          setState((previous) => ({
            ...previous,
            data: null,
            loading: false,
            error: getErrorMessage(requestError),
          }))
        }
      }
    }

    if (state.desde && state.hasta && state.desde <= state.hasta) void loadReport()

    return () => {
      cancelled = true
    }
  }, [state.desde, state.hasta, state.limite])

  const updateDesde = (desde: string) =>
    setState((previous) => {
      const error = getPeriodError(desde, previous.hasta)
      return { ...previous, desde, data: null, loading: !error, error }
    })

  const updateHasta = (hasta: string) =>
    setState((previous) => {
      const error = getPeriodError(previous.desde, hasta)
      return { ...previous, hasta, data: null, loading: !error, error }
    })

  const updateLimite = (limite: number) =>
    setState((previous) => ({ ...previous, limite, data: null, loading: !previous.error }))

  const rows = state.data?.productos ?? []
  const totalUnits = rows.reduce((total, row) => total + row.unidades, 0)
  const totalAmount = rows.reduce((total, row) => total + row.importe, 0)
  const maxUnits = rows.reduce((max, row) => Math.max(max, row.unidades), 0)

  return { state, rows, totalUnits, totalAmount, maxUnits, updateDesde, updateHasta, updateLimite }
}
