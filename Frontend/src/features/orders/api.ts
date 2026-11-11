import { apiFetch } from '../../api/client'
import type {
  Invoice,
  InvoiceLine,
  InvoiceLinePayload,
  Order,
  OrderItem,
  OrderItemCreatePayload,
  OrderItemUpdatePayload,
  OrdersPage,
  OrderPayload,
  OrderUpdatePayload,
} from './types'


export function getOrders(limit = 500): Promise<Order[]> {
  return apiFetch<Order[]>(`/comandas?limit=${limit}`)
}

export function getOrdersPage(params: {
  page: number
  pageSize: number
  status?: string
  search?: string
}): Promise<OrdersPage> {
  const query = new URLSearchParams({
    pagina: String(params.page),
    tamanio_pagina: String(params.pageSize),
  })
  if (params.status) query.set('estado', params.status)
  if (params.search?.trim()) query.set('buscar', params.search.trim())
  return apiFetch<OrdersPage>(`/comandas/resumen?${query}`)
}

export function getOrder(id: number): Promise<Order> {
  return apiFetch<Order>(`/comandas/${id}`)
}

export function createOrder(data: OrderPayload): Promise<Order> {
  return apiFetch<Order>('/comandas', { method: 'POST', body: data })
}

export function updateOrder(id: number, data: OrderUpdatePayload): Promise<Order> {
  return apiFetch<Order>(`/comandas/${id}`, { method: 'PUT', body: data })
}

export function deleteOrder(id: number): Promise<void> {
  return apiFetch<void>(`/comandas/${id}`, { method: 'DELETE' })
}

export function createOrderItem(data: OrderItemCreatePayload): Promise<OrderItem> {
  return apiFetch<OrderItem>('/detalles-comanda', { method: 'POST', body: data })
}

export function updateOrderItem(id: number, data: OrderItemUpdatePayload): Promise<OrderItem> {
  return apiFetch<OrderItem>(`/detalles-comanda/${id}`, { method: 'PUT', body: data })
}

export function deleteOrderItem(id: number): Promise<void> {
  return apiFetch<void>(`/detalles-comanda/${id}`, { method: 'DELETE' })
}

export function getOrderInvoices(orderId: number): Promise<Invoice[]> {
  return apiFetch<Invoice[]>(`/facturas?comanda_id=${orderId}`)
}

export function createInvoice(orderId: number): Promise<Invoice> {
  return apiFetch<Invoice>('/facturas', { method: 'POST', body: { comanda_id: orderId } })
}

export function createInvoiceLine(data: InvoiceLinePayload): Promise<InvoiceLine> {
  return apiFetch<InvoiceLine>('/detalles-factura', { method: 'POST', body: data })
}

