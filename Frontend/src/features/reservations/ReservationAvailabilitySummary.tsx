import type { TableRecord } from './types'

type ReservationAvailabilitySummaryProps = {
  date: string
  time: string
  available: TableRecord[]
  warning: TableRecord[]
  unavailable: TableRecord[]
}

function TableTags({ tables }: { tables: TableRecord[] }) {
  return (
    <div className="reservation-table-tags">
      {tables.length ? tables.map((table) => (
        <span className="reservation-table-tag" key={table.id}>
          Mesa {table.id} · {table.capacidad} personas
        </span>
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
}: ReservationAvailabilitySummaryProps) {
  return (
    <div className="reservation-availability-summary">
      <div className="reservation-availability-heading">
        <strong>Disponibilidad de mesas</strong>
        <span>{date || 'Fecha seleccionada'} {time ? `· ${time}` : ''}</span>
      </div>
      <div className="reservation-availability-row">
        <span className="reservation-availability-label reservation-availability-success">Libres</span>
        <TableTags tables={available} />
      </div>
      {warning.length > 0 && (
        <div className="reservation-availability-row">
          <span className="reservation-availability-label reservation-availability-warning">Advertencia</span>
          <TableTags tables={warning} />
        </div>
      )}
      {unavailable.length > 0 && (
        <div className="reservation-availability-row">
          <span className="reservation-availability-label reservation-availability-danger">No disponibles</span>
          <TableTags tables={unavailable} />
        </div>
      )}
    </div>
  )
}
