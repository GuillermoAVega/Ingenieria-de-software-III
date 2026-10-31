import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { getSections } from '../sections/api'
import type { SeccionRespuesta } from '../sections/api'
import {
  deleteBebida,
  deletePlato,
  deletePostre,
  getBebidas,
  getPlatos,
  getPostres,
} from './api'
import type { BebidaRespuesta, PlatoRespuesta, PostreRespuesta } from './api'

export const PRODUCT_TABS = [
  { id: 'platos', label: 'Platos' },
  { id: 'bebidas', label: 'Bebidas' },
  { id: 'postres', label: 'Postres' },
] as const

export type ProductTabId = (typeof PRODUCT_TABS)[number]['id']

export type ProductListItem = PlatoRespuesta | BebidaRespuesta | PostreRespuesta

type ProductsListState = {
  activeTab: ProductTabId
  products: ProductListItem[]
  loading: boolean
  error: string | null
  search: string
  sectionId: string
  sections: SeccionRespuesta[]
  sectionsLoading: boolean
  deletingId: number | null
  reloadToken: number
}

const initialState: ProductsListState = {
  activeTab: 'platos',
  products: [],
  loading: true,
  error: null,
  search: '',
  sectionId: '',
  sections: [],
  sectionsLoading: true,
  deletingId: null,
  reloadToken: 0,
}

function fetchProducts(tab: ProductTabId): Promise<ProductListItem[]> {
  if (tab === 'bebidas') return getBebidas()
  if (tab === 'postres') return getPostres()
  return getPlatos()
}

function deleteProduct(tab: ProductTabId, id: number): Promise<void> {
  if (tab === 'bebidas') return deleteBebida(id)
  if (tab === 'postres') return deletePostre(id)
  return deletePlato(id)
}

export function useProductsList() {
  const [state, setState] = useState<ProductsListState>(initialState)

  useEffect(() => {
    let cancelled = false

    async function loadSections() {
      try {
        const sections = await getSections()
        if (cancelled) return
        setState((previous) => ({ ...previous, sections, sectionsLoading: false }))
      } catch {
        if (cancelled) return
        setState((previous) => ({ ...previous, sectionsLoading: false }))
      }
    }

    void loadSections()

    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    const tab = state.activeTab

    async function loadProducts() {
      setState((previous) => ({ ...previous, loading: true, error: null }))
      try {
        const products = await fetchProducts(tab)
        if (cancelled) return
        setState((previous) => ({ ...previous, products, loading: false }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          products: [],
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadProducts()

    return () => {
      cancelled = true
    }
  }, [state.activeTab, state.reloadToken])

  const updateTab = (activeTab: string) => {
    setState((previous) => ({ ...previous, activeTab: activeTab as ProductTabId }))
  }

  const updateSearch = (search: string) => {
    setState((previous) => ({ ...previous, search }))
  }

  const updateSection = (sectionId: string) => {
    setState((previous) => ({ ...previous, sectionId }))
  }

  const remove = async (id: number) => {
    const tab = state.activeTab
    setState((previous) => ({ ...previous, deletingId: id, error: null }))
    try {
      await deleteProduct(tab, id)
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
  const products = state.products.filter((product) => {
    const matchesSearch = !search || product.nombre.toLowerCase().includes(search)
    const matchesSection =
      !state.sectionId || String(product.seccion_id ?? '') === state.sectionId
    return matchesSearch && matchesSection
  })

  return {
    state,
    products,
    updateTab,
    updateSearch,
    updateSection,
    remove,
  }
}
