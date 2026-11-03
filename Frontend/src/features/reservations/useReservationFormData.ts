import { useEffect, useState } from 'react'
import {
  getReservation,
  listCustomers,
  listReservationDetails,
  listReservationTables,
  listTables,
} from './api'
import type { CustomerRecord, ReservationDetail, ReservationRecord, TableRecord } from './types'

export type ReservationFormData = {
  customers: CustomerRecord[]
  tables: TableRecord[]
  reservation: ReservationRecord | null
  reservationTables: TableRecord[]
  reservationDetails: ReservationDetail[]
  loading: boolean
  loadFailed: boolean
  error: string | null
}

function initialState(): ReservationFormData {
  return {
    customers: [],
    tables: [],
    reservation: null,
    reservationTables: [],
    reservationDetails: [],
    loading: true,
    loadFailed: false,
    error: null,
  }
}

function getErrorMessage(cause: unknown): string {
  return cause instanceof Error ? cause.message : 'No se pudieron cargar los datos de la reserva.'
}

export function useReservationFormData(id?: string): ReservationFormData {
  const [state, setState] = useState<ReservationFormData>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadFormData() {
      try {
        const [customers, tables] = await Promise.all([listCustomers(), listTables()])
        if (cancelled) return

        if (!id) {
          setState((previous) => ({ ...previous, customers, tables, loading: false }))
          return
        }

        const reservationId = Number(id)
        if (!Number.isInteger(reservationId) || reservationId < 1) {
          throw new Error('El identificador de la reserva no es válido.')
        }

        const [reservation, reservationTables, reservationDetails] = await Promise.all([
          getReservation(reservationId),
          listReservationTables(reservationId),
          listReservationDetails(reservationId),
        ])
        if (cancelled) return

        setState({
          customers,
          tables: [...new Map([...tables, ...reservationTables].map((table) => [table.id, table])).values()],
          reservation,
          reservationTables,
          reservationDetails,
          loading: false,
          loadFailed: false,
          error: null,
        })
      } catch (cause) {
        if (!cancelled) {
          setState((previous) => ({
            ...previous,
            loading: false,
            loadFailed: true,
            error: getErrorMessage(cause),
          }))
        }
      }
    }

    void loadFormData()
    return () => {
      cancelled = true
    }
  }, [id])

  return state
}
