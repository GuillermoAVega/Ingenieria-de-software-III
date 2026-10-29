import type { Section } from './types'

export const DEMO_SECTIONS: Section[] = [
  {
    id: 'sec-1',
    name: 'Salón principal',
    floor: 'Planta baja',
    condition: 'No fumadores',
    description: 'Sector principal con mesas para el servicio de salón.',
    tableCount: 8,
  },
  {
    id: 'sec-2',
    name: 'Terraza',
    floor: 'Planta baja',
    condition: 'Apto fumadores',
    description: 'Mesas al aire libre, disponible todo el año.',
    tableCount: 6,
  },
  {
    id: 'sec-3',
    name: 'Barra',
    floor: 'Planta baja',
    condition: 'No fumadores',
    description: 'Servicio rápido en barra para comensales individuales.',
    tableCount: 4,
  },
  {
    id: 'sec-4',
    name: 'Salón privado',
    floor: 'Planta alta',
    condition: 'No fumadores',
    description: 'Espacio reservado para eventos y grupos pequeños.',
    tableCount: 2,
  },
]
