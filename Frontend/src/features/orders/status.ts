import type { BadgeTone } from '../../ui/ui'
import type { OrderStatus } from './types'

export const ORDER_STATUS_LABEL: Record<OrderStatus, string> = {
  abierta: 'Abierta',
  cerrada: 'Cerrada',
}

export const ORDER_STATUS_TONE: Record<OrderStatus, BadgeTone> = {
  abierta: 'warning',
  cerrada: 'success',
}
