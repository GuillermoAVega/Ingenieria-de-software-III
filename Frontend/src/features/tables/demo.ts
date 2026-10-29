import type { RestaurantTable, Sector } from './types'

export const DEMO_SECTORS: Sector[] = [
  {
    id: 'sector-salon',
    name: 'Salón principal',
    floor: 'Planta baja',
    condition: 'No fumadores',
    description: 'Sector principal del salón.',
  },
  {
    id: 'sector-terraza',
    name: 'Terraza',
    floor: 'Planta baja',
    condition: 'Apto fumadores',
    description: 'Mesas al aire libre.',
  },
]

export const DEMO_TABLES: RestaurantTable[] = [
  { id: 'mesa-1', number: 'Mesa 1', seats: 4, status: 'ocupada', sectorId: 'sector-salon' },
  { id: 'mesa-2', number: 'Mesa 2', seats: 2, status: 'disponible', sectorId: 'sector-salon' },
  { id: 'mesa-3', number: 'Mesa 3', seats: 4, status: 'ocupada', sectorId: 'sector-salon' },
  { id: 'mesa-4', number: 'Mesa 4', seats: 6, status: 'disponible', sectorId: 'sector-salon' },
  { id: 'mesa-5', number: 'Mesa 5', seats: 2, status: 'disponible', sectorId: 'sector-salon' },
  { id: 'mesa-6', number: 'Mesa 6', seats: 4, status: 'disponible', sectorId: 'sector-salon' },
  { id: 'mesa-7', number: 'Mesa 7', seats: 4, status: 'ocupada', sectorId: 'sector-salon' },
  { id: 'mesa-8', number: 'Mesa 8', seats: 8, status: 'disponible', sectorId: 'sector-salon' },
  { id: 'mesa-9', number: 'Mesa 9', seats: 2, status: 'disponible', sectorId: 'sector-terraza' },
  { id: 'mesa-10', number: 'Mesa 10', seats: 2, status: 'ocupada', sectorId: 'sector-terraza' },
  { id: 'mesa-11', number: 'Mesa 11', seats: 4, status: 'disponible', sectorId: 'sector-terraza' },
  { id: 'mesa-12', number: 'Mesa 12', seats: 4, status: 'ocupada', sectorId: 'sector-terraza' },
  { id: 'mesa-13', number: 'Mesa 13', seats: 6, status: 'disponible', sectorId: 'sector-terraza' },
  { id: 'mesa-14', number: 'Mesa 14', seats: 4, status: 'disponible', sectorId: 'sector-terraza' },
]
