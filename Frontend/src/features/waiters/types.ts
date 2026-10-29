export type Waiter = {
  id: number
  name: string
  nro_legajo: number
  estado: boolean
}

export type WaiterPayload = {
  nombre: string
  nro_legajo: number
}

export type Attention = {
  id: number
  fecha_desde: string
  fecha_hasta: string | null
  mozo_id: number
  sector_id: number
  estado: boolean
}

export type AttentionPayload = {
  fecha_desde: string
  mozo_id: number
  sector_id: number
}
