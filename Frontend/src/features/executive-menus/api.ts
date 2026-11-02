import { apiFetch } from '../../api/client'
import type { ProductoBaseRespuesta } from '../products/api'

export type MenuEjecutivoPayload = {
  nombre: string
  precio: number | string
  descripcion?: string | null
  imagen?: string | null
  seccion_id?: number | null
  plato_id: number
  postre_id: number
}

export type MenuEjecutivoRespuesta = ProductoBaseRespuesta & {
  tipo: 'menu_ejecutivo'
  plato_id: number
  postre_id: number
}

export function getMenusEjecutivos(): Promise<MenuEjecutivoRespuesta[]> {
  return apiFetch<MenuEjecutivoRespuesta[]>('/productos/menus-ejecutivos')
}

export function getMenuEjecutivo(id: number): Promise<MenuEjecutivoRespuesta> {
  return apiFetch<MenuEjecutivoRespuesta>(`/productos/menus-ejecutivos/${id}`)
}

export function createMenuEjecutivo(
  data: MenuEjecutivoPayload,
): Promise<MenuEjecutivoRespuesta> {
  return apiFetch<MenuEjecutivoRespuesta>('/productos/menus-ejecutivos', {
    method: 'POST',
    body: data,
  })
}

export function updateMenuEjecutivo(
  id: number,
  data: MenuEjecutivoPayload,
): Promise<MenuEjecutivoRespuesta> {
  return apiFetch<MenuEjecutivoRespuesta>(`/productos/menus-ejecutivos/${id}`, {
    method: 'PUT',
    body: data,
  })
}

export function deleteMenuEjecutivo(id: number): Promise<void> {
  return apiFetch<void>(`/productos/menus-ejecutivos/${id}`, { method: 'DELETE' })
}
