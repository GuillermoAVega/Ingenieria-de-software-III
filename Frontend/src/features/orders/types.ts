export type OrderStatus = 'abierta' | 'cerrada'

export type OrderItem = {
  id: number
  comanda_id: number
  producto_id: number
  cantidad: number
  observaciones: string | null
  entregado: boolean
  activo: boolean
}

export type Order = {
  id: number
  fecha: string
  hora: string
  estado: OrderStatus
  mozo_id: number | null
  mesa_id: number | null
  mesa_ids: number[]
  cliente_id: number | null
  reserva_id: number | null
  activo: boolean
  detalles: OrderItem[]
}

export type OrderListItem = Order & {
  waiterName: string | null
}

export type OrderItemPayload = {
  producto_id: number
  cantidad: number
  observaciones?: string | null
}

export type OrderItemCreatePayload = OrderItemPayload & {
  comanda_id: number
}

export type OrderItemUpdatePayload = Partial<OrderItemPayload> & {
  entregado?: boolean
}

export type OrderPayload = {
  fecha?: string
  hora?: string
  mesa_ids?: number[]
  comensales?: number
  mozo_id?: number | null
  mesa_id?: number | null
  cliente_id?: number | null
  reserva_id?: number | null
  detalles?: OrderItemPayload[]
}

export type OrderUpdatePayload = Partial<Omit<OrderPayload, 'detalles'>> & {
  estado?: OrderStatus
}

export type Invoice = {
  id: number
  comanda_id: number
  importe_total: number
  fecha_hora_emision: string
  activo: boolean
}

export type InvoiceLinePayload = {
  factura_id: number
  detalle_comanda_id: number | null
  precio_unitario: number
  cantidad: number
  precio_final?: number
}

export type InvoiceLine = {
  id: number
  factura_id: number
  detalle_comanda_id: number | null
  promocion_id: number | null
  precio_unitario: number
  cantidad: number
  precio_final: number
  activo: boolean
}
