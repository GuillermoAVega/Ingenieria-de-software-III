import { apiFetch } from '../../api/client'

export type ProductoMenuPayload = {
  menu_del_dia_id: number
  fecha: string
}

export type ProductoMenuRespuesta = {
  id: number
  menu_del_dia_id: number
  fecha: string
}

/** Ítem del listado: incluye el menú del día asociado ya resuelto por el backend. */
export type ProductoMenuDetalle = ProductoMenuRespuesta & {
  menu_del_dia_nombre: string
  menu_del_dia_dado_de_baja: boolean
}

export function getProductoMenus(): Promise<ProductoMenuDetalle[]> {
  return apiFetch<ProductoMenuDetalle[]>('/productos-menu')
}

export function getProductoMenu(id: number): Promise<ProductoMenuDetalle> {
  return apiFetch<ProductoMenuDetalle>(`/productos-menu/${id}`)
}

export function createProductoMenu(data: ProductoMenuPayload): Promise<ProductoMenuRespuesta> {
  return apiFetch<ProductoMenuRespuesta>('/productos-menu', { method: 'POST', body: data })
}

export function updateProductoMenuFecha(
  id: number,
  fecha: string,
): Promise<ProductoMenuRespuesta> {
  return apiFetch<ProductoMenuRespuesta>(`/productos-menu/${id}`, {
    method: 'PUT',
    body: { fecha },
  })
}

export function deleteProductoMenu(id: number): Promise<void> {
  return apiFetch<void>(`/productos-menu/${id}`, { method: 'DELETE' })
}
