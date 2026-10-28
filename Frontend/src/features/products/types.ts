export type ProductTabId =
  | 'platos'
  | 'postres'
  | 'bebidas'
  | 'menu-ejecutivo'
  | 'menu-del-dia'
  | 'combos'
  | 'promociones'

export type Product = {
  id: string
  name: string
  section: string
  price: number
  tab: ProductTabId
}

export type ProductTab = {
  id: ProductTabId
  label: string
  count: number
}
