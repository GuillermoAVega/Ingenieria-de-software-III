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

const API_BASE_URL = 'http://localhost:8000'

async function request(path: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers)
  if (init?.body) headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
  if (response.ok) return response

  const body = await response.text()
  let message = body
  try {
    const error = JSON.parse(body) as { detail?: unknown }
    if (typeof error.detail === 'string') {
      message = error.detail
    } else if (Array.isArray(error.detail)) {
      message = error.detail
        .map((item) => (typeof item === 'object' && item !== null && 'msg' in item ? item.msg : ''))
        .filter(Boolean)
        .join('. ')
    }
  } catch {
    // Si la respuesta no es JSON, se muestra el texto devuelto por el servidor.
  }

  throw new Error(message || `Error al comunicarse con el servidor (${response.status}).`)
}

async function getJson<T>(path: string): Promise<T> {
  const response = await request(path)
  return (await response.json()) as T
}

async function sendJson<T>(path: string, method: 'POST' | 'PUT', body: unknown): Promise<T> {
  const response = await request(path, { method, body: JSON.stringify(body) })
  return (await response.json()) as T
}

async function remove(path: string): Promise<void> {
  await request(path, { method: 'DELETE' })
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
