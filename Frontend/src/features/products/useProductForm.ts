import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { ApiError, getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import {
  createBebida,
  createPlato,
  createPostre,
  getBebida,
  getPlato,
  getPostre,
  updateBebida,
  updatePlato,
  updatePostre,
} from './api'
import { getSections } from '../sections/api'
import type { SeccionRespuesta } from '../sections/api'

export type ProductType = 'platos' | 'bebidas' | 'postres'

export type ProductFormValues = {
  nombre: string
  precio: string
  cantPersonas: string
  esAlcoholica: boolean
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

const initialState: ProductFormState = {
  nombre: '',
  precio: '',
  cantPersonas: '1',
  esAlcoholica: false,
  seccionId: '',
  descripcion: '',
  sections: [],
  sectionsLoading: true,
  sectionsError: null,
  loading: false,
  saving: false,
  error: null,
  fieldErrors: {},
}

function getProduct(tipo: ProductType, id: number) {
  if (tipo === 'bebidas') return getBebida(id)
  if (tipo === 'postres') return getPostre(id)
  return getPlato(id)
}

export function useProductForm(tipo: ProductType, id?: string) {
  const numericId = id !== undefined ? Number(id) : null
  const isEditing = numericId !== null && Number.isInteger(numericId) && numericId > 0

  const [state, setState] = useState<ProductFormState>(() => ({
    ...initialState,
    loading: isEditing,
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
    const productoId = numericId

    async function loadProduct() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const product = await getProduct(tipo, productoId)
        if (cancelled) return

        setState((previous) => ({
          ...previous,
          nombre: product.nombre,
          precio: product.precio,
          cantPersonas:
            product.tipo === 'plato' ? String(product.cant_personas) : previous.cantPersonas,
          esAlcoholica:
            product.tipo === 'bebida' ? product.es_alcoholica : previous.esAlcoholica,
          seccionId: product.seccion_id === null ? '' : String(product.seccion_id),
          descripcion: product.descripcion ?? '',
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

    void loadProduct()

    return () => {
      cancelled = true
    }
  }, [isEditing, numericId, tipo])

  const updateField = (field: keyof ProductFormValues, value: string | boolean) => {
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.loading || state.saving || (isEditing && numericId === null)) {
      return
    }

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    const base = {
      nombre: state.nombre.trim(),
      precio: Number(state.precio),
      descripcion: state.descripcion.trim() || null,
      seccion_id: state.seccionId.trim() ? Number(state.seccionId) : null,
    }

    try {
      if (tipo === 'bebidas') {
        const payload = { ...base, es_alcoholica: state.esAlcoholica }
        if (isEditing && numericId !== null) {
          await updateBebida(numericId, payload)
        } else {
          await createBebida(payload)
        }
      } else if (tipo === 'postres') {
        if (isEditing && numericId !== null) {
          await updatePostre(numericId, base)
        } else {
          await createPostre(base)
        }
      } else {
        const payload = { ...base, cant_personas: Number(state.cantPersonas) }
        if (isEditing && numericId !== null) {
          await updatePlato(numericId, payload)
        } else {
          await createPlato(payload)
        }
      }
      navigate('/productos')
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        error:
          requestError instanceof ApiError && requestError.status === 404
            ? 'El producto que querés editar ya no existe.'
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
