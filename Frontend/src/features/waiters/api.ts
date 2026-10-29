import type { Attention, AttentionPayload, Waiter, WaiterPayload } from './types'

const API_BASE_URL = 'http://localhost:8000'

type WaiterResponse = Omit<Waiter, 'name'> & {
  nombre: string
}

async function request(path: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers)
  if (init?.body) headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  })

  if (!response.ok) {
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

  return response
}

function toWaiter(response: WaiterResponse): Waiter {
  return {
    id: response.id,
    name: response.nombre,
    nro_legajo: response.nro_legajo,
    estado: response.estado,
  }
}

export async function listWaiters(): Promise<Waiter[]> {
  const response = await request('/mozos/')
  const waiters = (await response.json()) as WaiterResponse[]
  return waiters.map(toWaiter)
}

export async function getWaiter(id: number): Promise<Waiter> {
  const waiters = await listWaiters()
  const waiter = waiters.find((candidate) => candidate.id === id)
  if (!waiter) throw new Error('No se encontró el mozo solicitado.')
  return waiter
}

export async function createWaiter(waiter: WaiterPayload): Promise<void> {
  await request('/mozos/', {
    method: 'POST',
    body: JSON.stringify(waiter),
  })
}

export async function updateWaiter(id: number, waiter: WaiterPayload): Promise<void> {
  await request(`/mozos/${id}`, {
    method: 'PUT',
    body: JSON.stringify(waiter),
  })
}

export async function deactivateWaiter(id: number): Promise<void> {
  await request(`/mozos/${id}`, { method: 'DELETE' })
}

export async function reactivateWaiter(id: number): Promise<void> {
  await request(`/mozos/${id}/reactivar`, { method: 'PATCH' })
}

export async function listAttentions(mozoId?: number): Promise<Attention[]> {
  const query = mozoId === undefined ? '' : `?mozo_id=${mozoId}`
  const response = await request(`/atenciones/${query}`)
  return (await response.json()) as Attention[]
}

export async function createAttention(attention: AttentionPayload): Promise<Attention> {
  const response = await request('/atenciones/', {
    method: 'POST',
    body: JSON.stringify(attention),
  })
  return (await response.json()) as Attention
}

export async function finishAttention(id: number, fecha_hasta: string): Promise<Attention> {
  const response = await request(`/atenciones/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ fecha_hasta }),
  })
  return (await response.json()) as Attention
}
