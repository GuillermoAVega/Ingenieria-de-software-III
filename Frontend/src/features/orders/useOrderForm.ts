import { useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { createOrder } from './api'

export type OrderFormValues = {
  mesaId: string
  clienteId: string
  reservaId: string
}

type OrderFormState = OrderFormValues & {
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

function createInitialState(): OrderFormState {
  return {
    mesaId: '',
    clienteId: '',
    reservaId: '',
    saving: false,
    error: null,
    fieldErrors: {},
  }
}

export function useOrderForm(reservationId?: string) {
  const [state, setState] = useState<OrderFormState>(() => ({
    ...createInitialState(),
    reservaId: reservationId ?? '',
  }))

  const updateField = (field: keyof OrderFormValues, value: string) => {
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.saving) return

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    try {
      const order = await createOrder(reservationId
        ? { reserva_id: Number(reservationId) }
        : {
            mesa_ids: [Number(state.mesaId)],
            cliente_id: state.clienteId.trim() ? Number(state.clienteId) : null,
            reserva_id: state.reservaId.trim() ? Number(state.reservaId) : null,
          })
      navigate(`/comandas/${order.id}`)
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
    updateField,
    submit,
  }
}
