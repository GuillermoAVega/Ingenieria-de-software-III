import { Alert, BarRow, Card, DataTable, DateInput, EmptyState, Field, Stat } from '../../ui/ui'
import { formatDate } from '../../utils/format'
import { useOccupancyBySectorReport } from './useOccupancyBySectorReport'

export function OccupancyBySectorReport() {
  const { state, updateDesde, updateHasta } = useOccupancyBySectorReport()
  const rows = state.data?.por_sector ?? []
  const totalCommands = rows.reduce((total, row) => total + row.cantidad_comandas, 0)
  const totalTables = rows.reduce((total, row) => total + row.mesas_atendidas, 0)
  const maxCommands = rows.reduce((max, row) => Math.max(max, row.cantidad_comandas), 0)
  const mostRotatedSector = rows.reduce(
    (top, row) => (row.rotacion > (top?.rotacion ?? 0) ? row : top),
    rows[0],
  )

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
        <Card title="Resumen del período" subtitle={`${formatDate(state.data.desde)} al ${formatDate(state.data.hasta)}`}>
          <div className="form-grid">
            <Stat label="Usos de mesas" value={totalCommands} hint="Incluye cada atención" />
            <Stat label="Mesas diferentes" value={totalTables} hint="Cantidad de mesas distintas utilizadas" />
            <Stat
              label="Mayor uso promedio"
              value={mostRotatedSector ? `${mostRotatedSector.rotacion.toLocaleString('es-AR')} veces` : '—'}
              hint={mostRotatedSector?.sector ?? 'Sin actividad'}
            />
          </div>
        </Card>
      )}

      <Card title="Actividad por sector" subtitle="Comparación de atenciones registradas en el período.">
        {state.loading ? (
          <EmptyState title="Cargando reporte…" />
        ) : state.error ? null : rows.length ? (
          <div className="stack">
            {rows.map((row) => (
              <BarRow
                key={row.sector_id}
                label={row.sector}
                value={row.cantidad_comandas}
                max={maxCommands}
                display={`${row.cantidad_comandas} atenciones`}
              />
            ))}
          </div>
        ) : (
          <EmptyState title="Sin actividad en este período">
            Probá seleccionar otro rango de fechas.
          </EmptyState>
        )}
      </Card>

      <Card title="Detalle por sector" subtitle="Compará cuántas veces se usaron las mesas de cada sector.">
        {state.loading ? (
          <EmptyState title="Cargando reporte…" />
        ) : state.error ? null : rows.length ? (
          <DataTable
            rowKey="sector_id"
            rows={rows}
            columns={[
              { key: 'sector', header: 'Sector' },
              { key: 'mesas_atendidas', header: 'Mesas utilizadas', num: true },
              { key: 'cantidad_comandas', header: 'Atenciones', num: true },
              {
                key: 'rotacion',
                header: 'Promedio de veces que se usó cada mesa',
                num: true,
                render: (row) => `${row.rotacion.toLocaleString('es-AR', { maximumFractionDigits: 2 })} veces por mesa`,
              },
            ]}
          />
        ) : (
          <EmptyState title="Sin actividad en este período">
            Probá seleccionar otro rango de fechas.
          </EmptyState>
        )}
      </Card>
    </>
  )
}
