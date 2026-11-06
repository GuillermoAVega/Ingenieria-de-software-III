import { useState } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { getErrorMessage, getFieldErrors } from '../../api/client'
import { createOrderItem, deleteOrderItem, updateOrderItem } from './api'
import type { OrderItem } from './types'
import type { ProductOption } from '../products/productOptions'

type OrderItemModal = { mode: 'new' } | { mode: 'edit'; item: OrderItem }

type OrderItemFormValues = {
  productoId: string
  productoQuery: string
  cantidad: string
  observaciones: string
}

type OrderItemsState = OrderItemFormValues & {
  productListOpen: boolean
  modal: OrderItemModal | null
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
  deletingId: number | null
  deliveryUpdatingId: number | null
}

const initialState: OrderItemsState = {
  modal: null,
  productoId: '',
  productoQuery: '',
  productListOpen: false,
  cantidad: '1',
  observaciones: '',
  saving: false,
  error: null,
  fieldErrors: {},
  deletingId: null,
  deliveryUpdatingId: null,
}

export function useOrderItems(comandaId: number, onChanged: () => void, products: ProductOption[]) {
  const [state, setState] = useState<OrderItemsState>(initialState)

  const openNew = () => {
    setState((previous) => ({
      ...previous,
      modal: { mode: 'new' },
      productoId: '',
      productoQuery: '',
      cantidad: '1',
      observaciones: '',
      error: null,
      fieldErrors: {},
    }))
  }

  const openEdit = (item: OrderItem) => {
    setState((previous) => ({
      ...previous,
      modal: { mode: 'edit', item },
      productoId: String(item.producto_id),
      productoQuery: products.find((product) => product.id === item.producto_id)?.name ?? `Producto #${item.producto_id}`,
      cantidad: String(item.cantidad),
      observaciones: item.observaciones ?? '',
      error: null,
      fieldErrors: {},
    }))
  }

  const closeModal = () => {
    setState((previous) => ({ ...previous, modal: null, saving: false, error: null }))
  }

  const openProductList = () => {
    setState((previous) => ({ ...previous, productListOpen: true }))
  }

  const closeProductList = () => {
    setState((previous) => ({ ...previous, productListOpen: false }))
  }

  const updateField = (field: keyof OrderItemFormValues, value: string) => {
    if (field === 'productoQuery') {
      const match = products.find((product) => product.name.toLocaleLowerCase() === value.trim().toLocaleLowerCase())
      setState((previous) => ({ ...previous, productoQuery: value, productoId: match ? String(match.id) : '' }))
      return
    }
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const save = async () => {
    if (!state.modal || state.saving) return

    if (!state.productoId) {
      setState((previous) => ({
        ...previous,
        error: 'Seleccioná un producto existente de la lista.',
      }))
      return
    }

    const payload = {
      producto_id: Number(state.productoId),
      cantidad: Number(state.cantidad),
      observaciones: state.observaciones.trim() || null,
    }

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    try {
      if (state.modal.mode === 'new') {
        await createOrderItem({ ...payload, comanda_id: comandaId })
      } else {
        await updateOrderItem(state.modal.item.id, payload)
      }
      setState((previous) => ({ ...previous, modal: null, saving: false }))
      onChanged()
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        saving: false,
        error: getErrorMessage(requestError),
        fieldErrors: getFieldErrors(requestError),
      }))
    }
  }

  const remove = async (item: OrderItem) => {
    setState((previous) => ({ ...previous, deletingId: item.id, error: null }))
    try {
      await deleteOrderItem(item.id)
      setState((previous) => ({ ...previous, deletingId: null }))
      onChanged()
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        deletingId: null,
        error: getErrorMessage(requestError),
      }))
    }
  }

  const toggleDelivered = async (item: OrderItem) => {
    setState((previous) => ({ ...previous, deliveryUpdatingId: item.id, error: null }))
    try {
      await updateOrderItem(item.id, { entregado: !item.entregado })
      setState((previous) => ({ ...previous, deliveryUpdatingId: null }))
      onChanged()
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        deliveryUpdatingId: null,
        error: getErrorMessage(requestError),
      }))
    }
  }

  return {
    state,
    openNew,
    openEdit,
    closeModal,
    openProductList,
    closeProductList,
    updateField,
    save,
    remove,
    toggleDelivered,
  }
}
