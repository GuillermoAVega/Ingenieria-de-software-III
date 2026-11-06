import { useEffect, useState } from 'react'
import { loadProductOptions } from '../products/productOptions'
import type { ProductOption } from '../products/productOptions'
import { listCustomers } from '../reservations/api'
import { listSectors, listTables } from '../tables/api'
import type { SectorRecord, TableRecord } from '../tables/types'
import { listAttentions, listWaiters } from '../waiters/api'
import type { Attention, Waiter } from '../waiters/types'
import type { CustomerRecord } from '../reservations/types'
import type { Order } from './types'

type OrderCatalogState = {
  products: ProductOption[]
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

export function useOrderCatalog() {
  const [state, setState] = useState<OrderCatalogState>(initialState)

  useEffect(() => {
    let cancelled = false
    async function loadCatalog() {
      try {
        const [products, customers, tables, sectors, waiters, attentions] = await Promise.all([
          loadProductOptions(), listCustomers(), listTables(), listSectors(), listWaiters(), listAttentions(),
        ])
        if (cancelled) return
        setState({
          products,
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
