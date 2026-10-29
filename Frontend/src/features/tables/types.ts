export type TableStatus = 'disponible' | 'ocupada' | 'reservada'

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
