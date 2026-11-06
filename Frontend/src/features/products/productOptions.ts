import { getProductoMenus } from '../daily-menu/api'
import { getBebidas, getCombos, getMenusEjecutivos, getPlatos, getPostres } from './api'

export type ProductOption = {
  id: number
  name: string
  type: string
  price: string
}

/** Carga los productos reales disponibles para comandas y reservas. */
export async function loadProductOptions(): Promise<ProductOption[]> {
  const [platos, bebidas, postres, menus, combos, menusDelDia] = await Promise.all([
    getPlatos(),
    getBebidas(),
    getPostres(),
    getMenusEjecutivos(),
    getCombos(),
    getProductoMenus(),
  ])

  const baseProducts: ProductOption[] = [
    ...platos.map((product) => ({ id: product.id, name: product.nombre, type: 'Plato', price: String(product.precio) })),
    ...bebidas.map((product) => ({ id: product.id, name: product.nombre, type: 'Bebida', price: String(product.precio) })),
    ...postres.map((product) => ({ id: product.id, name: product.nombre, type: 'Postre', price: String(product.precio) })),
    ...menus.map((product) => ({ id: product.id, name: product.nombre, type: 'Menú ejecutivo', price: String(product.precio) })),
    ...combos.map((product) => ({ id: product.id, name: product.nombre, type: 'Combo promocional', price: String(product.precio) })),
  ]

  return [
    ...menusDelDia.map((product) => ({
      id: product.producto_id,
      name: product.producto_nombre,
      type: 'Menú del día',
      price: baseProducts.find((candidate) => candidate.id === product.producto_id)?.price ?? '',
    })),
    ...baseProducts,
  ].filter((product, index, all) => all.findIndex((candidate) => candidate.id === product.id) === index)
}
