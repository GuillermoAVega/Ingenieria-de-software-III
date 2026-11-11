import { ApiError, apiFetch } from '../../api/client'
import { getProductoMenus } from '../daily-menu/api'
import type { ProductoMenuDetalle } from '../daily-menu/api'
import { getMenusEjecutivos } from '../executive-menus/api'
import type { MenuEjecutivoRespuesta } from '../executive-menus/api'
import { getBebidas, getCombos, getMenusDelDia, getPlatos, getPostres } from '../products/api'
import type { BebidaRespuesta, ComboListado, MenuDelDiaListado, PlatoRespuesta, PostreRespuesta } from '../products/api'
import { getPromotions } from '../promotions/api'
import { getSections } from '../sections/api'
import type { SeccionRespuesta } from '../sections/api'
import type { Promotion } from '../promotions/types'

export type MenuViewData = {
  dailyMenus: ProductoMenuDetalle[]
  menusDelDia: MenuDelDiaListado[]
  executiveMenus: MenuEjecutivoRespuesta[]
  combos: ComboListado[]
  platos: PlatoRespuesta[]
  postres: PostreRespuesta[]
  bebidas: BebidaRespuesta[]
  sections: SeccionRespuesta[]
  promotions: Promotion[]
}

type MenuViewResponse = {
  menus_diarios: ProductoMenuDetalle[]
  menus_del_dia: MenuDelDiaListado[]
  menus_ejecutivos: MenuEjecutivoRespuesta[]
  combos: ComboListado[]
  platos: PlatoRespuesta[]
  postres: PostreRespuesta[]
  bebidas: BebidaRespuesta[]
  secciones: SeccionRespuesta[]
  promociones: Promotion[]
}

function mapResponse(response: MenuViewResponse): MenuViewData {
  return {
    dailyMenus: response.menus_diarios,
    menusDelDia: response.menus_del_dia,
    executiveMenus: response.menus_ejecutivos,
    combos: response.combos,
    platos: response.platos,
    postres: response.postres,
    bebidas: response.bebidas,
    sections: response.secciones,
    promotions: response.promociones,
  }
}

async function getLegacyMenuViewData(): Promise<MenuViewData> {
  const [dailyMenus, menusDelDia, executiveMenus, combos, platos, postres, bebidas, sections, promotions] =
    await Promise.all([
      getProductoMenus(),
      getMenusDelDia(),
      getMenusEjecutivos(),
      getCombos(),
      getPlatos(),
      getPostres(),
      getBebidas(),
      getSections(),
      getPromotions(false),
    ])

  return { dailyMenus, menusDelDia, executiveMenus, combos, platos, postres, bebidas, sections, promotions }
}

export async function getMenuViewData(): Promise<MenuViewData> {
  try {
    return mapResponse(await apiFetch<MenuViewResponse>('/carta'))
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return getLegacyMenuViewData()
    }
    throw error
  }
}
