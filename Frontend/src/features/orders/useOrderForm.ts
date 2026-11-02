import { useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { currentTime, todayISO } from '../../utils/format'
import { createOrder } from './api'

export type OrderFormValues = {
  fecha: string
  hora: string
  mesaId: string
  mozoId: string
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
    fecha: todayISO(),
    hora: currentTime(),
    mesaId: '',
    mozoId: '',
    clienteId: '',
    reservaId: '',
    saving: false,
    error: null,
    fieldErrors: {},
  }
}

export function useOrderForm() {
  const [state, setState] = useState<OrderFormState>(createInitialState)

  const updateField = (field: keyof OrderFormValues, value: string) => {
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.saving) return

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    try {
      const order = await createOrder({
        fecha: state.fecha,
        hora: state.hora,
        mesa_id: Number(state.mesaId),
        mozo_id: Number(state.mozoId),
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
