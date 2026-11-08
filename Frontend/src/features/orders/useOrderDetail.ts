import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { navigate } from '../../app/navigation'
import { formatCurrency } from '../../utils/format'
import { createInvoice, createInvoiceLine, deleteOrder, getOrder, getOrderInvoices, updateOrder } from './api'
import type { Invoice, InvoiceLine, Order, OrderStatus } from './types'

type OrderDetailState = {
  order: Order | null
  invoice: Invoice | null
  loading: boolean
  error: string | null
  reloadToken: number
  statusSaving: boolean
  deleting: boolean
  invoiceModalOpen: boolean
  invoiceSaving: boolean
  invoiceError: string | null
  success: string | null
}

const initialState: OrderDetailState = {
  order: null,
  invoice: null,
  loading: true,
  error: null,
  reloadToken: 0,
  statusSaving: false,
  deleting: false,
  invoiceModalOpen: false,
  invoiceSaving: false,
  invoiceError: null,
  success: null,
}

export function useOrderDetail(id: number) {
  const [state, setState] = useState<OrderDetailState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadOrder() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const [order, invoices] = await Promise.all([getOrder(id), getOrderInvoices(id)])
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          order,
          invoice: invoices.find((invoice) => invoice.activo) ?? null,
          loading: false,
        }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadOrder()

    return () => {
      cancelled = true
    }
  }, [id, state.reloadToken])

  const reload = () => {
    setState((previous) => ({ ...previous, reloadToken: previous.reloadToken + 1 }))
  }

  const changeStatus = async (estado: OrderStatus) => {
    if (state.statusSaving) return

    setState((previous) => ({ ...previous, statusSaving: true, error: null, success: null }))
    try {
      await updateOrder(id, { estado })
      setState((previous) => ({
        ...previous,
        statusSaving: false,
        success: estado === 'cerrada' ? 'Comanda cerrada.' : 'Comanda reabierta.',
      }))
      reload()
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        statusSaving: false,
        error: getErrorMessage(requestError),
      }))
    }
  }

  const remove = async () => {
    if (state.deleting) return

    setState((previous) => ({ ...previous, deleting: true, error: null }))
    try {
      await deleteOrder(id)
      navigate('/comandas')
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        deleting: false,
        error: getErrorMessage(requestError),
      }))
    }
  }

  const openInvoiceModal = () => {
    setState((previous) => ({
      ...previous,
      invoiceModalOpen: true,
      invoiceError: null,
    }))
  }

  const closeInvoiceModal = () => {
    setState((previous) => ({ ...previous, invoiceModalOpen: false, invoiceError: null }))
  }

  const generateInvoice = async () => {
    if (!state.order || state.invoiceSaving) return

    const details = state.order.detalles
    setState((previous) => ({ ...previous, invoiceSaving: true, invoiceError: null, error: null }))

    let createdInvoiceId: number | null = null
    try {
      const invoice = await createInvoice(id)
      createdInvoiceId = invoice.id

      const lines: InvoiceLine[] = []
      for (const item of details) {
        lines.push(
          await createInvoiceLine({
            factura_id: invoice.id,
            detalle_comanda_id: item.id,
            cantidad: item.cantidad,
          }),
        )
      }

      // El servidor calcula precios y promociones: el total sale de precio_final
      const total = lines.reduce((sum, line) => sum + line.precio_final, 0)
      const promoted = lines.filter((line) => line.promocion_id !== null).length
      const promoText = promoted > 0 ? ` Promociones aplicadas en ${promoted} línea(s).` : ''

      setState((previous) => ({
        ...previous,
        invoiceModalOpen: false,
        invoiceSaving: false,
        success: `Factura #${invoice.id} generada por ${formatCurrency(total)}.${promoText}`,
      }))
      reload()
    } catch (requestError) {
      if (createdInvoiceId !== null) {
        reload()
      }
      setState((previous) => ({
        ...previous,
        invoiceSaving: false,
        invoiceError: getErrorMessage(requestError),
      }))
    }
  }

  return {
    state,
    reload,
    changeStatus,
    remove,
    openInvoiceModal,
    closeInvoiceModal,
    generateInvoice,
  }
}
