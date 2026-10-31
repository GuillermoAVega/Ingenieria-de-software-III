import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { deleteSection, getSections } from './api'
import type { SeccionRespuesta } from './api'

type SectionsListState = {
  sections: SeccionRespuesta[]
  loading: boolean
  error: string | null
  search: string
  deletingId: number | null
  reloadToken: number
}

const initialState: SectionsListState = {
  sections: [],
  loading: true,
  error: null,
  search: '',
  deletingId: null,
  reloadToken: 0,
}

export function useSectionsList() {
  const [state, setState] = useState<SectionsListState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadSections() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const sections = await getSections()
        if (cancelled) return
        setState((previous) => ({ ...previous, sections, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadSections()

    return () => {
      cancelled = true
    }
  }, [state.reloadToken])

  const updateSearch = (search: string) => {
    setState((previous) => ({ ...previous, search }))
  }

  const remove = async (id: number) => {
    setState((previous) => ({ ...previous, deletingId: id, error: null }))
    try {
      await deleteSection(id)
      setState((previous) => ({
        ...previous,
        deletingId: null,
        reloadToken: previous.reloadToken + 1,
      }))
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        deletingId: null,
        error: getErrorMessage(requestError),
      }))
    }
  }

  const search = state.search.trim().toLowerCase()
  const sections = search
    ? state.sections.filter((section) => section.nombre.toLowerCase().includes(search))
    : state.sections

  return {
    state,
    sections,
    updateSearch,
    remove,
  }
}
