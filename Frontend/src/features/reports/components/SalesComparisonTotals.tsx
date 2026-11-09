import { Stat } from '../../../ui/ui'
import { formatCurrency, formatMonth, formatMonthYear } from '../format'
import { buildComparisonTotals } from '../totals'
import type { SalesComparisonReport } from '../types'

function periodHint(cutoffDay: number | null, month: number): string {
  if (cutoffDay === 0) return 'Sin días transcurridos.'
  if (cutoffDay === null) return 'Mes completo.'
  return `Del 1 al ${cutoffDay} de ${formatMonth(month)}.`
}

export function SalesComparisonTotals({ report }: { report: SalesComparisonReport }) {
  const totals = buildComparisonTotals(report)

  return (
    <div className="grid-2">
      <Stat
        label={`Total de ${formatMonthYear(report.mes, report.anio)}`}
        value={formatCurrency(totals.actual)}
        hint={periodHint(totals.cutoffDay, report.mes)}
      />
      <Stat
        label={`Total de ${formatMonthYear(report.mes_anterior, report.anio_anterior)}`}
        value={formatCurrency(totals.anterior)}
        hint={
          <>
            {periodHint(totals.cutoffDay, report.mes_anterior)}
            <br />
            Total completo del mes: {formatCurrency(totals.anteriorCompleto)}
          </>
        }
      />
    </div>
  )
}
