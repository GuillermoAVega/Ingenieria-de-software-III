import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { getPlatos, getPostres } from '../products/api'
import type { PlatoRespuesta, PostreRespuesta } from '../products/api'
import { getSections } from '../sections/api'
import type { SeccionRespuesta } from '../sections/api'
import { deleteMenuEjecutivo, getMenusEjecutivos } from './api'
import type { MenuEjecutivoRespuesta } from './api'

type ExecutiveMenusListState = {
  menus: MenuEjecutivoRespuesta[]
  platos: PlatoRespuesta[]
  postres: PostreRespuesta[]
  sections: SeccionRespuesta[]
  loading: boolean
  error: string | null
  search: string
  deletingId: number | null
  reloadToken: number
}

const initialState: ExecutiveMenusListState = {
  menus: [],
  platos: [],
  postres: [],
  sections: [],
  loading: true,
  error: null,
  search: '',
  deletingId: null,
  reloadToken: 0,
}

export function useExecutiveMenusList() {
  const [state, setState] = useState<ExecutiveMenusListState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadMenus() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const [menus, platos, postres, sections] = await Promise.all([
          getMenusEjecutivos(),
          getPlatos(),
          getPostres(),
          getSections(),
        ])
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          menus,
          platos,
          postres,
          sections,
          loading: false,
        }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadMenus()

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
      await deleteMenuEjecutivo(id)
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

  const platoById = new Map(state.platos.map((plato) => [plato.id, plato.nombre]))
  const postreById = new Map(state.postres.map((postre) => [postre.id, postre.nombre]))
  const seccionById = new Map(state.sections.map((section) => [section.id, section.nombre]))

  const search = state.search.trim().toLowerCase()
  const menus = state.menus.filter((menu) => {
    if (!search) return true
    const texto = [
      menu.nombre,
      platoById.get(menu.plato_id) ?? '',
      postreById.get(menu.postre_id) ?? '',
    ]
      .join(' ')
      .toLowerCase()
    return texto.includes(search)
  })

  return {
    state,
    menus,
    platoById,
    postreById,
    seccionById,
    updateSearch,
    remove,
  }
}
