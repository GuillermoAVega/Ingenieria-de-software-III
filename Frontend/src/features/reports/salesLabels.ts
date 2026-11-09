export type ChartRow = { label: string; value: number; share: number }

export const MONTH_LABELS = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
]

export const WEEKDAY_LABELS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

const YEAR_OPTIONS_COUNT = 10

export function getYearOptions(currentYear: number): number[] {
  return Array.from({ length: YEAR_OPTIONS_COUNT }, (_, index) => currentYear - index)
}

const SHARE_FORMAT = new Intl.NumberFormat('es-AR', { style: 'percent', maximumFractionDigits: 1 })

export function countTotal(items: { cantidad: number }[]): number {
  return items.reduce((total, item) => total + item.cantidad, 0)
}

export function toChartRows(items: { cantidad: number }[], labels: string[]): ChartRow[] {
  const total = countTotal(items)
  return items.map((item, index) => ({
    label: labels[index],
    value: item.cantidad,
    share: total > 0 ? item.cantidad / total : 0,
  }))
}

export function formatCountWithShare(row: ChartRow): string {
  return `${row.value} (${SHARE_FORMAT.format(row.share)})`
}
