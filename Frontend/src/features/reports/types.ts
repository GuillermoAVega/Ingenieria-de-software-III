export type ReportSlug =
  | 'comparativa-mensual'
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

export type SalesComparisonDay = {
  dia: number
  importe: number
}

export type SalesComparisonReport = {
  anio: number
  mes: number
  anio_anterior: number
  mes_anterior: number
  actual: SalesComparisonDay[]
  anterior: SalesComparisonDay[]
}

export type SalesComparisonParams = {
  anio: number
  mes: number
}

export type SalesCountResponse = {
  anio: number
  por_mes: { mes: number; cantidad: number }[]
  por_dia_semana: { dia: number; cantidad: number }[]
}

export type WaiterOrderReport = {
  desde: string
  hasta: string
  por_mozo: {
    mozo_id: number
    nombre: string
    cantidad_comandas: number
    importe_ventas: number
  }[]
}
