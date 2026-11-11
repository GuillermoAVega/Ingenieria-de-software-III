import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { getAbsentClientsReport } from './api'
import type { AbsentClientsReport } from './types'

type AbsentClientsReportState = {
  data: AbsentClientsReport | null
  loading: boolean
  error: string | null
}

export function useAbsentClientsReport() {
  const [state, setState] = useState<AbsentClientsReportState>({
    data: null,
    loading: true,
    error: null,
  })

  useEffect(() => {
    let cancelled = false

    async function loadReport() {
      try {
        const data = await getAbsentClientsReport()
        if (!cancelled) setState({ data, loading: false, error: null })
      } catch (requestError) {
        if (!cancelled) {
          setState({ data: null, loading: false, error: getErrorMessage(requestError) })
        }
      }
    }

    void loadReport()
    return () => {
      cancelled = true
    }
  }, [])

  return { state }
}
