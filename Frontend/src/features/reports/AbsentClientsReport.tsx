import { Alert, Card, DataTable, EmptyState } from '../../ui/ui'
import { formatDate } from '../../utils/format'
import { useAbsentClientsReport } from './useAbsentClientsReport'

export function AbsentClientsReport() {
  const { state } = useAbsentClientsReport()
  const rows = state.data?.clientes ?? []

  return (
    <Card title="Clientes que inasistieron a reservas">
      {state.loading ? (
        <EmptyState title="Cargando reporte…" />
      ) : state.error ? (
        <Alert tone="danger" title="No se pudo cargar el reporte">
          {state.error}
        </Alert>
      ) : rows.length ? (
        <DataTable
          rowKey="dni"
          rows={rows}
          columns={[
            {
              key: 'nombre',
              header: 'Cliente',
              render: (row) => <span className="cell-main">{`${row.nombre} ${row.apellido}`}</span>,
            },
            { key: 'dni', header: 'DNI' },
            {
              key: 'ultima_fecha',
              header: 'Última reserva ausente',
              render: (row) => `${formatDate(row.ultima_fecha)} ${row.ultima_hora.slice(0, 5)}`,
            },
            { key: 'cantidad_ausencias', header: 'Inasistencias', num: true },
          ]}
        />
      ) : (
        <EmptyState title="Sin clientes ausentes">
          No hay reservas marcadas como ausentes.
        </EmptyState>
      )}
    </Card>
  )
}
