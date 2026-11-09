import { Alert, Card, EmptyState, Stat } from '../../ui/ui'
import { SalesCountChart } from './components/SalesCountChart'
import { SalesPrintSummary } from './components/SalesPrintSummary'
import { YearSelector } from './components/YearSelector'
import { MONTH_LABELS, WEEKDAY_LABELS, countTotal, formatIssueDate, getYearOptions, toChartRows } from './salesLabels'
import { useSalesCountReport } from './useSalesCountReport'

export function SalesCountReport() {
  const { state, updateYear } = useSalesCountReport()
  const { year, data, loading, error } = state
  const monthRows = data && toChartRows(data.por_mes, MONTH_LABELS)
  const weekdayRows = data && toChartRows(data.por_dia_semana, WEEKDAY_LABELS)

  return (
    <>
      <Card title="Período" className="no-print">
        <div className="form-grid">
          <YearSelector year={year} options={getYearOptions(new Date().getFullYear())} onChange={updateYear} />
          {data && (
            <div className="sales-total">
              <Stat label={`Total de ventas en ${data.anio}`} value={countTotal(data.por_mes)} />
            </div>
          )}
        </div>
      </Card>

      {loading && (
        <Card>
          <EmptyState title="Cargando reporte…" />
        </Card>
      )}
      {error && <Alert tone="danger">{error}</Alert>}
      {data && monthRows && weekdayRows && (
        <>
          <SalesPrintSummary
            year={data.anio}
            issuedAt={formatIssueDate(new Date())}
            total={countTotal(data.por_mes)}
            monthRows={monthRows}
            weekdayRows={weekdayRows}
          />
          <SalesCountChart
            title="Ventas por mes"
            subtitle="Cantidad de ventas cobradas en cada mes."
            rows={monthRows}
            tone="accent"
          />
          <SalesCountChart
            title="Ventas por día de la semana"
            subtitle="Cantidad de ventas cobradas en cada día."
            rows={weekdayRows}
            tone="info"
          />
        </>
      )}
    </>
  )
}
