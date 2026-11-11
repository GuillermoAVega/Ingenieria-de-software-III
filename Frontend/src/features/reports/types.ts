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

export type ProductSalesRow = {
  producto_id: number
  nombre: string
  tipo: string
  unidades: number
  importe: number
}

export type ProductSalesReport = {
  desde: string
  hasta: string
  limite: number
  productos: ProductSalesRow[]
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

export type AbsentClientRow = {
  dni: string
  nombre: string
  apellido: string
  ultima_fecha: string
  ultima_hora: string
  cantidad_ausencias: number
}

export type AbsentClientsReport = {
  clientes: AbsentClientRow[]
}

export type OccupancyBySectorRow = {
  sector_id: number
  sector: string
  mesas_atendidas: number
  cantidad_comandas: number
  rotacion: number
}

export type OccupancyBySectorReport = {
  desde: string
  hasta: string
  por_sector: OccupancyBySectorRow[]
}

export type PaymentMethodUsageRow = {
  medio_pago_id: number
  descripcion: string
  cantidad_comprobantes: number
  importe: number
  importe_promedio: number
  porcentaje_uso: number
  porcentaje_importe: number
}

export type PaymentMethodReport = {
  desde: string
  hasta: string
  total_comprobantes: number
  total_importe: number
  importe_promedio: number
  medios: PaymentMethodUsageRow[]
}
