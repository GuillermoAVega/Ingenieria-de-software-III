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

export type MenuDelDiaPayload = ProductoBasePayload & {
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

export type MenuEjecutivoRespuesta = ProductoBaseRespuesta & {
  tipo: 'menu_ejecutivo'
}

export type ComboRespuesta = ProductoBaseRespuesta & {
  tipo: 'combo_promocion'
}

export type MenuDelDiaRespuesta = ProductoBaseRespuesta & {
  tipo: 'menu_del_dia'
}

/** Ítem del listado: incluye la fecha asignada más cercana desde hoy, si existe. */
export type MenuDelDiaListado = MenuDelDiaRespuesta & {
  proxima_fecha: string | null
}

export function getPlatos(): Promise<PlatoRespuesta[]> {
  return apiFetch<PlatoRespuesta[]>('/productos/platos')
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

export function getBebidas(): Promise<BebidaRespuesta[]> {
  return apiFetch<BebidaRespuesta[]>('/productos/bebidas')
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

export function getPostres(): Promise<PostreRespuesta[]> {
  return apiFetch<PostreRespuesta[]>('/productos/postres')
}

export function getMenusEjecutivos(): Promise<MenuEjecutivoRespuesta[]> {
  return apiFetch<MenuEjecutivoRespuesta[]>('/productos/menus-ejecutivos')
}

export function getCombos(): Promise<ComboListado[]> {
  return apiFetch<ComboListado[]>('/productos/combos')
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

export function getMenusDelDia(): Promise<MenuDelDiaListado[]> {
  return apiFetch<MenuDelDiaListado[]>('/productos/menus-del-dia')
}

export function getMenuDelDia(id: number): Promise<MenuDelDiaRespuesta> {
  return apiFetch<MenuDelDiaRespuesta>(`/productos/menus-del-dia/${id}`)
}

export function createMenuDelDia(data: MenuDelDiaPayload): Promise<MenuDelDiaRespuesta> {
  return apiFetch<MenuDelDiaRespuesta>('/productos/menus-del-dia', { method: 'POST', body: data })
}

export function updateMenuDelDia(
  id: number,
  data: MenuDelDiaPayload,
): Promise<MenuDelDiaRespuesta> {
  return apiFetch<MenuDelDiaRespuesta>(`/productos/menus-del-dia/${id}`, {
    method: 'PUT',
    body: data,
  })
}

export function deleteMenuDelDia(id: number): Promise<void> {
  return apiFetch<void>(`/productos/menus-del-dia/${id}`, { method: 'DELETE' })
}

export type MenuEjecutivoListado = ProductoBaseRespuesta & {
  tipo: 'menu_ejecutivo'
  plato_id: number
  postre_id: number
}

/** Componente de un combo: id del producto y unidades (entero >= 1). */
export type ComboComponente = {
  id: number
  cantidad: number
}

export type ComboListado = ProductoBaseRespuesta & {
  tipo: 'combo_promocion'
  fecha_desde: string
  fecha_hasta: string
  platos: ComboComponente[]
  bebidas: ComboComponente[]
  postres: ComboComponente[]
}

export type ComboPayload = ProductoBasePayload & {
  fecha_desde: string
  fecha_hasta: string
  platos: ComboComponente[]
  bebidas: ComboComponente[]
  postres: ComboComponente[]
}
