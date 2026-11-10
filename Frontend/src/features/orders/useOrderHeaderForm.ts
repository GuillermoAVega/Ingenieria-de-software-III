import { useState } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { getErrorMessage, getFieldErrors } from '../../api/client'
import { updateOrder } from './api'
import type { Order } from './types'

type OrderHeaderFormValues = {
  mesaId: string
  mozoId: string
  clienteId: string
  reservaId: string
}

type OrderHeaderFormState = OrderHeaderFormValues & {
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

function createInitialState(order: Order): OrderHeaderFormState {
  return {
    mesaId: String(order.mesa_id),
    mozoId: order.mozo_id === null ? '' : String(order.mozo_id),
    clienteId: order.cliente_id === null ? '' : String(order.cliente_id),
    reservaId: order.reserva_id === null ? '' : String(order.reserva_id),
    saving: false,
    error: null,
    fieldErrors: {},
  }
}

export function useOrderHeaderForm(order: Order, onSaved: () => void) {
  const [state, setState] = useState<OrderHeaderFormState>(() => createInitialState(order))

  const updateField = (field: keyof OrderHeaderFormValues, value: string) => {
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const isDirty =
    state.mesaId !== String(order.mesa_id) ||
    state.mozoId !== (order.mozo_id === null ? '' : String(order.mozo_id)) ||
    state.clienteId !== (order.cliente_id === null ? '' : String(order.cliente_id)) ||
    state.reservaId !== (order.reserva_id === null ? '' : String(order.reserva_id))

  const submit = async () => {
    if (!isDirty || state.saving) return

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    try {
      await updateOrder(order.id, {
        mesa_id: Number(state.mesaId),
        mozo_id: state.mozoId.trim() ? Number(state.mozoId) : null,
        cliente_id: state.clienteId.trim() ? Number(state.clienteId) : null,
        reserva_id: state.reservaId.trim() ? Number(state.reservaId) : null,
      })
      onSaved()
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        error: getErrorMessage(requestError),
        fieldErrors: getFieldErrors(requestError),
      }))
    } finally {
      setState((previous) => ({ ...previous, saving: false }))
    }
  }

  return {
    state,
    isDirty,
    updateField,
    submit,
  }
}
