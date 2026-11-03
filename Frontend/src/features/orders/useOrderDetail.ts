import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { navigate } from '../../app/navigation'
import { formatCurrency } from '../../utils/format'
import { createInvoice, createInvoiceLine, deleteOrder, getOrder, getOrderInvoices, updateOrder, updateOrderItem } from './api'
import type { Invoice, Order, OrderStatus } from './types'

type OrderDetailState = {
  order: Order | null
  invoice: Invoice | null
  loading: boolean
  error: string | null
  reloadToken: number
  statusSaving: boolean
  deleting: boolean
  invoiceModalOpen: boolean
  invoicePrices: Record<number, string>
  invoiceSaving: boolean
  invoiceError: string | null
  success: string | null
  closeConfirmationOpen: boolean
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
  invoicePrices: {},
  invoiceSaving: false,
  invoiceError: null,
  success: null,
  closeConfirmationOpen: false,
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

  const requestClose = () => {
    if (!state.order) return
    const pendientes = state.order.detalles.some((detalle) => !detalle.entregado)
    if (pendientes) {
      setState((previous) => ({ ...previous, closeConfirmationOpen: true }))
      return
    }
    void changeStatus('cerrada')
  }

  const cancelClose = () => {
    setState((previous) => ({ ...previous, closeConfirmationOpen: false }))
  }

  const confirmCloseWithPending = async () => {
    if (!state.order || state.statusSaving) return
    const pendientes = state.order.detalles.filter((detalle) => !detalle.entregado)
    setState((previous) => ({ ...previous, statusSaving: true, closeConfirmationOpen: false, error: null, success: null }))
    try {
      for (const detalle of pendientes) {
        await updateOrderItem(detalle.id, { entregado: true })
      }
      await updateOrder(id, { estado: 'cerrada' })
      setState((previous) => ({ ...previous, statusSaving: false, success: 'Comanda cerrada y productos pendientes marcados como entregados.' }))
      reload()
    } catch (requestError) {
      setState((previous) => ({ ...previous, statusSaving: false, error: getErrorMessage(requestError) }))
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
      invoicePrices: Object.fromEntries(
        (previous.order?.detalles ?? []).map((item) => [item.id, '']),
      ),
      invoiceError: null,
    }))
  }

  const closeInvoiceModal = () => {
    setState((previous) => ({ ...previous, invoiceModalOpen: false, invoiceError: null }))
  }

  const setInvoicePrice = (itemId: number, value: string) => {
    setState((previous) => ({
      ...previous,
      invoicePrices: { ...previous.invoicePrices, [itemId]: value },
    }))
  }

  const generateInvoice = async () => {
    if (!state.order || state.invoiceSaving) return

    const details = state.order.detalles
    const missingPrice = details.some((item) => !state.invoicePrices[item.id]?.trim())
    if (missingPrice) {
      setState((previous) => ({
        ...previous,
        invoiceError: 'Ingresá el precio unitario de todos los productos.',
      }))
      return
    }

    setState((previous) => ({ ...previous, invoiceSaving: true, invoiceError: null, error: null }))

    let createdInvoiceId: number | null = null
    try {
      const invoice = await createInvoice(id)
      createdInvoiceId = invoice.id

      for (const item of details) {
        await createInvoiceLine({
          factura_id: invoice.id,
          detalle_comanda_id: item.id,
          precio_unitario: Number(state.invoicePrices[item.id]),
          cantidad: item.cantidad,
        })
      }

      const total = details.reduce(
        (sum, item) => sum + Number(state.invoicePrices[item.id]) * item.cantidad,
        0,
      )

      setState((previous) => ({
        ...previous,
        invoiceModalOpen: false,
        invoiceSaving: false,
        success: `Factura #${invoice.id} generada por ${formatCurrency(total)}.`,
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
    requestClose,
    cancelClose,
    confirmCloseWithPending,
    remove,
    openInvoiceModal,
    closeInvoiceModal,
    setInvoicePrice,
    generateInvoice,
  }
}
