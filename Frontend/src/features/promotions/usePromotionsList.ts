import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { deletePromotion, getPromotions } from './api'
import type { Promotion } from './types'

export type PromotionStatusFilter = 'activas' | 'todas' | 'bajas'

type PromotionsListState = {
  promotions: Promotion[]
  loading: boolean
  error: string | null
  search: string
  statusFilter: PromotionStatusFilter
  deletingId: number | null
  reloadToken: number
}

const initialState: PromotionsListState = {
  promotions: [],
  loading: true,
  error: null,
  search: '',
  statusFilter: 'activas',
  deletingId: null,
  reloadToken: 0,
}

export function usePromotionsList() {
  const [state, setState] = useState<PromotionsListState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadPromotions() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const promotions = await getPromotions(state.statusFilter !== 'activas')
        if (cancelled) return
        setState((previous) => ({ ...previous, promotions, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadPromotions()

    return () => {
      cancelled = true
    }
  }, [state.statusFilter, state.reloadToken])

  const updateSearch = (search: string) => {
    setState((previous) => ({ ...previous, search }))
  }

  const updateStatusFilter = (statusFilter: PromotionStatusFilter) => {
    setState((previous) => ({ ...previous, statusFilter }))
  }

  const remove = async (id: number) => {
    setState((previous) => ({ ...previous, deletingId: id, error: null }))
    try {
      await deletePromotion(id)
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

  const term = state.search.trim().toLowerCase()
  const promotions = state.promotions.filter(
    (promotion) =>
      (state.statusFilter !== 'bajas' || promotion.dado_de_baja) &&
      (!term || promotion.nombre.toLowerCase().includes(term)),
  )

  return { state, promotions, updateSearch, updateStatusFilter, remove }
}
