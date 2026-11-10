import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { ApiError, getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { createPaymentMethod, getPaymentMethod, updatePaymentMethod } from './api'

export type PaymentMethodFormValues = {
  descripcion: string
}

type PaymentMethodFormState = PaymentMethodFormValues & {
  loading: boolean
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

export function usePaymentMethodForm(id?: string) {
  const numericId = id !== undefined ? Number(id) : null
  const isEditing = numericId !== null && Number.isInteger(numericId) && numericId > 0

  const [state, setState] = useState<PaymentMethodFormState>(() => ({
    descripcion: '',
    loading: isEditing,
    saving: false,
    error: null,
    fieldErrors: {},
  }))

  useEffect(() => {
    if (!isEditing || numericId === null) {
      return
    }

    let cancelled = false
    const methodId = numericId

    async function loadMethod() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const method = await getPaymentMethod(methodId)
        if (cancelled) return
        setState((previous) => ({ ...previous, descripcion: method.descripcion }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          error: getErrorMessage(requestError),
          fieldErrors: getFieldErrors(requestError),
        }))
      } finally {
        if (!cancelled) {
          setState((previous) => ({ ...previous, loading: false }))
        }
      }
    }

    void loadMethod()

    return () => {
      cancelled = true
    }
  }, [isEditing, numericId])

  const updateField = (field: keyof PaymentMethodFormValues, value: string) => {
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.loading || state.saving) {
      return
    }

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    const payload = { descripcion: state.descripcion.trim() }

    try {
      if (isEditing && numericId !== null) {
        await updatePaymentMethod(numericId, payload)
      } else {
        await createPaymentMethod(payload)
      }
      navigate('/medios-de-pago')
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        error:
          requestError instanceof ApiError && requestError.status === 404
            ? 'El medio de pago que querés editar ya no existe.'
            : requestError instanceof ApiError && requestError.status === 400
              ? 'Ya existe un medio de pago con esa descripción.'
              : getErrorMessage(requestError),
        fieldErrors: getFieldErrors(requestError),
      }))
    } finally {
      setState((previous) => ({ ...previous, saving: false }))
    }
  }

  return {
    state,
    isEditing,
    updateField,
    submit,
  }
}
