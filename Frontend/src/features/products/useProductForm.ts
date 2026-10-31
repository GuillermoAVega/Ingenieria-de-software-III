import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { ApiError, getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { createPlato, getPlato, updatePlato } from './api'
import { DEMO_PRODUCTS } from './demo'
import { getSections } from '../sections/api'
import type { SeccionRespuesta } from '../sections/api'

export type ProductFormValues = {
  nombre: string
  precio: string
  cantPersonas: string
  seccionId: string
  descripcion: string
}

type ProductFormState = ProductFormValues & {
  sections: SeccionRespuesta[]
  sectionsLoading: boolean
  sectionsError: string | null
  loading: boolean
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

export function useProductForm(id?: string) {
  const numericId = id !== undefined ? Number(id) : null
  const isEditing = numericId !== null && Number.isInteger(numericId) && numericId > 0
  const isDemo = Boolean(id) && !isEditing
  const demoProduct = !isEditing && id ? DEMO_PRODUCTS.find((candidate) => candidate.id === id) : undefined

  const [state, setState] = useState<ProductFormState>(() => ({
    nombre: demoProduct?.name ?? '',
    precio: demoProduct ? String(demoProduct.price) : '',
    cantPersonas: '1',
    seccionId: '',
    descripcion: '',
    sections: [],
    sectionsLoading: true,
    sectionsError: null,
    loading: isEditing,
    saving: false,
    error: null,
    fieldErrors: {},
  }))

  useEffect(() => {
    let cancelled = false

    async function loadSections() {
      try {
        const sections = await getSections()
        if (cancelled) return
        setState((previous) => ({ ...previous, sections, sectionsLoading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          sectionsLoading: false,
          sectionsError: getErrorMessage(requestError),
        }))
      }
    }

    void loadSections()

    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!isEditing || numericId === null) {
      return
    }

    let cancelled = false
    const platoId = numericId

    async function loadPlato() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const plato = await getPlato(platoId)
        if (cancelled) return

        setState((previous) => ({
          ...previous,
          nombre: plato.nombre,
          precio: plato.precio,
          cantPersonas: String(plato.cant_personas),
          seccionId: plato.seccion_id === null ? '' : String(plato.seccion_id),
          descripcion: plato.descripcion ?? '',
        }))
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

    void loadPlato()

    return () => {
      cancelled = true
    }
  }, [isEditing, numericId])

  const updateField = (field: keyof ProductFormValues, value: string) => {
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.loading || state.saving || (isEditing && numericId === null)) {
      return
    }

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    const payload = {
      nombre: state.nombre.trim(),
      precio: Number(state.precio),
      descripcion: state.descripcion.trim() || null,
      cant_personas: Number(state.cantPersonas),
      seccion_id: state.seccionId.trim() ? Number(state.seccionId) : null,
    }

    try {
      if (isEditing && numericId !== null) {
        await updatePlato(numericId, payload)
      } else {
        await createPlato(payload)
      }
      navigate('/productos')
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        error:
          requestError instanceof ApiError && requestError.status === 404
            ? 'El plato que querés editar ya no existe.'
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
    isDemo,
    updateField,
    submit,
  }
}
