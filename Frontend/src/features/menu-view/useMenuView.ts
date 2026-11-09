import { useEffect, useMemo, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { todayISO } from '../../utils/format'
import { getMenuViewData } from './api'
import type { MenuViewData } from './api'
import type { MenuViewItem, MenuViewSectionGroup, MenuViewState } from './types'

function createInitialState(): MenuViewState {
  return {
    date: todayISO(),
    loading: true,
    error: null,
    data: null,
  }
}

/**
 * Agrupa los ítems por sección. Los ítems sin sección (o con una sección
 * inexistente) se descartan: la carta solo muestra secciones.
 */
function groupBySection(
  items: MenuViewItem[],
  sections: MenuViewData['sections'],
): MenuViewSectionGroup[] {
  const sectionById = new Map(sections.map((section) => [section.id, section]))
  const itemsBySection = new Map<number, MenuViewItem[]>()

  for (const item of items) {
    if (item.seccionId === null) continue
    const section = sectionById.get(item.seccionId)
    if (!section) continue

    const sectionItems = itemsBySection.get(section.id) ?? []
    sectionItems.push(item)
    itemsBySection.set(section.id, sectionItems)
  }

  return sections
    .filter((section) => itemsBySection.has(section.id))
    .sort((left, right) => left.posicion - right.posicion)
    .map((section) => ({
      id: section.id,
      nombre: section.nombre,
      subtitulo: section.subtitulo,
      items: itemsBySection.get(section.id) ?? [],
    }))
}

export function useMenuView() {
  const [state, setState] = useState<MenuViewState>(createInitialState)

  useEffect(() => {
    let cancelled = false

    async function loadMenu() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const data = await getMenuViewData()
        if (cancelled) return
        setState((previous) => ({ ...previous, data, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          data: null,
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadMenu()

    return () => {
      cancelled = true
    }
  }, [])

  const sections = useMemo<MenuViewSectionGroup[]>(() => {
    if (!state.data) return []

    const {
      dailyMenus,
      menusDelDia,
      executiveMenus,
      platos,
      postres,
      bebidas,
      sections: allSections,
    } = state.data
    const platosById = new Map(platos.map((plato) => [plato.id, plato]))
    const postresById = new Map(postres.map((postre) => [postre.id, postre]))
    const menusDelDiaById = new Map(menusDelDia.map((menu) => [menu.id, menu]))

    const dailyItems = dailyMenus
      .filter((assignment) => assignment.fecha === state.date && !assignment.menu_del_dia_dado_de_baja)
      .flatMap((assignment) => {
        const menu = menusDelDiaById.get(assignment.menu_del_dia_id)
        return menu
          ? [
              {
                key: `daily-${assignment.id}`,
                nombre: menu.nombre,
                descripcion: menu.descripcion,
                precio: menu.precio,
                seccionId: menu.seccion_id,
              },
            ]
          : []
      })

    const executiveItems = executiveMenus
      .filter((menu) => !menu.dado_de_baja)
      .map((menu) => ({
        key: `executive-${menu.id}`,
        nombre: menu.nombre,
        descripcion: menu.descripcion,
        precio: menu.precio,
        seccionId: menu.seccion_id,
        platoNombre: platosById.get(menu.plato_id)?.nombre,
        postreNombre: postresById.get(menu.postre_id)?.nombre,
      }))

    const productItems = (products: typeof platos | typeof postres | typeof bebidas) =>
      products
        .filter((product) => !product.dado_de_baja)
        .map((product) => ({
          key: `${product.tipo}-${product.id}`,
          nombre: product.nombre,
          descripcion: product.descripcion,
          precio: product.precio,
          seccionId: product.seccion_id,
        }))

    const items = [
      ...dailyItems,
      ...executiveItems,
      ...productItems(platos),
      ...productItems(postres),
      ...productItems(bebidas),
    ]

    return groupBySection(items, allSections)
  }, [state.data, state.date])

  return { state, sections }
}
