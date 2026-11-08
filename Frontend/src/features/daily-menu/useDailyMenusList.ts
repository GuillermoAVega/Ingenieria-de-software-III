import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { normalizeText } from '../promotions/text'
import { deleteProductoMenu, getProductoMenus } from './api'
import type { ProductoMenuDetalle } from './api'

type DailyMenusListState = {
  menus: ProductoMenuDetalle[]
  loading: boolean
  error: string | null
  search: string
  dateFilter: string
  deletingId: number | null
  reloadToken: number
}

const initialState: DailyMenusListState = {
  menus: [],
  loading: true,
  error: null,
  search: '',
  dateFilter: '',
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

  const updateDateFilter = (dateFilter: string) => {
    setState((previous) => ({ ...previous, dateFilter }))
  }

  const clearFilters = () => {
    setState((previous) => ({ ...previous, search: '', dateFilter: '' }))
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

  // El texto busca solo por menú del día (sin distinguir tildes); la fecha tiene su propio filtro
  const search = normalizeText(state.search)
  const menus = state.menus.filter((menu) => {
    if (state.dateFilter && menu.fecha !== state.dateFilter) return false
    return !search || normalizeText(menu.menu_del_dia_nombre).includes(search)
  })
  const hasFilters = state.search !== '' || state.dateFilter !== ''

  return {
    state,
    menus,
    hasFilters,
    updateSearch,
    updateDateFilter,
    clearFilters,
    remove,
  }
}
