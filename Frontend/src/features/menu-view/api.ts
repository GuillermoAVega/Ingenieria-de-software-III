import { getProductoMenus } from '../daily-menu/api'
import type { ProductoMenuDetalle } from '../daily-menu/api'
import { getMenusEjecutivos } from '../executive-menus/api'
import type { MenuEjecutivoRespuesta } from '../executive-menus/api'
import { getBebidas, getMenusDelDia, getPlatos, getPostres } from '../products/api'
import type { BebidaRespuesta, MenuDelDiaListado, PlatoRespuesta, PostreRespuesta } from '../products/api'
import { getSections } from '../sections/api'
import type { SeccionRespuesta } from '../sections/api'

export type MenuViewData = {
  dailyMenus: ProductoMenuDetalle[]
  menusDelDia: MenuDelDiaListado[]
  executiveMenus: MenuEjecutivoRespuesta[]
  platos: PlatoRespuesta[]
  postres: PostreRespuesta[]
  bebidas: BebidaRespuesta[]
  sections: SeccionRespuesta[]
}

export async function getMenuViewData(): Promise<MenuViewData> {
  const [dailyMenus, menusDelDia, executiveMenus, platos, postres, bebidas, sections] = await Promise.all([
    getProductoMenus(),
    getMenusDelDia(),
    getMenusEjecutivos(),
    getPlatos(),
    getPostres(),
    getBebidas(),
    getSections(),
  ])

  return { dailyMenus, menusDelDia, executiveMenus, platos, postres, bebidas, sections }
}
