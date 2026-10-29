export type TableStatus = 'disponible' | 'ocupada'

export type Sector = {
  id: string
  name: string
  floor: string
  condition: string
  description: string
}

export type RestaurantTable = {
  id: string
  number: string
  seats: number
  status: TableStatus
  sectorId: string
}

export type SectorRecord = {
  id: number
  nombre: string
  apto_fumadores: boolean
  piso: string
  estado: boolean
}

export type SectorPayload = Omit<SectorRecord, 'id' | 'estado'>

export type TableRecord = {
  id: number
  capacidad: number
  disponible: boolean
  sector_id: number
  estado: boolean
}

export type TablePayload = Omit<TableRecord, 'id' | 'estado'>
