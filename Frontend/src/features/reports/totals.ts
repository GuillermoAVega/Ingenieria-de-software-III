import type { SalesComparisonDay, SalesComparisonReport } from './types'

export type ComparisonTotals = {
  actual: number
  anterior: number
  cutoffDay: number | null
}

/**
 * Día de corte de un mes concreto:
 * - Mes actual: hasta el día de hoy.
 * - Mes pasado: todos sus días.
 * - Mes futuro: ningún día transcurrido.
 */
export function cutoffDayForMonth(
  anio: number,
  mes: number,
  today: Date = new Date(),
): number | null {
  const anioActual = today.getFullYear()
  const mesActual = today.getMonth() + 1

  if (anio === anioActual && mes === mesActual) {
    return today.getDate()
  }

  const esMesPasado =
    anio < anioActual || (anio === anioActual && mes < mesActual)

  return esMesPasado ? null : 0
}

/**
 * Día de corte de la comparación:
 * - Mes actual: hasta el día de hoy.
 * - Mes pasado: todos sus días.
 * - Mes futuro: ningún día transcurrido.
 */
export function comparisonCutoffDay(
  report: SalesComparisonReport,
  today: Date = new Date(),
): number | null {
  return cutoffDayForMonth(report.anio, report.mes, today)
}

function sumarHasta(dias: SalesComparisonDay[], cutoffDay: number | null): number {
  if (cutoffDay === 0) return 0

  const total = dias.reduce(
    (acumulado, punto) =>
      cutoffDay === null || punto.dia <= cutoffDay
        ? acumulado + punto.importe
        : acumulado,
    0,
  )
  return Math.round(total * 100) / 100
}

export function buildComparisonTotals(
  report: SalesComparisonReport,
  today: Date = new Date(),
): ComparisonTotals {
  const cutoffDay = comparisonCutoffDay(report, today)
  return {
    actual: sumarHasta(report.actual, cutoffDay),
    anterior: sumarHasta(report.anterior, cutoffDay),
    cutoffDay,
  }
}
