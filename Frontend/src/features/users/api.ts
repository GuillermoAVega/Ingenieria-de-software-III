import { apiFetch } from '../../api/client'
import type { UserPayload, UserRecord } from './types'

export function getUsers(): Promise<UserRecord[]> {
  return apiFetch<UserRecord[]>('/usuarios')
}

export function getUser(id: number): Promise<UserRecord> {
  return apiFetch<UserRecord>(`/usuarios/${id}`)
}

export function createUser(payload: UserPayload & { clave: string }): Promise<UserRecord> {
  return apiFetch<UserRecord>('/usuarios', { method: 'POST', body: payload })
}

export function updateUser(id: number, payload: Partial<UserPayload>): Promise<UserRecord> {
  return apiFetch<UserRecord>(`/usuarios/${id}`, { method: 'PUT', body: payload })
}
