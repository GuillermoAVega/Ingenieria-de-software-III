import { BarRow, Card } from '../../../ui/ui'
import { formatCountWithShare, type ChartRow } from '../salesLabels'

export function SalesCountChart({ title, subtitle, rows }: { title: string; subtitle: string; rows: ChartRow[] }) {
  const max = Math.max(...rows.map((row) => row.value))
  return (
    <Card title={title} subtitle={subtitle}>
      <div className="stack">
        {rows.map((row) => (
          <BarRow key={row.label} label={row.label} value={row.value} max={max} display={formatCountWithShare(row)} />
        ))}
      </div>
    </Card>
  )
}
