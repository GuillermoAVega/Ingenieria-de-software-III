import { Alert, Card, EmptyState } from '../../ui/ui'
import { MonthYearFilter } from './components/MonthYearFilter'
import { SalesComparisonChart } from './components/SalesComparisonChart'
import { SalesComparisonTotals } from './components/SalesComparisonTotals'
import { formatMonthYear } from './format'
import { useSalesComparison } from './useSalesComparison'

export function SalesComparisonReport() {
  const { state, updateAnio, updateMes } = useSalesComparison()

  return (
    <>
      <MonthYearFilter
        anio={state.anio}
        mes={state.mes}
        onChangeAnio={updateAnio}
        onChangeMes={updateMes}
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo cargar la comparativa">
          {state.error}
        </Alert>
      )}

      <Card
        title="Ventas por día"
        subtitle={
          state.report
            ? `${formatMonthYear(state.report.mes, state.report.anio)} contra ${formatMonthYear(
                state.report.mes_anterior,
                state.report.anio_anterior,
              )}.`
            : 'Comparativa contra el mes anterior.'
        }
      >
        {state.loading ? (
          <p className="muted">Cargando reporte...</p>
        ) : state.report ? (
          <div className="stack">
            <SalesComparisonTotals report={state.report} />
            <SalesComparisonChart report={state.report} />
          </div>
        ) : (
          <EmptyState title="Sin datos para mostrar">
            No se pudo obtener la comparativa de ventas.
          </EmptyState>
        )}
      </Card>
    </>
  )
}
