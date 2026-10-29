export type OrderStatus = 'abierta' | 'cerrada'

export type OrderItemStatus = 'pendiente' | 'entregado'

export type OrderItem = {
  id: string
  name: string
  quantity: number
  unitPrice: number
  note?: string
  status: OrderItemStatus
}

export type Order = {
  id: string
  table: string
  sector: string
  waiter: string
  customer?: string
  openedAt: string
  subtotal: number
  discountLabel?: string
  discount: number
  total: number
  status: OrderStatus
  reservation?: string
  items: OrderItem[]
}
