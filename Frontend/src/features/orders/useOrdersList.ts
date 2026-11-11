import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { deleteOrder, getOrdersPage } from './api'
import type { OrderListItem, OrderStatus } from './types'

const PAGE_SIZE = 10

type OrdersListState = {
  orders: OrderListItem[]
  total: number
  loading: boolean
  error: string | null
  statusFilter: '' | OrderStatus
  search: string
  page: number
  deletingId: number | null
  reloadToken: number
}

const initialState: OrdersListState = {
  orders: [],
  total: 0,
  loading: true,
  error: null,
  statusFilter: '',
  search: '',
  page: 1,
  deletingId: null,
  reloadToken: 0,
}

export function useOrdersList() {
  const [state, setState] = useState<OrdersListState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadOrders() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const result = await getOrdersPage({
          page: state.page,
          pageSize: PAGE_SIZE,
          status: state.statusFilter,
          search: state.search,
        })
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          orders: result.items,
          total: result.total,
          page: result.pagina,
          loading: false,
        }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          orders: [],
          total: 0,
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    const timeoutId = window.setTimeout(() => void loadOrders(), state.search ? 250 : 0)

    return () => {
      cancelled = true
      window.clearTimeout(timeoutId)
    }
  }, [state.page, state.reloadToken, state.search, state.statusFilter])

  const updateSearch = (search: string) => {
    setState((previous) => ({ ...previous, search, page: 1 }))
  }

  const updateStatus = (value: string) => {
    setState((previous) => ({ ...previous, statusFilter: value as '' | OrderStatus, page: 1 }))
  }

  const changePage = (page: number) => {
    setState((previous) => ({ ...previous, page }))
  }

  const remove = async (id: number) => {
    setState((previous) => ({ ...previous, deletingId: id, error: null }))
    try {
      await deleteOrder(id)
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

  return {
    state,
    orders: state.orders,
    total: state.total,
    page: state.page,
    pageSize: PAGE_SIZE,
    updateSearch,
    updateStatus,
    changePage,
    remove,
  }
}
