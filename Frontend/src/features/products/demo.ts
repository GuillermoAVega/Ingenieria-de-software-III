import type { Product, ProductTab } from './types'

export const DEMO_PRODUCT_TABS: ProductTab[] = [
  { id: 'platos', label: 'Platos', count: 24 },
  { id: 'postres', label: 'Postres', count: 8 },
  { id: 'bebidas', label: 'Bebidas', count: 15 },
  { id: 'menu-ejecutivo', label: 'Menú ejecutivo', count: 3 },
  { id: 'menu-del-dia', label: 'Menú del día', count: 2 },
  { id: 'combos', label: 'Combos', count: 4 },
  { id: 'promociones', label: 'Promociones', count: 2 },
]

export const DEMO_PRODUCTS: Product[] = [
  { id: 'prod-1', name: 'Milanesa napolitana', section: 'Principales', price: 12400, tab: 'platos' },
  { id: 'prod-2', name: 'Ravioles de ricota', section: 'Pastas', price: 13200, tab: 'platos' },
  { id: 'prod-3', name: 'Ensalada caesar', section: 'Entradas', price: 9800, tab: 'platos' },
  { id: 'prod-4', name: 'Bife de chorizo', section: 'Parrilla', price: 18900, tab: 'platos' },
  { id: 'prod-5', name: 'Risotto de hongos', section: 'Pastas', price: 14300, tab: 'platos' },
  { id: 'prod-6', name: 'Provoleta', section: 'Entradas', price: 8700, tab: 'platos' },
  { id: 'prod-7', name: 'Ñoquis de papa', section: 'Pastas', price: 11900, tab: 'platos' },
]

export const DEMO_PRODUCT_SECTIONS = [
  'Principales',
  'Pastas',
  'Entradas',
  'Parrilla',
  'Postres',
  'Bebidas',
]
