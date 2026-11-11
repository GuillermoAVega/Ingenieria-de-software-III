import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { deletePaymentMethod, getPaymentMethods } from './api'
import type { PaymentMethod } from './types'

const PAGE_SIZE = 10

type PaymentMethodsListState = {
  methods: PaymentMethod[]
  loading: boolean
  error: string | null
  search: string
  page: number
  deletingId: number | null
  reloadToken: number
}

const initialState: PaymentMethodsListState = {
  methods: [],
  loading: true,
  error: null,
  search: '',
  page: 1,
  deletingId: null,
  reloadToken: 0,
}

export function usePaymentMethodsList() {
  const [state, setState] = useState<PaymentMethodsListState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadMethods() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const methods = await getPaymentMethods()
        if (cancelled) return
        setState((previous) => ({ ...previous, methods, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          methods: [],
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadMethods()

    return () => {
      cancelled = true
    }
  }, [state.reloadToken])

  const updateSearch = (search: string) => {
    setState((previous) => ({ ...previous, search, page: 1 }))
  }

  const changePage = (page: number) => {
    setState((previous) => ({ ...previous, page }))
  }

  const remove = async (id: number) => {
    setState((previous) => ({ ...previous, deletingId: id, error: null }))
    try {
      await deletePaymentMethod(id)
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
  const filtered = search
    ? state.methods.filter((method) => method.descripcion.toLowerCase().includes(search))
    : state.methods
  const total = filtered.length
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const page = Math.min(state.page, totalPages)

  return {
    state,
    methods: filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE),
    total,
    page,
    pageSize: PAGE_SIZE,
    updateSearch,
    changePage,
    remove,
  }
}
