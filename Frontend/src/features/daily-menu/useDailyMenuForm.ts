import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { getErrorMessage, getFieldErrors } from '../../api/client'
import { getPlatos } from '../products/api'
import type { PlatoRespuesta } from '../products/api'
import { createProductoMenu } from './api'
import type { ProductoMenuRespuesta } from './api'

export type DailyMenuFormField = 'fecha' | 'productoId'

type DailyMenuFormState = {
  fecha: string
  productoId: string
  platos: PlatoRespuesta[]
  loading: boolean
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
  created: ProductoMenuRespuesta | null
}

/** Fecha local de hoy en formato YYYY-MM-DD (sin corrimiento por zona horaria). */
export function getTodayInputValue(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}

function createInitialState(): DailyMenuFormState {
  return {
    fecha: getTodayInputValue(),
    productoId: '',
    platos: [],
    loading: true,
    saving: false,
    error: null,
    fieldErrors: {},
    created: null,
  }
}

export function useDailyMenuForm() {
  const [state, setState] = useState<DailyMenuFormState>(createInitialState)

  useEffect(() => {
    let cancelled = false

    async function loadPlatos() {
      try {
        const platos = await getPlatos()
        if (cancelled) return
        setState((previous) => ({ ...previous, platos, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          platos: [],
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadPlatos()

    return () => {
      cancelled = true
    }
  }, [])

  const updateField = (field: DailyMenuFormField, value: string) => {
    setState((previous) => {
      const fieldErrors = { ...previous.fieldErrors }
      delete fieldErrors[field]
      if (field === 'productoId') {
        delete fieldErrors.producto_id
      }
      return { ...previous, [field]: value, fieldErrors, created: null }
    })
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.loading || state.saving) {
      return
    }

    const fieldErrors: ApiFieldErrors = {}
    if (!state.fecha) {
      fieldErrors.fecha = 'Elegí la fecha del menú.'
    }
    if (!state.productoId) {
      fieldErrors.producto_id = 'Elegí un plato para el menú del día.'
    }
    if (Object.keys(fieldErrors).length > 0) {
      setState((previous) => ({ ...previous, error: null, fieldErrors }))
      return
    }

    setState((previous) => ({
      ...previous,
      saving: true,
      error: null,
      fieldErrors: {},
      created: null,
    }))

    try {
      const created = await createProductoMenu({
        producto_id: Number(state.productoId),
        fecha: state.fecha,
      })
      setState((previous) => ({ ...previous, created, productoId: '' }))
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

  const reset = () => {
    setState((previous) => ({
      ...previous,
      fecha: getTodayInputValue(),
      productoId: '',
      error: null,
      fieldErrors: {},
      created: null,
    }))
  }

  return {
    state,
    updateField,
    submit,
    reset,
  }
}
