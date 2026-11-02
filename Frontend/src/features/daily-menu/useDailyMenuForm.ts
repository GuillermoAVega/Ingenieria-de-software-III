import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { ApiError, getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { getPlatos } from '../products/api'
import type { PlatoRespuesta } from '../products/api'
import { createProductoMenu, getProductoMenu, updateProductoMenuFecha } from './api'
import type { ProductoMenuDetalle } from './api'

export type DailyMenuFormField = 'fecha' | 'productoId'

type DailyMenuFormState = {
  fecha: string
  productoId: string
  producto: ProductoMenuDetalle | null
  platos: PlatoRespuesta[]
  platosLoading: boolean
  loading: boolean
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

/** Fecha local de hoy en formato YYYY-MM-DD (sin corrimiento por zona horaria). */
export function getTodayInputValue(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}

function createInitialState(isEditing: boolean): DailyMenuFormState {
  return {
    fecha: getTodayInputValue(),
    productoId: '',
    producto: null,
    platos: [],
    platosLoading: true,
    loading: isEditing,
    saving: false,
    error: null,
    fieldErrors: {},
  }
}

export function useDailyMenuForm(id?: string) {
  const numericId = id !== undefined ? Number(id) : null
  const isEditing = numericId !== null && Number.isInteger(numericId) && numericId > 0

  const [state, setState] = useState<DailyMenuFormState>(() => createInitialState(isEditing))

  useEffect(() => {
    let cancelled = false

    async function loadPlatos() {
      try {
        const platos = await getPlatos()
        if (cancelled) return
        setState((previous) => ({ ...previous, platos, platosLoading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          platos: [],
          platosLoading: false,
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

  useEffect(() => {
    if (!isEditing || numericId === null) {
      return
    }

    let cancelled = false
    const menuId = numericId

    async function loadMenu() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const menu = await getProductoMenu(menuId)
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          fecha: menu.fecha,
          productoId: String(menu.producto_id),
          producto: menu,
        }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          error:
            requestError instanceof ApiError && requestError.status === 404
              ? 'El menú del día que querés editar ya no existe.'
              : getErrorMessage(requestError),
          fieldErrors: getFieldErrors(requestError),
        }))
      } finally {
        if (!cancelled) {
          setState((previous) => ({ ...previous, loading: false }))
        }
      }
    }

    void loadMenu()

    return () => {
      cancelled = true
    }
  }, [isEditing, numericId])

  const updateField = (field: DailyMenuFormField, value: string) => {
    setState((previous) => {
      const fieldErrors = { ...previous.fieldErrors }
      delete fieldErrors[field]
      if (field === 'productoId') {
        delete fieldErrors.producto_id
      }
      return { ...previous, [field]: value, fieldErrors }
    })
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.loading || state.saving || (isEditing && numericId === null)) {
      return
    }

    const fieldErrors: ApiFieldErrors = {}
    if (!state.fecha) {
      fieldErrors.fecha = 'Elegí la fecha del menú.'
    }
    if (!isEditing && !state.productoId) {
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
    }))

    try {
      if (isEditing && numericId !== null) {
        await updateProductoMenuFecha(numericId, state.fecha)
      } else {
        await createProductoMenu({
          producto_id: Number(state.productoId),
          fecha: state.fecha,
        })
      }
      navigate('/menus')
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
    isEditing,
    updateField,
    submit,
  }
}
