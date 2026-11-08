import { apiFetch } from '../../api/client'
import type { ComboListado, ComboPayload } from '../products/api'

export function getCombos(): Promise<ComboListado[]> {
  return apiFetch<ComboListado[]>('/productos/combos')
}

export function getCombo(id: number): Promise<ComboListado> {
  return apiFetch<ComboListado>(`/productos/combos/${id}`)
}

export function createCombo(data: ComboPayload): Promise<ComboListado> {
  return apiFetch<ComboListado>('/productos/combos', { method: 'POST', body: data })
}

export function updateCombo(id: number, data: ComboPayload): Promise<ComboListado> {
  return apiFetch<ComboListado>(`/productos/combos/${id}`, { method: 'PUT', body: data })
}

export function deleteCombo(id: number): Promise<void> {
  return apiFetch<void>(`/productos/combos/${id}`, { method: 'DELETE' })
}
