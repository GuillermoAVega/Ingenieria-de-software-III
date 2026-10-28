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
