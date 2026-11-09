import { BarRow, Card } from '../../../ui/ui'
import { formatCountWithShare, type ChartRow } from '../salesLabels'

type SalesCountChartProps = {
  title: string
  subtitle: string
  rows: ChartRow[]
  tone: 'accent' | 'info'
}

export function SalesCountChart({ title, subtitle, rows, tone }: SalesCountChartProps) {
  const max = Math.max(...rows.map((row) => row.value))
  return (
    <Card title={title} subtitle={subtitle} className={`sales-chart sales-chart--${tone}`}>
      <div className="stack">
        {rows.map((row) => (
          <BarRow key={row.label} label={row.label} value={row.value} max={max} display={formatCountWithShare(row)} />
        ))}
      </div>
    </Card>
  )
}
