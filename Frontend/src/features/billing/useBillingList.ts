import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import type { Invoice } from '../orders/types'
import { getVouchers } from '../payments/api'
import { fromCents, toCents } from '../payments/money'
import { getPaymentStatus } from '../payments/status'
import type { PaymentVoucher } from '../payments/types'
import { getInvoices } from './api'
import type { BillingRow } from './types'

const PAGE_SIZE = 10

type BillingListState = {
  invoices: Invoice[]
  vouchers: PaymentVoucher[]
  loading: boolean
  error: string | null
  search: string
  date: string
  page: number
}

const initialState: BillingListState = {
  invoices: [],
  vouchers: [],
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
        const [invoices, vouchers] = await Promise.all([getInvoices(), getVouchers()])
        if (cancelled) return
        const sorted = [...invoices].sort((first, second) => second.id - first.id)
        setState((previous) => ({ ...previous, invoices: sorted, vouchers, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          invoices: [],
          vouchers: [],
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

  const paidCentsByInvoice = new Map<number, number>()
  for (const voucher of state.vouchers) {
    paidCentsByInvoice.set(
      voucher.factura_id,
      (paidCentsByInvoice.get(voucher.factura_id) ?? 0) + toCents(voucher.importe),
    )
  }
  const rows: BillingRow[] = state.invoices.map((invoice) => {
    const paid = fromCents(paidCentsByInvoice.get(invoice.id) ?? 0)
    return { ...invoice, paid, paymentStatus: getPaymentStatus(invoice.importe_total, paid) }
  })

  const search = state.search.trim().toLowerCase()
  const filtered = rows.filter((invoice) => {
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
