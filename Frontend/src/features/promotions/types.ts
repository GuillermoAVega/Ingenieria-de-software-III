/** Promoción tal como la devuelve `GET /promociones`. */
export type PromotionType = 'porcentaje' | 'lleva_paga'

export type Promotion = {
  id: number
  nombre: string
  tipo: PromotionType
  fecha_desde: string
  fecha_hasta: string
  descuento: string | null
  lleva: number | null
  paga: number | null
  dado_de_baja: boolean
  productos_ids: number[]
  /** true si alguna línea de factura la referencia: no se puede modificar */
  en_uso: boolean
}

/** Cuerpo de `POST /promociones` y `PUT /promociones/{id}`. */
export type PromotionPayload = {
  nombre: string
  tipo: PromotionType
  fecha_desde: string
  fecha_hasta: string
  /** solo con `tipo = 'porcentaje'` */
  descuento?: number
  /** solo con `tipo = 'lleva_paga'` */
  lleva?: number
  paga?: number
  productos_ids: number[]
}

/** Producto seleccionable en el formulario, con su tipo legible. */
export type PromotionProductOption = {
  key: string
  nombre: string
  tipoLabel: string
  dado_de_baja: boolean
}
