import type { Customer } from './types'

export const DEMO_CUSTOMERS: Customer[] = [
  {
    id: 'customer-1',
    dni: '10000001',
    name: 'Valentina Ortiz',
    phone: '280 455-0187',
    visits: 12,
    lastVisit: '2026-10-16',
  },
  {
    id: 'customer-2',
    dni: '10000002',
    name: 'Federico Luna',
    phone: '280 455-0233',
    visits: 8,
    lastVisit: '2026-10-16',
  },
  {
    id: 'customer-3',
    dni: '10000003',
    name: 'Julieta Navarro',
    phone: '280 455-0420',
    visits: 5,
    lastVisit: '2026-10-21',
  },
  {
    id: 'customer-4',
    dni: '10000004',
    name: 'Esteban Molina',
    phone: '280 455-0518',
    visits: 3,
    lastVisit: '2026-10-15',
  },
  {
    id: 'customer-5',
    dni: '10000005',
    name: 'Agustina Peralta',
    phone: '280 455-0609',
    visits: 9,
    lastVisit: '2026-10-09',
  },
]

export type FakeVisitData = {
  visits: number
  lastVisit: string
}

export function generateFakeVisitData(customerDni: string): FakeVisitData {
  let seed = 0
  for (const character of customerDni) {
    seed = (seed * 31 + character.charCodeAt(0)) >>> 0
  }

  const daysAgo = (seed >>> 8) % 30
  const lastVisit = new Date()
  lastVisit.setDate(lastVisit.getDate() - daysAgo)
  const formattedDate = [
    lastVisit.getFullYear(),
    String(lastVisit.getMonth() + 1).padStart(2, '0'),
    String(lastVisit.getDate()).padStart(2, '0'),
  ].join('-')

  return {
    visits: (seed % 12) + 1,
    lastVisit: formattedDate,
  }
}
