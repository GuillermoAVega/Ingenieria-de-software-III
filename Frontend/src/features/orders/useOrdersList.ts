import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { deleteOrder, getOrders } from './api'
import type { Order, OrderStatus } from './types'

const PAGE_SIZE = 10

type OrdersListState = {
  orders: Order[]
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
        const orders = await getOrders()
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          orders: [...orders].sort((first, second) => second.id - first.id),
          loading: false,
        }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          orders: [],
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadOrders()

    return () => {
      cancelled = true
    }
  }, [state.reloadToken])

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

  const search = state.search.trim().toLowerCase()
  const filteredOrders = state.orders.filter((order) => {
    const matchesStatus = !state.statusFilter || order.estado === state.statusFilter
    const matchesSearch =
      !search ||
      String(order.id).includes(search) ||
      String(order.mesa_id).includes(search) ||
      String(order.mozo_id).includes(search)
    return matchesStatus && matchesSearch
  })

  const total = filteredOrders.length
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const page = Math.min(state.page, totalPages)
  const orders = filteredOrders.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return {
    state,
    orders,
    total,
    page,
    pageSize: PAGE_SIZE,
    updateSearch,
    updateStatus,
    changePage,
    remove,
  }
}
