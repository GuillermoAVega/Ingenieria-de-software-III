import { Alert, Card, DataTable, DateInput, EmptyState, Field, Stat } from '../../ui/ui'
import { formatDate } from '../../utils/format'
import { formatCurrency } from './format'
import { useWaiterOrderReport } from './useWaiterOrderReport'

export function WaiterOrderReport() {
  const { state, updateDesde, updateHasta } = useWaiterOrderReport()
  const totalOrders = state.data?.por_mozo.reduce((total, row) => total + row.cantidad_comandas, 0) ?? 0
  const totalSales = state.data?.por_mozo.reduce((total, row) => total + row.importe_ventas, 0) ?? 0

  return (
    <>
      <Card title="Período" className="no-print">
        <div className="form-grid">
          <Field label="Desde">
            <DateInput
              value={state.desde}
              max={state.hasta || undefined}
              required
              onChange={updateDesde}
            />
          </Field>
          <Field label="Hasta">
            <DateInput
              value={state.hasta}
              min={state.desde || undefined}
              required
              onChange={updateHasta}
            />
          </Field>
        </div>
      </Card>

      {state.error && <Alert tone="danger" title="No se pudo cargar el reporte">{state.error}</Alert>}

      {state.data && (
        <Card
          title="Resumen del período"
          subtitle={`${formatDate(state.data.desde)} al ${formatDate(state.data.hasta)}`}
        >
          <div className="form-grid">
            <Stat label="Comandas" value={totalOrders} />
            <Stat label="Ventas facturadas" value={formatCurrency(totalSales)} />
          </div>
        </Card>
      )}

      <Card title="Comandas y ventas por mozo">
        {state.loading ? (
          <EmptyState title="Cargando reporte…" />
        ) : state.error ? null : state.data?.por_mozo.length ? (
          <DataTable
            rowKey="mozo_id"
            rows={state.data.por_mozo}
            columns={[
              { key: 'nombre', header: 'Mozo' },
              { key: 'cantidad_comandas', header: 'Comandas', num: true },
              {
                key: 'importe_ventas',
                header: 'Ventas facturadas',
                num: true,
                render: (row) => formatCurrency(row.importe_ventas),
              },
            ]}
          />
        ) : (
          <EmptyState title="Sin comandas en este período">
            Probá seleccionar otro rango de fechas.
          </EmptyState>
        )}
      </Card>
    </>
  )
}
