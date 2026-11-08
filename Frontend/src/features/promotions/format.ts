import type { Promotion } from './types'

/** Texto legible del beneficio: "10%", "2x1", "3x2" o "Lleva N paga M". */
export function formatBenefit(
  promotion: Pick<Promotion, 'tipo' | 'descuento' | 'lleva' | 'paga'>,
): string {
  if (promotion.tipo === 'lleva_paga' && promotion.lleva !== null && promotion.paga !== null) {
    if (promotion.lleva - promotion.paga === 1) return `${promotion.lleva}x${promotion.paga}`
    return `Lleva ${promotion.lleva} paga ${promotion.paga}`
  }
  return `${Number(promotion.descuento)}%`
}
