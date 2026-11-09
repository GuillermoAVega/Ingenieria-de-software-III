export type ReportSlug =
  | 'ventas'
  | 'productos'
  | 'comandas-mozo'
  | 'ocupacion'
  | 'reservas'
  | 'medios-pago'

export type ReportDefinition = {
  slug: ReportSlug
  title: string
  description: string
}

export type ProductRanking = {
  id: string
  name: string
  value: number
}

export type SalesCountResponse = {
  anio: number
  por_mes: { mes: number; cantidad: number }[]
  por_dia_semana: { dia: number; cantidad: number }[]
}
