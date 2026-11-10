import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import type { Invoice } from '../orders/types'
import { getInvoices } from './api'

const PAGE_SIZE = 10

type BillingListState = {
  invoices: Invoice[]
  loading: boolean
  error: string | null
  search: string
  date: string
  page: number
}

const initialState: BillingListState = {
  invoices: [],
  loading: true,
  error: null,
  search: '',
  date: '',
  page: 1,
}

export function useBillingList() {
  const [state, setState] = useState<BillingListState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadInvoices() {
      try {
        const invoices = await getInvoices()
        if (cancelled) return
        const sorted = [...invoices].sort((first, second) => second.id - first.id)
        setState((previous) => ({ ...previous, invoices: sorted, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          invoices: [],
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadInvoices()

    return () => {
      cancelled = true
    }
  }, [])

  const updateSearch = (search: string) => {
    setState((previous) => ({ ...previous, search, page: 1 }))
  }

  const updateDate = (date: string) => {
    setState((previous) => ({ ...previous, date, page: 1 }))
  }

  const changePage = (page: number) => {
    setState((previous) => ({ ...previous, page }))
  }

  const search = state.search.trim().toLowerCase()
  const filtered = state.invoices.filter((invoice) => {
    const matchesDate = !state.date || invoice.fecha_hora_emision.startsWith(state.date)
    const matchesSearch =
      !search ||
      String(invoice.id).includes(search) ||
      String(invoice.comanda_id).includes(search)
    return matchesDate && matchesSearch
  })

  const total = filtered.length
  const totalAmount = filtered.reduce((sum, invoice) => sum + Number(invoice.importe_total), 0)
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const page = Math.min(state.page, totalPages)

  return {
    state,
    invoices: filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE),
    total,
    totalAmount,
    averageTicket: total > 0 ? totalAmount / total : 0,
    page,
    pageSize: PAGE_SIZE,
    updateSearch,
    updateDate,
    changePage,
  }
}
