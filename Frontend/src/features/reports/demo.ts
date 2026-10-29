import type { ProductRanking, ReportDefinition } from './types'

export const DEMO_REPORTS: ReportDefinition[] = [
  {
    slug: 'ventas',
    title: 'Ventas por período',
    description: 'Evolución de la facturación por día, semana o mes.',
  },
  {
    slug: 'productos',
    title: 'Productos más vendidos',
    description: 'Ranking de productos por unidades vendidas.',
  },
  {
    slug: 'comandas-mozo',
    title: 'Comandas por mozo',
    description: 'Cantidad de comandas y ventas atribuidas a cada mozo.',
  },
  {
    slug: 'ocupacion',
    title: 'Ocupación por sector',
    description: 'Uso de mesas y rotación por sector del salón.',
  },
  {
    slug: 'reservas',
    title: 'Reservas canceladas y ausencias',
    description: 'Seguimiento de cancelaciones y clientes ausentes.',
  },
  {
    slug: 'medios-pago',
    title: 'Ingresos por medio de pago',
    description: 'Distribución de cobros por medio de pago.',
  },
]

export const DEMO_PRODUCT_RANKING: ProductRanking[] = [
  { id: 'ranking-1', name: 'Milanesa napolitana', value: 148 },
  { id: 'ranking-2', name: 'Cerveza artesanal', value: 131 },
  { id: 'ranking-3', name: 'Ravioles de ricota', value: 96 },
  { id: 'ranking-4', name: 'Bife de chorizo', value: 84 },
  { id: 'ranking-5', name: 'Flan casero', value: 71 },
]
