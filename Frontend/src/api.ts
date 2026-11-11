import { apiFetch, ApiError } from './api/client'

export { ApiError }

export async function api<T = void>(
  path: string,
  opts: { method?: string; body?: unknown } = {},
): Promise<T> {
  return apiFetch<T>(path, { method: opts.method ?? 'GET', body: opts.body })
}

// ---- Tipos (reflejan los schemas del backend) ----

export interface DetalleComanda {
  id: number
  comanda_id: number
  producto_id: number
  cantidad: number
  observaciones: string | null
  entregado: boolean
  activo: boolean
}

export interface Comanda {
  id: number
  fecha: string
  hora: string
  estado: 'abierta' | 'cerrada'
  mozo_id: number
  mesa_id: number
  cliente_id: number | null
  reserva_id: number | null
  activo: boolean
  detalles: DetalleComanda[]
}

export interface Factura {
  id: number
  comanda_id: number
  importe_total: number
  fecha_hora_emision: string
  activo: boolean
}

export interface DetalleFactura {
  id: number
  factura_id: number
  detalle_comanda_id: number | null
  promocion_id: number | null
  precio_unitario: number
  cantidad: number
  precio_final: number
  activo: boolean
}

export interface ComprobantePago {
  id: number
  factura_id: number
  medio_pago_id: number
  importe: number
  fecha_hora_emision: string
  activo: boolean
}

export interface MedioPago {
  id: number
  descripcion: string
  activo: boolean
}
