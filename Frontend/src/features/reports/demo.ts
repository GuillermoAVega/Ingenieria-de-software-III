import type { ReportDefinition } from './types'

export const DEMO_REPORTS: ReportDefinition[] = [
  {
    slug: 'comparativa-mensual',
    title: 'Comparativa con el mes anterior',
    description: 'Ventas por día del mes seleccionado contra el mes anterior.',
  },
  {
    slug: 'ventas',
    title: 'Cantidad de ventas',
    description: 'Ventas cobradas por mes y por día de la semana en un año.',
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
    title: 'Clientes ausentes a reservas',
    description: 'Clientes que faltaron a reservas y cantidad total de inasistencias.',
  },
  {
    slug: 'medios-pago',
    title: 'Ingresos por medio de pago',
    description: 'Distribución de cobros por medio de pago.',
  },
]
