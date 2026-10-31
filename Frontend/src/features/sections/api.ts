import { apiFetch } from '../../api/client'

export type SeccionPayload = {
  nombre: string
  subtitulo?: string | null
  posicion: number
}

export type SeccionRespuesta = {
  id: number
  nombre: string
  subtitulo: string | null
  posicion: number
  productos_ids: number[]
}

export function getSections(): Promise<SeccionRespuesta[]> {
  return apiFetch<SeccionRespuesta[]>('/secciones')
}

export function getSection(id: number): Promise<SeccionRespuesta> {
  return apiFetch<SeccionRespuesta>(`/secciones/${id}`)
}

export function createSection(data: SeccionPayload): Promise<SeccionRespuesta> {
  return apiFetch<SeccionRespuesta>('/secciones', { method: 'POST', body: data })
}

export function updateSection(id: number, data: SeccionPayload): Promise<SeccionRespuesta> {
  return apiFetch<SeccionRespuesta>(`/secciones/${id}`, { method: 'PUT', body: data })
}

export function deleteSection(id: number): Promise<void> {
  return apiFetch<void>(`/secciones/${id}`, { method: 'DELETE' })
}
