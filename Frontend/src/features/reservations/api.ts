import type {
  CustomerPayload,
  CustomerRecord,
  ReservationDetail,
  ReservationDetailPayload,
  ReservationPayload,
  ReservationRecord,
  ReservationUpdatePayload,
  TableRecord,
} from './types'
import { apiFetch } from '../../api/client'

async function getJson<T>(path: string): Promise<T> {
  return apiFetch<T>(path)
}

async function sendJson<T>(path: string, method: 'POST' | 'PUT' | 'PATCH', body: unknown): Promise<T> {
  return apiFetch<T>(path, { method, body })
}

async function remove(path: string): Promise<void> {
  await apiFetch(path, { method: 'DELETE' })
}

export function listReservations(): Promise<ReservationRecord[]> {
  return getJson('/reservas')
}

export function getReservation(id: number): Promise<ReservationRecord> {
  return getJson(`/reservas/${id}`)
}

export function createReservation(payload: ReservationPayload & {
  mesa_ids: number[]
  detalles: ReservationDetailPayload[]
}): Promise<ReservationRecord> {
  return sendJson('/reservas', 'POST', payload)
}

export function updateReservation(id: number, payload: ReservationUpdatePayload): Promise<ReservationRecord> {
  return sendJson(`/reservas/${id}`, 'PUT', payload)
}

export function cancelReservation(id: number): Promise<void> {
  return remove(`/reservas/${id}`)
}

export function markReservationAbsent(id: number): Promise<ReservationRecord> {
  return sendJson(`/reservas/${id}/ausente`, 'PATCH', {})
}

export function listCustomers(): Promise<CustomerRecord[]> {
  return getJson('/clientes')
}

export function createCustomer(payload: CustomerPayload): Promise<CustomerRecord> {
  return sendJson('/clientes', 'POST', payload)
}

export function listTables(): Promise<TableRecord[]> {
  return getJson('/mesas')
}

export function listReservationTables(id: number): Promise<TableRecord[]> {
  return getJson(`/reservas/${id}/mesas`)
}

export function addReservationTable(reservationId: number, tableId: number): Promise<TableRecord> {
  return sendJson(`/reservas/${reservationId}/mesas`, 'POST', { mesa_id: tableId })
}

export function removeReservationTable(reservationId: number, tableId: number): Promise<void> {
  return remove(`/reservas/${reservationId}/mesas/${tableId}`)
}

export function listReservationDetails(id: number): Promise<ReservationDetail[]> {
  return getJson(`/reservas/${id}/detalles`)
}

export function addReservationDetail(
  reservationId: number,
  payload: ReservationDetailPayload,
): Promise<ReservationDetail> {
  return sendJson(`/reservas/${reservationId}/detalles`, 'POST', payload)
}

export function removeReservationDetail(reservationId: number, productId: number): Promise<void> {
  return remove(`/reservas/${reservationId}/detalles/${productId}`)
}
