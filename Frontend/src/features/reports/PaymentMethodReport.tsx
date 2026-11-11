import { Alert, BarRow, Card, DataTable, DateInput, EmptyState, Field, Stat } from '../../ui/ui'
import { formatDate } from '../../utils/format'
import { formatCurrency, formatPercentage } from './format'
import { usePaymentMethodReport } from './usePaymentMethodReport'

export function PaymentMethodReport() {
  const { state, rows, rowsByImporte, rowsByPromedio, updateDesde, updateHasta } =
    usePaymentMethodReport()

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

      {state.loading ? (
        <Card>
          <EmptyState title="Cargando reporte…" />
        </Card>
      ) : state.error ? null : state.data && rows.length === 0 ? (
        <Card>
          <EmptyState title="Sin comprobantes de pago en este período">
            Probá seleccionar otro rango de fechas.
          </EmptyState>
        </Card>
      ) : state.data ? (
        <>
          <Card
            title="Resumen del período"
            subtitle={`${formatDate(state.data.desde)} al ${formatDate(state.data.hasta)}`}
          >
            <div className="form-grid">
              <Stat label="Comprobantes de pago" value={state.data.total_comprobantes} />
              <Stat label="Importe total" value={formatCurrency(state.data.total_importe)} />
              <Stat
                label="Importe promedio"
                value={formatCurrency(state.data.importe_promedio)}
                hint="Por comprobante"
              />
            </div>
          </Card>

          <Card
            title="Top por cantidad de comprobantes"
            subtitle="Participación de cada medio sobre el total de comprobantes."
          >
            <div className="stack">
              {rows.map((row) => (
                <BarRow
                  key={row.medio_pago_id}
                  label={row.descripcion}
                  value={row.porcentaje_uso}
                  max={100}
                  display={`${row.cantidad_comprobantes} (${formatPercentage(row.porcentaje_uso)})`}
                />
              ))}
            </div>
          </Card>

          <Card
            title="Top por importe cobrado"
            subtitle="Participación de cada medio sobre el total cobrado."
          >
            <div className="stack">
              {rowsByImporte.map((row) => (
                <BarRow
                  key={row.medio_pago_id}
                  label={row.descripcion}
                  value={row.porcentaje_importe}
                  max={100}
                  display={`${formatCurrency(row.importe)} (${formatPercentage(row.porcentaje_importe)})`}
                />
              ))}
            </div>
          </Card>

          <Card
            title="Top por promedio por comprobante"
            subtitle="Promedio cobrado por comprobante en cada medio, de mayor a menor."
          >
            <DataTable
              rowKey="medio_pago_id"
              rows={rowsByPromedio}
              columns={[
                { key: 'descripcion', header: 'Medio de pago' },
                { key: 'cantidad_comprobantes', header: 'Comprobantes', num: true },
                {
                  key: 'importe',
                  header: 'Importe total',
                  num: true,
                  render: (row) => formatCurrency(row.importe),
                },
                {
                  key: 'importe_promedio',
                  header: 'Promedio',
                  num: true,
                  render: (row) => formatCurrency(row.importe_promedio),
                },
              ]}
            />
          </Card>
        </>
      ) : null}
    </>
  )
}
