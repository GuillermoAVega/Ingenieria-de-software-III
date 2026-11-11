const MONTHS = [
  'enero',
  'febrero',
  'marzo',
  'abril',
  'mayo',
  'junio',
  'julio',
  'agosto',
  'septiembre',
  'octubre',
  'noviembre',
  'diciembre',
]

export function formatMonth(month: number): string {
  return MONTHS[month - 1] ?? ''
}

export function formatMonthYear(month: number, year: number): string {
  return `${formatMonth(month)} ${year}`
}

export function formatCurrency(value: number): string {
  return `$ ${value.toLocaleString('es-AR', { maximumFractionDigits: 2 })}`
}

export function formatCompactCurrency(value: number): string {
  if (Math.abs(value) >= 1000) {
    const miles = value / 1000
    return `$ ${miles.toLocaleString('es-AR', { maximumFractionDigits: 1 })}k`
  }
  return formatCurrency(value)
}

export function formatPercentage(value: number): string {
  return `${value.toLocaleString('es-AR', { maximumFractionDigits: 2 })} %`
}
