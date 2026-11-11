import { apiFetch } from '../../api/client'
import type { Invoice } from '../orders/types'

export function getInvoices(limit = 500): Promise<Invoice[]> {
  return apiFetch<Invoice[]>(`/facturas?limit=${limit}`)
}
