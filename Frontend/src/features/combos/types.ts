import type { ComboComponente } from '../products/api'
import type { PickerOption } from '../promotions/ProductPicker'

export type ComboSource = 'platos' | 'bebidas' | 'postres'

export const COMBO_SOURCES: ComboSource[] = ['platos', 'bebidas', 'postres']

/** Producto seleccionable como componente de un combo. */
export type ComboOption = PickerOption & {
  source: ComboSource
  productId: number
  precio: number
}

export type { ComboComponente }
