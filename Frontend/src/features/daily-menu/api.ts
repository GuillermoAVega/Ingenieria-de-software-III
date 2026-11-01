import { apiFetch } from '../../api/client'

export type ProductoMenuPayload = {
  producto_id: number
  fecha: string
}

export type ProductoMenuRespuesta = {
  id: number
  producto_id: number
  fecha: string
}

export function createProductoMenu(data: ProductoMenuPayload): Promise<ProductoMenuRespuesta> {
  return apiFetch<ProductoMenuRespuesta>('/productos-menu', { method: 'POST', body: data })
}
