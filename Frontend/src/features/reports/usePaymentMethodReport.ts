import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { getPaymentMethodReport } from './api'
import { sortByAverage, sortByImporte } from './paymentMethodRanking'
import type { PaymentMethodReport } from './types'

type PaymentMethodReportState = {
  desde: string
  hasta: string
  data: PaymentMethodReport | null
  loading: boolean
  error: string | null
}

function localDateToIso(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function getInitialPeriod(): Pick<PaymentMethodReportState, 'desde' | 'hasta'> {
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  return { desde: localDateToIso(firstDay), hasta: localDateToIso(today) }
}

function getPeriodError(desde: string, hasta: string): string | null {
  if (!desde || !hasta) return 'Seleccioná ambas fechas para consultar el reporte.'
  if (desde > hasta) return 'La fecha Desde debe ser anterior o igual a la fecha Hasta.'
  return null
}

export function usePaymentMethodReport() {
  const [state, setState] = useState<PaymentMethodReportState>(() => ({
    ...getInitialPeriod(),
    data: null,
    loading: true,
    error: null,
  }))

  useEffect(() => {
    let cancelled = false

    async function loadReport() {
      try {
        const data = await getPaymentMethodReport(state.desde, state.hasta)
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
  }, [state.desde, state.hasta])

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

  const rows = state.data?.medios ?? []

  return {
    state,
    rows,
    rowsByImporte: sortByImporte(rows),
    rowsByPromedio: sortByAverage(rows),
    updateDesde,
    updateHasta,
  }
}
