import type { Promotion } from './types'

export const DEMO_PROMOTIONS: Promotion[] = [
  {
    id: 'promo-1',
    name: 'Cerveza artesanal 10%',
    appliesTo: 'Bebidas',
    discountType: 'Porcentaje',
    discountValue: 10,
    from: '2026-10-01',
    to: '2026-10-31',
    active: true,
  },
  {
    id: 'promo-2',
    name: 'Happy hour de cócteles',
    appliesTo: 'Bebidas',
    discountType: 'Porcentaje',
    discountValue: 20,
    from: '2026-10-15',
    to: '2026-11-15',
    active: true,
  },
  {
    id: 'promo-3',
    name: 'Postre de la casa sin cargo',
    appliesTo: 'Postres',
    discountType: 'Monto fijo',
    discountValue: 6500,
    from: '2026-10-20',
    to: '2026-10-30',
    active: false,
  },
  {
    id: 'promo-4',
    name: 'Menú ejecutivo 2x1',
    appliesTo: 'Menú ejecutivo',
    discountType: 'Porcentaje',
    discountValue: 50,
    from: '2026-11-01',
    to: '2026-11-30',
    active: false,
  },
]
