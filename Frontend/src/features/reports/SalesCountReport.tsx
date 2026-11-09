import { Alert, Card, EmptyState, Stat } from '../../ui/ui'
import { SalesCountChart } from './components/SalesCountChart'
import { YearSelector } from './components/YearSelector'
import { MONTH_LABELS, WEEKDAY_LABELS, countTotal, getYearOptions, toChartRows } from './salesLabels'
import { useSalesCountReport } from './useSalesCountReport'

export function SalesCountReport() {
  const { state, updateYear } = useSalesCountReport()
  const { year, data, loading, error } = state

  return (
    <>
      <Card title="Período">
        <div className="form-grid">
          <YearSelector year={year} options={getYearOptions(new Date().getFullYear())} onChange={updateYear} />
          {data && <Stat label={`Total de ventas en ${data.anio}`} value={countTotal(data.por_mes)} />}
        </div>
      </Card>

      {loading && (
        <Card>
          <EmptyState title="Cargando reporte…" />
        </Card>
      )}
      {error && <Alert tone="danger">{error}</Alert>}
      {data && (
        <>
          <SalesCountChart
            title="Ventas por mes"
            subtitle="Cantidad de ventas cobradas en cada mes."
            rows={toChartRows(data.por_mes, MONTH_LABELS)}
          />
          <SalesCountChart
            title="Ventas por día de la semana"
            subtitle="Cantidad de ventas cobradas en cada día."
            rows={toChartRows(data.por_dia_semana, WEEKDAY_LABELS)}
          />
        </>
      )}
    </>
  )
}
