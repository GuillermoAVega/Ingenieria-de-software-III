import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { getSalesCount } from './api'
import type { SalesCountResponse } from './types'

type SalesCountState = {
  year: number
  data: SalesCountResponse | null
  loading: boolean
  error: string | null
}

export function useSalesCountReport() {
  const [state, setState] = useState<SalesCountState>(() => ({
    year: new Date().getFullYear(),
    data: null,
    loading: true,
    error: null,
  }))
  const { year } = state

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const data = await getSalesCount(year)
        if (!cancelled) setState((previous) => ({ ...previous, data, loading: false, error: null }))
      } catch (error) {
        if (!cancelled)
          setState((previous) => ({ ...previous, data: null, loading: false, error: getErrorMessage(error) }))
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [year])

  const updateYear = (nextYear: number) =>
    setState((previous) => ({ ...previous, year: nextYear, data: null, loading: true, error: null }))

  return { state, updateYear }
}
