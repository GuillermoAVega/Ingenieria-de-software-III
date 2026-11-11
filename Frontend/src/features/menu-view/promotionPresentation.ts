import type { Promotion } from '../promotions/types'

export type PromotionPresentation = {
  precio: string
  precioOriginal?: string
  promociones: string[]
}

function promotionLabel(promotion: Promotion): string {
  if (promotion.tipo === 'porcentaje') {
    return `${promotion.nombre}: ${Number(promotion.descuento)}% OFF`
  }
  return `${promotion.nombre}: llevá ${promotion.lleva}, pagá ${promotion.paga}`
}

export function getPromotionPresentation(
  productId: number,
  price: string,
  date: string,
  promotions: Promotion[],
): PromotionPresentation {
  const active = promotions.filter(
    (promotion) =>
      !promotion.dado_de_baja &&
      promotion.fecha_desde <= date &&
      promotion.fecha_hasta >= date &&
      promotion.productos_ids.includes(productId),
  )
  const bestDiscount = Math.max(
    0,
    ...active
      .filter((promotion) => promotion.tipo === 'porcentaje')
      .map((promotion) => Number(promotion.descuento ?? 0)),
  )

  if (bestDiscount === 0) {
    return { precio: price, promociones: active.map(promotionLabel) }
  }

  const promotionalPrice = Number(price) * (1 - bestDiscount / 100)
  return {
    precio: promotionalPrice.toFixed(2),
    precioOriginal: price,
    promociones: active.map(promotionLabel),
  }
}
