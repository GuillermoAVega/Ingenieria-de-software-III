import { Card, Stat } from '../../../ui/ui'
import { formatAverage, formatShare, topRow, type ChartRow } from '../salesLabels'

type SalesPrintSummaryProps = {
  year: number
  issuedAt: string
  total: number
  monthRows: ChartRow[]
  weekdayRows: ChartRow[]
}

function TopStat({ label, rows, tone }: { label: string; rows: ChartRow[]; tone: string }) {
  const top = topRow(rows)
  return (
    <div className={`sales-kpi sales-kpi--${tone}`}>
      {top.value > 0 ? (
        <Stat label={label} value={top.label} hint={`${top.value} ventas (${formatShare(top.share)})`} />
      ) : (
        <Stat label={label} value="—" hint="Sin ventas" />
      )}
    </div>
  )
}

export function SalesPrintSummary({ year, issuedAt, total, monthRows, weekdayRows }: SalesPrintSummaryProps) {
  return (
    <Card className="print-only sales-summary" title={`Resumen del año ${year}`} subtitle={`Emitido el ${issuedAt}`}>
      <div className="sales-kpis">
        <div className="sales-kpi sales-kpi--accent">
          <Stat label="Total de ventas" value={total} />
        </div>
        <div className="sales-kpi sales-kpi--info">
          <Stat label="Promedio mensual" value={formatAverage(total, monthRows.length)} />
        </div>
        <TopStat label="Mes con más ventas" rows={monthRows} tone="success" />
        <TopStat label="Día con más ventas" rows={weekdayRows} tone="warning" />
      </div>
      <p className="muted">
        Se cuentan las facturas activas con al menos un comprobante de pago activo, según su fecha de emisión.
      </p>
    </Card>
  )
}
