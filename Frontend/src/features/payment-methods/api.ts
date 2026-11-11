import { apiFetch } from '../../api/client'
import type { PaymentMethod, PaymentMethodPayload } from './types'

export function getPaymentMethods(): Promise<PaymentMethod[]> {
  return apiFetch<PaymentMethod[]>('/medios-pago?limit=500')
}

export function getPaymentMethod(id: number): Promise<PaymentMethod> {
  return apiFetch<PaymentMethod>(`/medios-pago/${id}`)
}

export function createPaymentMethod(data: PaymentMethodPayload): Promise<PaymentMethod> {
  return apiFetch<PaymentMethod>('/medios-pago', { method: 'POST', body: data })
}

export function updatePaymentMethod(id: number, data: PaymentMethodPayload): Promise<PaymentMethod> {
  return apiFetch<PaymentMethod>(`/medios-pago/${id}`, { method: 'PUT', body: data })
}

export function deletePaymentMethod(id: number): Promise<void> {
  return apiFetch<void>(`/medios-pago/${id}`, { method: 'DELETE' })
}
