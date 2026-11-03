import { useEffect, useState } from 'react'
import { getBebidas, getCombos, getMenusEjecutivos, getPlatos, getPostres } from '../products/api'
import { getProductoMenus } from '../daily-menu/api'
import { listCustomers } from '../reservations/api'
import { listSectors, listTables } from '../tables/api'
import type { SectorRecord, TableRecord } from '../tables/types'
import { listAttentions, listWaiters } from '../waiters/api'
import type { Attention, Waiter } from '../waiters/types'
import type { CustomerRecord } from '../reservations/types'
import type { Order } from './types'

export type OrderProductOption = {
  id: number
  name: string
  type: string
}

type OrderCatalogState = {
  products: OrderProductOption[]
  customers: CustomerRecord[]
  tables: TableRecord[]
  sectors: SectorRecord[]
  waiters: Waiter[]
  attentions: Attention[]
  loading: boolean
  error: string | null
}

const initialState: OrderCatalogState = {
  products: [], customers: [], tables: [], sectors: [], waiters: [], attentions: [], loading: true, error: null,
}

const legacyProductOptions: OrderProductOption[] = [
  { id: 1, name: 'Empanadas surtidas', type: 'Plato' },
  { id: 2, name: 'Pizza muzzarella', type: 'Plato' },
  { id: 3, name: 'Ensalada de estación', type: 'Plato' },
  { id: 4, name: 'Flan casero', type: 'Postre' },
]

export function useOrderCatalog() {
  const [state, setState] = useState<OrderCatalogState>(initialState)

  useEffect(() => {
    let cancelled = false
    async function loadCatalog() {
      try {
        const [platos, bebidas, postres, menus, combos, menusDelDia, customers, tables, sectors, waiters, attentions] = await Promise.all([
          getPlatos(), getBebidas(), getPostres(), getMenusEjecutivos(), getCombos(), getProductoMenus(), listCustomers(), listTables(), listSectors(), listWaiters(), listAttentions(),
        ])
        if (cancelled) return
        setState({
          products: [
            ...menusDelDia.map((product) => ({ id: product.producto_id, name: product.producto_nombre, type: 'Menú del día' })),
            ...platos.map((product) => ({ id: product.id, name: product.nombre, type: 'Plato' })),
            ...bebidas.map((product) => ({ id: product.id, name: product.nombre, type: 'Bebida' })),
            ...postres.map((product) => ({ id: product.id, name: product.nombre, type: 'Postre' })),
            ...menus.map((product) => ({ id: product.id, name: product.nombre, type: 'Menú ejecutivo' })),
            ...combos.map((product) => ({ id: product.id, name: product.nombre, type: 'Combo promocional' })),
            ...legacyProductOptions,
          ].filter((product, index, all) => all.findIndex((candidate) => candidate.id === product.id) === index),
          customers, tables, sectors, waiters, attentions, loading: false, error: null,
        })
      } catch (cause) {
        if (!cancelled) setState((previous) => ({ ...previous, loading: false, error: cause instanceof Error ? cause.message : 'No se pudieron cargar los datos de la comanda.' }))
      }
    }
    void loadCatalog()
    return () => { cancelled = true }
  }, [])

  const getAvailableWaiters = (order: Order): Waiter[] => {
    const tableIds = order.mesa_ids.length ? order.mesa_ids : order.mesa_id === null ? [] : [order.mesa_id]
    const sectorIds = new Set(state.tables.filter((table) => tableIds.includes(table.id)).map((table) => table.sector_id))
    const today = new Date().toISOString().slice(0, 10)
    const waiterIds = new Set(state.attentions
      .filter((attention) => sectorIds.has(attention.sector_id) && attention.estado && attention.fecha_desde <= today && (!attention.fecha_hasta || attention.fecha_hasta >= today))
      .map((attention) => attention.mozo_id))
    return state.waiters.filter((waiter) => waiter.estado && waiterIds.has(waiter.id))
  }

  return { state, getAvailableWaiters }
}
