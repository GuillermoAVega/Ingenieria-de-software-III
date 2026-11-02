import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { ApiError, getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { getPlatos, getPostres } from '../products/api'
import type { PlatoRespuesta, PostreRespuesta } from '../products/api'
import { getSections } from '../sections/api'
import type { SeccionRespuesta } from '../sections/api'
import { createMenuEjecutivo, getMenuEjecutivo, updateMenuEjecutivo } from './api'

export type ExecutiveMenuFormField =
  | 'nombre'
  | 'precio'
  | 'descripcion'
  | 'seccionId'
  | 'platoId'
  | 'postreId'

type ExecutiveMenuFormState = {
  nombre: string
  precio: string
  descripcion: string
  seccionId: string
  platoId: string
  postreId: string
  platos: PlatoRespuesta[]
  postres: PostreRespuesta[]
  sections: SeccionRespuesta[]
  loading: boolean
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

const CAMPOS_API: Record<ExecutiveMenuFormField, string> = {
  nombre: 'nombre',
  precio: 'precio',
  descripcion: 'descripcion',
  seccionId: 'seccion_id',
  platoId: 'plato_id',
  postreId: 'postre_id',
}

function createInitialState(isEditing: boolean): ExecutiveMenuFormState {
  return {
    nombre: '',
    precio: '',
    descripcion: '',
    seccionId: '',
    platoId: '',
    postreId: '',
    platos: [],
    postres: [],
    sections: [],
    loading: isEditing,
    saving: false,
    error: null,
    fieldErrors: {},
  }
}

export function useExecutiveMenuForm(id?: string) {
  const numericId = id !== undefined ? Number(id) : null
  const isEditing = numericId !== null && Number.isInteger(numericId) && numericId > 0

  const [state, setState] = useState<ExecutiveMenuFormState>(() =>
    createInitialState(isEditing),
  )

  useEffect(() => {
    let cancelled = false

    async function loadCatalogos() {
      try {
        const [platos, postres, sections] = await Promise.all([
          getPlatos(),
          getPostres(),
          getSections(),
        ])
        if (cancelled) return
        setState((previous) => ({ ...previous, platos, postres, sections }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({ ...previous, error: getErrorMessage(requestError) }))
      }
    }

    void loadCatalogos()

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
        const menu = await getMenuEjecutivo(menuId)
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          nombre: menu.nombre,
          precio: menu.precio,
          descripcion: menu.descripcion ?? '',
          seccionId: menu.seccion_id === null ? '' : String(menu.seccion_id),
          platoId: String(menu.plato_id),
          postreId: String(menu.postre_id),
        }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          error:
            requestError instanceof ApiError && requestError.status === 404
              ? 'El menú ejecutivo que querés editar ya no existe.'
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

  const updateField = (field: ExecutiveMenuFormField, value: string) => {
    setState((previous) => {
      const fieldErrors = { ...previous.fieldErrors }
      delete fieldErrors[CAMPOS_API[field]]
      delete fieldErrors[field]
      return { ...previous, [field]: value, fieldErrors }
    })
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.loading || state.saving || (isEditing && numericId === null)) {
      return
    }

    const fieldErrors: ApiFieldErrors = {}
    if (!state.nombre.trim()) {
      fieldErrors.nombre = 'Ingresá el nombre del menú ejecutivo.'
    }
    const precio = Number(state.precio)
    if (!state.precio.trim() || Number.isNaN(precio) || precio <= 0) {
      fieldErrors.precio = 'Ingresá un precio mayor a 0.'
    }
    if (!state.platoId) {
      fieldErrors.plato_id = 'Elegí un plato.'
    }
    if (!state.postreId) {
      fieldErrors.postre_id = 'Elegí un postre.'
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

    const payload = {
      nombre: state.nombre.trim(),
      precio,
      descripcion: state.descripcion.trim() || null,
      seccion_id: state.seccionId.trim() ? Number(state.seccionId) : null,
      plato_id: Number(state.platoId),
      postre_id: Number(state.postreId),
    }

    try {
      if (isEditing && numericId !== null) {
        await updateMenuEjecutivo(numericId, payload)
      } else {
        await createMenuEjecutivo(payload)
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
