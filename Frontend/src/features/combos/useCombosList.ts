import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { getBebidas, getPlatos, getPostres } from '../products/api'
import type { ComboListado, ComboComponente } from '../products/api'
import { deleteCombo, getCombos } from './api'
import type { ComboSource } from './types'
import { normalizeText } from '../promotions/text'

type CombosListState = {
  combos: ComboListado[]
  names: Record<string, string>
  loading: boolean
  error: string | null
  deletingId: number | null
  reloadToken: number
}

const initialState: CombosListState = {
  combos: [],
  names: {},
  loading: true,
  error: null,
  deletingId: null,
  reloadToken: 0,
}

export const nameKey = (source: ComboSource, id: number) => `${source}:${id}`

export function useCombosList(search: string, sectionId = '') {
  const [state, setState] = useState<CombosListState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function load() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const [combos, platos, bebidas, postres] = await Promise.all([
          getCombos(),
          getPlatos(),
          getBebidas(),
          getPostres(),
        ])
        if (cancelled) return
        const names: Record<string, string> = {}
        platos.forEach((item) => (names[nameKey('platos', item.id)] = item.nombre))
        bebidas.forEach((item) => (names[nameKey('bebidas', item.id)] = item.nombre))
        postres.forEach((item) => (names[nameKey('postres', item.id)] = item.nombre))
        setState((previous) => ({ ...previous, combos, names, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void load()

    return () => {
      cancelled = true
    }
  }, [state.reloadToken])

  const remove = async (id: number) => {
    setState((previous) => ({ ...previous, deletingId: id, error: null }))
    try {
      await deleteCombo(id)
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

  /** Texto "2 × Milanesa, 1 × Gaseosa" con los componentes y sus cantidades. */
  const describe = (combo: ComboListado): string => {
    const parts: string[] = []
    const add = (source: ComboSource, items: ComboComponente[]) => {
      items.forEach((item) => {
        parts.push(`${item.cantidad} × ${state.names[nameKey(source, item.id)] ?? `#${item.id}`}`)
      })
    }
    add('platos', combo.platos)
    add('bebidas', combo.bebidas)
    add('postres', combo.postres)
    return parts.join(', ')
  }

  /** Nombres de los platos, bebidas y postres que componen el combo. */
  const componentNames = (combo: ComboListado): string[] => {
    const names: string[] = []
    const add = (source: ComboSource, items: ComboComponente[]) => {
      items.forEach((item) => {
        const name = state.names[nameKey(source, item.id)]
        if (name) names.push(name)
      })
    }
    add('platos', combo.platos)
    add('bebidas', combo.bebidas)
    add('postres', combo.postres)
    return names
  }

  // Los combos dados de baja no se muestran. La búsqueda coincide con el nombre
  // del combo o con el de alguno de sus componentes, sin distinguir tildes.
  const term = normalizeText(search)
  const combos = state.combos.filter(
    (combo) =>
      !combo.dado_de_baja &&
      (!term ||
        [combo.nombre, ...componentNames(combo)].some((name) =>
          normalizeText(name).includes(term),
        )) &&
      (!sectionId || String(combo.seccion_id) === sectionId),
  )

  return { state, combos, remove, describe }
}
