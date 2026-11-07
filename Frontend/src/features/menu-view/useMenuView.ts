import { useEffect, useMemo, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { todayISO } from '../../utils/format'
import { getMenuViewData } from './api'
import type { MenuViewData } from './api'
import type { MenuViewCategory, MenuViewItem, MenuViewState } from './types'

function createInitialState(): MenuViewState {
  return {
    date: todayISO(),
    loading: true,
    error: null,
    data: null,
  }
}

function groupBySection(
  items: MenuViewItem[],
  sections: MenuViewData['sections'],
) {
  const sectionById = new Map(sections.map((section) => [section.id, section]))
  const itemsBySection = new Map<number, MenuViewItem[]>()
  const unsectionedItems: MenuViewItem[] = []

  for (const item of items) {
    const section = item.seccionId === null ? undefined : sectionById.get(item.seccionId)
    if (!section) {
      unsectionedItems.push(item)
      continue
    }

    const sectionItems = itemsBySection.get(section.id) ?? []
    sectionItems.push(item)
    itemsBySection.set(section.id, sectionItems)
  }

  const sectionGroups = sections
    .filter((section) => itemsBySection.has(section.id))
    .sort((left, right) => left.posicion - right.posicion)
    .map((section) => ({
      id: section.id,
      nombre: section.nombre,
      subtitulo: section.subtitulo,
      items: itemsBySection.get(section.id) ?? [],
    }))

  return { sectionGroups, unsectionedItems }
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

  const categories = useMemo<MenuViewCategory[]>(() => {
    if (!state.data) return []

    const { dailyMenus, executiveMenus, platos, postres, bebidas, sections } = state.data
    const platosById = new Map(platos.map((plato) => [plato.id, plato]))
    const postresById = new Map(postres.map((postre) => [postre.id, postre]))

    const dailyItems = dailyMenus
      .filter(
        (menu) =>
          menu.fecha === state.date &&
          menu.producto_tipo === 'plato' &&
          !menu.producto_dado_de_baja,
      )
      .flatMap((menu) => {
        const plato = platosById.get(menu.producto_id)
        return plato
          ? [
              {
                key: `daily-${menu.id}`,
                nombre: plato.nombre,
                descripcion: plato.descripcion,
                precio: plato.precio,
                seccionId: plato.seccion_id,
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

    return [
      { id: 'daily', title: 'Menú del día', items: dailyItems },
      { id: 'executive', title: 'Menús ejecutivos', items: executiveItems },
      { id: 'dishes', title: 'Platos', items: productItems(platos) },
      { id: 'desserts', title: 'Postres', items: productItems(postres) },
      { id: 'drinks', title: 'Bebidas', items: productItems(bebidas) },
    ].map(({ id, title, items }) => ({
      id,
      title,
      ...groupBySection(items, sections),
    }))
  }, [state.data, state.date])

  return { state, categories }
}
