import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { ApiError, getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { createSection, getSection, updateSection } from './api'
import { DEMO_SECTIONS } from './demo'

export type SectionFormValues = {
  nombre: string
  subtitulo: string
  posicion: string
}

type SectionFormState = SectionFormValues & {
  loading: boolean
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

export function useSectionForm(id?: string) {
  const numericId = id !== undefined ? Number(id) : null
  const isEditing = numericId !== null && Number.isInteger(numericId) && numericId > 0
  const isDemo = Boolean(id) && !isEditing
  const demoSection = !isEditing && id ? DEMO_SECTIONS.find((candidate) => candidate.id === id) : undefined

  const [state, setState] = useState<SectionFormState>(() => ({
    nombre: demoSection?.name ?? '',
    subtitulo: demoSection?.description ?? '',
    posicion: '1',
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
    const sectionId = numericId

    async function loadSection() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const section = await getSection(sectionId)
        if (cancelled) return

        setState((previous) => ({
          ...previous,
          nombre: section.nombre,
          subtitulo: section.subtitulo ?? '',
          posicion: String(section.posicion),
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

    void loadSection()

    return () => {
      cancelled = true
    }
  }, [isEditing, numericId])

  const updateField = (field: keyof SectionFormValues, value: string) => {
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
      subtitulo: state.subtitulo.trim() || null,
      posicion: Number(state.posicion),
    }

    try {
      if (isEditing && numericId !== null) {
        await updateSection(numericId, payload)
      } else {
        await createSection(payload)
      }
      navigate('/secciones')
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        error:
          requestError instanceof ApiError && requestError.status === 404
            ? 'La sección que querés editar ya no existe.'
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
