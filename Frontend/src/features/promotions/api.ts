import { apiFetch } from '../../api/client'
import type { Promotion, PromotionPayload } from './types'

export function getPromotions(includeBajas: boolean): Promise<Promotion[]> {
  return apiFetch<Promotion[]>(`/promociones?incluir_bajas=${includeBajas}`)
}

export function getPromotion(id: number): Promise<Promotion> {
  return apiFetch<Promotion>(`/promociones/${id}`)
}

export function createPromotion(data: PromotionPayload): Promise<Promotion> {
  return apiFetch<Promotion>('/promociones', { method: 'POST', body: data })
}

export function updatePromotion(id: number, data: PromotionPayload): Promise<Promotion> {
  return apiFetch<Promotion>(`/promociones/${id}`, { method: 'PUT', body: data })
}

export function deletePromotion(id: number): Promise<void> {
  return apiFetch<void>(`/promociones/${id}`, { method: 'DELETE' })
}
