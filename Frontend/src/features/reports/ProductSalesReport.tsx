import { Alert, BarRow, Card, DataTable, DateInput, EmptyState, Field, Select, Stat } from '../../ui/ui'
import { formatDate } from '../../utils/format'
import { formatCurrency } from './format'
import { PRODUCT_SALES_LIMITS, useProductSalesReport } from './useProductSalesReport'

export function ProductSalesReport() {
  const { state, rows, totalUnits, totalAmount, maxUnits, updateDesde, updateHasta, updateLimite } =
    useProductSalesReport()

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
          <Field label="Mostrar">
            <Select
              value={state.limite}
              onChange={(event) => updateLimite(Number(event.target.value))}
            >
              {PRODUCT_SALES_LIMITS.map((limit) => (
                <option key={limit} value={limit}>
                  Top {limit}
                </option>
              ))}
            </Select>
          </Field>
        </div>
      </Card>

      {state.error && <Alert tone="danger" title="No se pudo cargar el reporte">{state.error}</Alert>}

      {state.data && (
        <Card
          title="Resumen del período"
          subtitle={`${formatDate(state.data.desde)} al ${formatDate(state.data.hasta)} · productos facturados`}
        >
          <div className="form-grid">
            <Stat label="Unidades vendidas" value={totalUnits} hint={`Top ${state.data.limite}`} />
            <Stat label="Importe vendido" value={formatCurrency(totalAmount)} hint={`Top ${state.data.limite}`} />
          </div>
        </Card>
      )}

      <Card title="Productos más vendidos" subtitle="Unidades facturadas en el período seleccionado.">
        {state.loading ? (
          <EmptyState title="Cargando reporte…" />
        ) : state.error ? null : rows.length ? (
          <div className="stack">
            {rows.map((row) => (
              <BarRow
                key={row.producto_id}
                label={row.nombre}
                value={row.unidades}
                max={maxUnits}
                display={`${row.unidades} u.`}
              />
            ))}
          </div>
        ) : (
          <EmptyState title="Sin ventas en este período">
            Probá seleccionar otro rango de fechas.
          </EmptyState>
        )}
      </Card>

      {!state.loading && !state.error && rows.length > 0 && (
        <Card title="Detalle">
          <DataTable
            rowKey="producto_id"
            rows={rows}
            columns={[
              { key: 'nombre', header: 'Producto' },
              { key: 'tipo', header: 'Tipo' },
              { key: 'unidades', header: 'Unidades', num: true },
              {
                key: 'importe',
                header: 'Importe',
                num: true,
                render: (row) => formatCurrency(row.importe),
              },
            ]}
          />
        </Card>
      )}
    </>
  )
}
