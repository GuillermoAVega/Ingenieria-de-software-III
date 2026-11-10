import { apiFetch } from '../../api/client'
import type { PaymentVoucher, PaymentVoucherPayload } from './types'

export function getInvoiceVouchers(invoiceId: number): Promise<PaymentVoucher[]> {
  return apiFetch<PaymentVoucher[]>(`/facturas/${invoiceId}/comprobantes`)
}

export function getVouchers(limit = 500): Promise<PaymentVoucher[]> {
  return apiFetch<PaymentVoucher[]>(`/comprobantes-pago?limit=${limit}`)
}

export function createVoucher(data: PaymentVoucherPayload): Promise<PaymentVoucher> {
  return apiFetch<PaymentVoucher>('/comprobantes-pago', { method: 'POST', body: data })
}

export function deleteVoucher(id: number): Promise<void> {
  return apiFetch<void>(`/comprobantes-pago/${id}`, { method: 'DELETE' })
}
