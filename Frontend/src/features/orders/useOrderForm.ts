import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { createOrder } from './api'
import { listTables } from '../tables/api'
import type { TableRecord } from '../tables/types'
import { listCustomers, listReservations } from '../reservations/api'
import type { CustomerRecord, ReservationRecord } from '../reservations/types'

export type OrderFormValues = {
  mesaId: string
  mesaIds: number[]
  comensales: string
  clienteId: string
  reservaId: string
}

type OrderFormState = OrderFormValues & {
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
  tables: TableRecord[]
  tablesLoading: boolean
  tablesError: string | null
  customers: CustomerRecord[]
  reservations: ReservationRecord[]
}

function createInitialState(): OrderFormState {
  return {
    mesaId: '',
    mesaIds: [],
    comensales: '',
    clienteId: '',
    reservaId: '',
    saving: false,
    error: null,
    fieldErrors: {},
    tables: [],
    tablesLoading: true,
    tablesError: null,
    customers: [],
    reservations: [],
  }
}

function seleccionarMesas(tables: TableRecord[], guests: number): number[] {
  if (!Number.isInteger(guests) || guests < 1) return []
  const disponibles = tables.filter((table) => table.estado && table.disponible)
  let mejorIds: number[] | null = null
  let mejorCapacidad = Number.POSITIVE_INFINITY

  function buscar(index: number, ids: number[], capacidad: number) {
    if (capacidad >= guests) {
      if (capacidad < mejorCapacidad || (capacidad === mejorCapacidad && ids.length > (mejorIds?.length ?? 0))) {
        mejorIds = ids
        mejorCapacidad = capacidad
      }
      return
    }
    for (let position = index; position < disponibles.length; position += 1) {
      const table = disponibles[position]
      buscar(position + 1, [...ids, table.id], capacidad + table.capacidad)
    }
  }

  buscar(0, [], 0)
  return mejorIds ?? []
}

function reservaEnVentana(reservation: ReservationRecord): boolean {
  if (reservation.estado !== 'pendiente') return false
  const now = new Date()
  const reservationTime = new Date(`${reservation.fecha}T${reservation.hora}`)
  const difference = (now.getTime() - reservationTime.getTime()) / 60000
  return difference >= -15 && difference <= 30
}

export function useOrderForm(reservationId?: string) {
  const [state, setState] = useState<OrderFormState>(() => ({
    ...createInitialState(),
    reservaId: reservationId ?? '',
  }))

  useEffect(() => {
    if (reservationId) return
    let cancelled = false
    async function loadTables() {
      try {
        const [tables, customers, reservations] = await Promise.all([listTables(), listCustomers(), listReservations()])
        if (!cancelled) {
          setState((previous) => {
            const mesaIds = seleccionarMesas(tables, Number(previous.comensales))
            return { ...previous, tables, customers, reservations, mesaIds, mesaId: mesaIds[0] ? String(mesaIds[0]) : '', tablesLoading: false }
          })
        }
      } catch (cause) {
        if (!cancelled) setState((previous) => ({ ...previous, tablesLoading: false, tablesError: cause instanceof Error ? cause.message : 'No se pudieron cargar las mesas.' }))
      }
    }
    void loadTables()
    return () => { cancelled = true }
  }, [reservationId])

  const updateField = (field: keyof OrderFormValues, value: string) => {
    if (field === 'comensales') {
      setState((previous) => {
        const mesaIds = seleccionarMesas(previous.tables, Number(value))
        return { ...previous, comensales: value, mesaIds, mesaId: mesaIds[0] ? String(mesaIds[0]) : '' }
      })
      return
    }
    if (field === 'reservaId') {
      const reservation = state.reservations.find((candidate) => candidate.id === Number(value) && reservaEnVentana(candidate))
      if (!reservation) {
        setState((previous) => ({ ...previous, reservaId: value }))
        return
      }
      setState((previous) => ({
        ...previous,
        reservaId: value,
        clienteId: String(reservation.cliente_id),
        comensales: String(reservation.cant_comensales),
        mesaIds: reservation.mesa_ids,
        mesaId: reservation.mesa_ids[0] ? String(reservation.mesa_ids[0]) : '',
      }))
      return
    }
    if (field === 'clienteId') {
      const reservation = state.reservations.find((candidate) => candidate.cliente_id === Number(value) && reservaEnVentana(candidate))
      if (!reservation) {
        setState((previous) => ({ ...previous, clienteId: value }))
        return
      }
      setState((previous) => ({
        ...previous,
        clienteId: value,
        reservaId: String(reservation.id),
        comensales: String(reservation.cant_comensales),
        mesaIds: reservation.mesa_ids,
        mesaId: reservation.mesa_ids[0] ? String(reservation.mesa_ids[0]) : '',
      }))
      return
    }
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.saving) return

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    try {
      if (!reservationId && state.mesaIds.length === 0) {
        setState((previous) => ({ ...previous, saving: false, error: 'No hay mesas disponibles para esa cantidad de comensales.' }))
        return
      }
      const order = await createOrder(reservationId
        ? { reserva_id: Number(reservationId) }
        : {
            mesa_ids: state.mesaIds,
            comensales: Number(state.comensales),
            cliente_id: state.clienteId.trim() ? Number(state.clienteId) : null,
            reserva_id: state.reservaId.trim() ? Number(state.reservaId) : null,
          })
      navigate(`/comandas/${order.id}`)
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        error: getErrorMessage(requestError),
        fieldErrors: getFieldErrors(requestError),
      }))
    } finally {
      setState((previous) => ({ ...previous, saving: false }))
    }
  }

  return {
    state,
    updateField,
    submit,
  }
}
