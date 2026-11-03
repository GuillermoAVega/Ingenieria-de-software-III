import type { TableRecord } from './types'

type ReservationAvailabilitySummaryProps = {
  date: string
  time: string
  available: TableRecord[]
  warning: TableRecord[]
  unavailable: TableRecord[]
  onSelectTable: (tableId: number) => void
}

function TableTags({ tables, onSelectTable, disabled = false }: { tables: TableRecord[]; onSelectTable: (tableId: number) => void; disabled?: boolean }) {
  return (
    <div className="reservation-table-tags">
      {tables.length ? tables.map((table) => (
        <button className="reservation-table-tag" key={table.id} type="button" onClick={() => onSelectTable(table.id)} disabled={disabled}>
          Mesa {table.id} · {table.capacidad} personas
        </button>
      )) : <span className="reservation-availability-empty">No hay mesas libres</span>}
    </div>
  )
}

export function ReservationAvailabilitySummary({
  date,
  time,
  available,
  warning,
  unavailable,
  onSelectTable,
}: ReservationAvailabilitySummaryProps) {
  return (
    <div className="reservation-availability-summary">
      <div className="reservation-availability-heading">
        <strong>Disponibilidad de mesas</strong>
        <span>{date || 'Fecha seleccionada'} {time ? `· ${time}` : ''}</span>
      </div>
      <div className="reservation-availability-row">
        <span className="reservation-availability-label reservation-availability-success">Libres</span>
        <TableTags tables={available} onSelectTable={onSelectTable} />
      </div>
      {warning.length > 0 && (
        <div className="reservation-availability-row">
          <span className="reservation-availability-label reservation-availability-warning">Advertencia</span>
          <TableTags tables={warning} onSelectTable={onSelectTable} />
        </div>
      )}
      {unavailable.length > 0 && (
        <div className="reservation-availability-row">
          <span className="reservation-availability-label reservation-availability-danger">No disponibles</span>
          <TableTags tables={unavailable} onSelectTable={onSelectTable} disabled />
        </div>
      )}
    </div>
  )
}
