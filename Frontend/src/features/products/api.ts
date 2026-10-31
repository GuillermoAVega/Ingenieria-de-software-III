import { apiFetch } from '../../api/client'

export type ProductoBasePayload = {
  nombre: string
  precio: number | string
  descripcion?: string | null
  imagen?: string | null
  seccion_id?: number | null
}

export type ProductoBaseRespuesta = {
  id: number
  nombre: string
  precio: string
  descripcion: string | null
  imagen: string | null
  dado_de_baja: boolean
  seccion_id: number | null
}

export type PlatoPayload = ProductoBasePayload & {
  cant_personas: number
  dado_de_baja?: boolean | null
}

export type BebidaPayload = ProductoBasePayload & {
  es_alcoholica: boolean
  dado_de_baja?: boolean | null
}

export type PostrePayload = ProductoBasePayload & {
  dado_de_baja?: boolean | null
}

export type PlatoRespuesta = ProductoBaseRespuesta & {
  tipo: 'plato'
  cant_personas: number
}

export type BebidaRespuesta = ProductoBaseRespuesta & {
  tipo: 'bebida'
  es_alcoholica: boolean
}

export type PostreRespuesta = ProductoBaseRespuesta & {
  tipo: 'postre'
}

export function getPlato(id: number): Promise<PlatoRespuesta> {
  return apiFetch<PlatoRespuesta>(`/productos/platos/${id}`)
}

export function createPlato(data: PlatoPayload): Promise<PlatoRespuesta> {
  return apiFetch<PlatoRespuesta>('/productos/platos', { method: 'POST', body: data })
}

export function updatePlato(id: number, data: PlatoPayload): Promise<PlatoRespuesta> {
  return apiFetch<PlatoRespuesta>(`/productos/platos/${id}`, { method: 'PUT', body: data })
}

export function deletePlato(id: number): Promise<void> {
  return apiFetch<void>(`/productos/platos/${id}`, { method: 'DELETE' })
}

export function getBebida(id: number): Promise<BebidaRespuesta> {
  return apiFetch<BebidaRespuesta>(`/productos/bebidas/${id}`)
}

export function createBebida(data: BebidaPayload): Promise<BebidaRespuesta> {
  return apiFetch<BebidaRespuesta>('/productos/bebidas', { method: 'POST', body: data })
}

export function updateBebida(id: number, data: BebidaPayload): Promise<BebidaRespuesta> {
  return apiFetch<BebidaRespuesta>(`/productos/bebidas/${id}`, { method: 'PUT', body: data })
}

export function deleteBebida(id: number): Promise<void> {
  return apiFetch<void>(`/productos/bebidas/${id}`, { method: 'DELETE' })
}

export function getPostre(id: number): Promise<PostreRespuesta> {
  return apiFetch<PostreRespuesta>(`/productos/postres/${id}`)
}

export function createPostre(data: PostrePayload): Promise<PostreRespuesta> {
  return apiFetch<PostreRespuesta>('/productos/postres', { method: 'POST', body: data })
}

export function updatePostre(id: number, data: PostrePayload): Promise<PostreRespuesta> {
  return apiFetch<PostreRespuesta>(`/productos/postres/${id}`, { method: 'PUT', body: data })
}

export function deletePostre(id: number): Promise<void> {
  return apiFetch<void>(`/productos/postres/${id}`, { method: 'DELETE' })
}
