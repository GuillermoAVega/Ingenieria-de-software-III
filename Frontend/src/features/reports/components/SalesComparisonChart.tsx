import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { formatCompactCurrency, formatCurrency, formatMonthYear } from '../format'
import { cutoffDayForMonth } from '../totals'
import type { SalesComparisonReport } from '../types'

type ChartPoint = {
  dia: number
  actual: number | null
  anterior: number | null
}

function incluyeDia(dia: number, cutoffDay: number | null): boolean {
  if (cutoffDay === 0) return false
  return cutoffDay === null || dia <= cutoffDay
}

function buildChartData(
  report: SalesComparisonReport,
  today: Date = new Date(),
): ChartPoint[] {
  const actual = new Map(report.actual.map((punto) => [punto.dia, punto.importe]))
  const anterior = new Map(report.anterior.map((punto) => [punto.dia, punto.importe]))
  const cutoffActual = cutoffDayForMonth(report.anio, report.mes, today)
  const cutoffAnterior = cutoffDayForMonth(
    report.anio_anterior,
    report.mes_anterior,
    today,
  )
  const cantidadDias = Math.max(report.actual.length, report.anterior.length)

  return Array.from({ length: cantidadDias }, (_, index) => {
    const dia = index + 1
    return {
      dia,
      actual: incluyeDia(dia, cutoffActual) ? (actual.get(dia) ?? null) : null,
      anterior: incluyeDia(dia, cutoffAnterior)
        ? (anterior.get(dia) ?? null)
        : null,
    }
  })
}

export function SalesComparisonChart({ report }: { report: SalesComparisonReport }) {
  const data = buildChartData(report)
  const actualLabel = formatMonthYear(report.mes, report.anio)
  const anteriorLabel = formatMonthYear(report.mes_anterior, report.anio_anterior)
  const intervaloTicks = data.length > 20 ? 4 : 1

  return (
    <div
      className="chart-wrap"
      role="img"
      aria-label={`Ventas por día de ${actualLabel} comparadas con ${anteriorLabel}`}
    >
      <ResponsiveContainer width="100%" height={320}>
        <LineChart
          data={data}
          margin={{ top: 8, right: 16, bottom: 8, left: 0 }}
          accessibilityLayer
        >
          <CartesianGrid vertical={false} stroke="var(--c-border)" strokeDasharray="3 3" />
          <XAxis
            dataKey="dia"
            interval={intervaloTicks}
            tick={{ fill: 'var(--c-text-3)', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: 'var(--c-border)' }}
          />
          <YAxis
            width={72}
            tick={{ fill: 'var(--c-text-3)', fontSize: 12 }}
            tickFormatter={(value: number) => formatCompactCurrency(value)}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            cursor={{ stroke: 'var(--c-border-strong)', strokeDasharray: '3 3' }}
            labelFormatter={(label) => `Día ${label}`}
            formatter={(value) => formatCurrency(Number(value))}
            contentStyle={{
              background: 'var(--c-surface)',
              border: '1px solid var(--c-border)',
              borderRadius: 'var(--radius)',
              boxShadow: 'var(--shadow-md)',
              fontFamily: 'var(--font-sans)',
            }}
            labelStyle={{ color: 'var(--c-text-2)' }}
            itemStyle={{ color: 'var(--c-text)' }}
          />
          <Legend
            wrapperStyle={{
              fontFamily: 'var(--font-sans)',
              fontSize: 13,
              color: 'var(--c-text-2)',
            }}
          />
          <Line
            type="monotone"
            dataKey="actual"
            name={actualLabel}
            stroke="var(--c-accent)"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="anterior"
            name={anteriorLabel}
            stroke="var(--c-text-3)"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
