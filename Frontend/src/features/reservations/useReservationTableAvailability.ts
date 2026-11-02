import { useEffect, useMemo, useState } from 'react'
import { listReservations } from './api'
import type { ReservationRecord } from './types'

type AvailabilityState = {
  reservations: ReservationRecord[]
  loading: boolean
  error: string | null
}

export function useReservationTableAvailability(
  date: string,
  time: string,
  selectedTableIds: number[],
  reservationId?: number,
) {
  const [state, setState] = useState<AvailabilityState>({
    reservations: [],
    loading: true,
    error: null,
  })

  useEffect(() => {
    let cancelled = false

    async function loadReservations() {
      try {
        const reservations = await listReservations()
        if (!cancelled) {
          setState({ reservations, loading: false, error: null })
        }
      } catch (cause) {
        if (!cancelled) {
          setState({
            reservations: [],
            loading: false,
            error: cause instanceof Error
              ? cause.message
              : 'No se pudieron cargar las reservas para verificar las mesas.',
          })
        }
      }
    }

    void loadReservations()
    return () => {
      cancelled = true
    }
  }, [])

  const issues = useMemo(() => {
    if (!date || !time) return { conflicts: [], warnings: [] }

    const targetTime = new Date(`${date}T${time}`).getTime()
    const conflicts: Array<{ tableId: number; time: string }> = []
    const warnings: Array<{ tableId: number; time: string }> = []

    for (const reservation of state.reservations) {
      if (
        reservation.id === reservationId ||
        reservation.estado === 'cancelada' ||
        reservation.estado === 'ausente'
      ) {
        continue
      }

      const reservationTime = new Date(`${reservation.fecha}T${reservation.hora}`).getTime()
      const difference = (targetTime - reservationTime) / (60 * 1000)
      if (Math.abs(difference) > 4 * 60) continue

      for (const tableId of selectedTableIds) {
        if (!reservation.mesa_ids.includes(tableId)) continue
        const issue = { tableId, time: reservation.hora.slice(0, 5) }
        if (difference === 0) {
          conflicts.push(issue)
        } else {
          warnings.push(issue)
        }
      }
    }

    return { conflicts, warnings }
  }, [date, reservationId, selectedTableIds, state.reservations, time])

  return { ...issues, loading: state.loading, error: state.error }
}
