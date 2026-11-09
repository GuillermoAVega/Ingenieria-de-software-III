import { getProductoMenus } from '../daily-menu/api'
import {
  getBebidas,
  getCombos,
  getMenusDelDia,
  getMenusEjecutivos,
  getPlatos,
  getPostres,
} from './api'

export type ProductOption = {
  id: number
  name: string
  type: string
  price: string
}

/** Carga los productos reales disponibles para comandas y reservas. */
export async function loadProductOptions(): Promise<ProductOption[]> {
  const [platos, bebidas, postres, menus, combos, asignacionesMenuDelDia, menusDelDia] =
    await Promise.all([
      getPlatos(),
      getBebidas(),
      getPostres(),
      getMenusEjecutivos(),
      getCombos(),
      getProductoMenus(),
      getMenusDelDia(),
    ])

  const baseProducts: ProductOption[] = [
    ...platos.map((product) => ({ id: product.id, name: product.nombre, type: 'Plato', price: String(product.precio) })),
    ...bebidas.map((product) => ({ id: product.id, name: product.nombre, type: 'Bebida', price: String(product.precio) })),
    ...postres.map((product) => ({ id: product.id, name: product.nombre, type: 'Postre', price: String(product.precio) })),
    ...menus.map((product) => ({ id: product.id, name: product.nombre, type: 'Menú ejecutivo', price: String(product.precio) })),
    ...combos.map((product) => ({ id: product.id, name: product.nombre, type: 'Combo promocional', price: String(product.precio) })),
  ]

  const menusDelDiaPorId = new Map(menusDelDia.map((product) => [product.id, product]))
  const opcionesMenuDelDia: ProductOption[] = asignacionesMenuDelDia.flatMap(
    (asignacion) => {
      const menu = menusDelDiaPorId.get(asignacion.menu_del_dia_id)
      if (!menu || asignacion.menu_del_dia_dado_de_baja) return []

      return [{
        id: menu.id,
        name: menu.nombre,
        type: 'Menú del día',
        price: String(menu.precio),
      }]
    },
  )

  return [
    ...opcionesMenuDelDia,
    ...baseProducts,
  ].filter((product, index, all) => all.findIndex((candidate) => candidate.id === product.id) === index)
}
