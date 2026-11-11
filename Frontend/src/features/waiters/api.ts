import type { Attention, AttentionPayload, Waiter, WaiterPayload } from './types'
import { apiFetch } from '../../api/client'

type WaiterResponse = Omit<Waiter, 'name'> & {
  nombre: string
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
  const waiters = await apiFetch<WaiterResponse[]>('/mozos/')
  return waiters.map(toWaiter)
}

export async function getWaiter(id: number): Promise<Waiter> {
  const waiters = await listWaiters()
  const waiter = waiters.find((candidate) => candidate.id === id)
  if (!waiter) throw new Error('No se encontró el mozo solicitado.')
  return waiter
}

export async function createWaiter(waiter: WaiterPayload): Promise<void> {
  await apiFetch('/mozos/', { method: 'POST', body: waiter })
}

export async function updateWaiter(id: number, waiter: WaiterPayload): Promise<void> {
  await apiFetch(`/mozos/${id}`, { method: 'PUT', body: waiter })
}

export async function deactivateWaiter(id: number): Promise<void> {
  await apiFetch(`/mozos/${id}`, { method: 'DELETE' })
}

export async function reactivateWaiter(id: number): Promise<void> {
  await apiFetch(`/mozos/${id}/reactivar`, { method: 'PATCH' })
}

export async function listAttentions(mozoId?: number): Promise<Attention[]> {
  const query = mozoId === undefined ? '' : `?mozo_id=${mozoId}`
  return apiFetch<Attention[]>(`/atenciones/${query}`)
}

export async function createAttention(attention: AttentionPayload): Promise<Attention> {
  return apiFetch<Attention>('/atenciones/', { method: 'POST', body: attention })
}

export async function finishAttention(id: number, fecha_hasta: string): Promise<Attention> {
  return apiFetch<Attention>(`/atenciones/${id}`, { method: 'PUT', body: { fecha_hasta } })
}
