import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { getSalesComparison } from './api'
import type { SalesComparisonReport } from './types'

type SalesComparisonState = {
  anio: number
  mes: number
  report: SalesComparisonReport | null
  loading: boolean
  error: string | null
}

const now = new Date()

const initialState: SalesComparisonState = {
  anio: now.getFullYear(),
  mes: now.getMonth() + 1,
  report: null,
  loading: true,
  error: null,
}

export function useSalesComparison() {
  const [state, setState] = useState<SalesComparisonState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadReport() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const report = await getSalesComparison({ anio: state.anio, mes: state.mes })
        if (cancelled) return
        setState((previous) => ({ ...previous, report, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          report: null,
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadReport()

    return () => {
      cancelled = true
    }
  }, [state.anio, state.mes])

  const updateAnio = (anio: number) => {
    setState((previous) => ({ ...previous, anio }))
  }

  const updateMes = (mes: number) => {
    setState((previous) => ({ ...previous, mes }))
  }

  return { state, updateAnio, updateMes }
}
