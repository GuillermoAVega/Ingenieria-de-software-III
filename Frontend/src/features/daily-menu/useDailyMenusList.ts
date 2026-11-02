import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { formatDate, tipoLabel } from '../menus/format'
import { deleteProductoMenu, getProductoMenus } from './api'
import type { ProductoMenuDetalle } from './api'

type DailyMenusListState = {
  menus: ProductoMenuDetalle[]
  loading: boolean
  error: string | null
  search: string
  deletingId: number | null
  reloadToken: number
}

const initialState: DailyMenusListState = {
  menus: [],
  loading: true,
  error: null,
  search: '',
  deletingId: null,
  reloadToken: 0,
}

export function useDailyMenusList() {
  const [state, setState] = useState<DailyMenusListState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadMenus() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const menus = await getProductoMenus()
        if (cancelled) return
        setState((previous) => ({ ...previous, menus, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          menus: [],
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadMenus()

    return () => {
      cancelled = true
    }
  }, [state.reloadToken])

  const updateSearch = (search: string) => {
    setState((previous) => ({ ...previous, search }))
  }

  const remove = async (id: number) => {
    setState((previous) => ({ ...previous, deletingId: id, error: null }))
    try {
      await deleteProductoMenu(id)
      setState((previous) => ({
        ...previous,
        deletingId: null,
        reloadToken: previous.reloadToken + 1,
      }))
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        deletingId: null,
        error: getErrorMessage(requestError),
      }))
    }
  }

  const search = state.search.trim().toLowerCase()
  const menus = search
    ? state.menus.filter((menu) => {
        const texto = [
          menu.producto_nombre,
          tipoLabel(menu.producto_tipo),
          menu.fecha,
          formatDate(menu.fecha),
        ]
          .join(' ')
          .toLowerCase()
        return texto.includes(search)
      })
    : state.menus

  return {
    state,
    menus,
    updateSearch,
    remove,
  }
}
