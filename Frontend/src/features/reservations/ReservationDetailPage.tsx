import { useEffect, useState } from 'react'
import {
  Alert,
  Badge,
  Breadcrumb,
  Button,
  Card,
  KeyValue,
  PageHeader,
} from '../../ui/ui'
import { navigate } from '../../app/navigation'
import {
  getReservation,
  listCustomers,
  listReservationDetails,
  listReservationTables,
} from './api'
import type {
  CustomerRecord,
  ReservationDetail,
  ReservationRecord,
  ReservationStatus,
  TableRecord,
} from './types'

const statusLabel: Record<ReservationStatus, string> = {
  pendiente: 'Pendiente',
  con_comanda: 'Con comanda',
  cancelada: 'Cancelada',
  ausente: 'Ausente',
}

const statusTone = {
  pendiente: 'neutral',
  con_comanda: 'info',
  cancelada: 'danger',
  ausente: 'warning',
} as const

const fakeProductNames: Record<number, string> = {
  1: 'Empanadas surtidas',
  2: 'Pizza muzzarella',
  3: 'Ensalada de estación',
  4: 'Flan casero',
}

type ReservationDetails = {
  reservation: ReservationRecord
  customer: CustomerRecord | undefined
  tables: TableRecord[]
  details: ReservationDetail[]
}

export function ReservationDetailPage({ id }: { id: string }) {
  const [data, setData] = useState<ReservationDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadReservation() {
      try {
        const reservationId = Number(id)
        if (!Number.isInteger(reservationId) || reservationId < 1) {
          throw new Error('El identificador de la reserva no es válido.')
        }

        const [reservation, customers, tables, details] = await Promise.all([
          getReservation(reservationId),
          listCustomers(),
          listReservationTables(reservationId),
          listReservationDetails(reservationId),
        ])
        if (cancelled) return

        setData({
          reservation,
          customer: customers.find((customer) => customer.id === reservation.cliente_id),
          tables,
          details,
        })
      } catch (cause) {
        if (!cancelled) {
          setError(cause instanceof Error ? cause.message : 'No se pudo cargar la reserva.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    void loadReservation()
    return () => {
      cancelled = true
    }
  }, [id])

  const reservation = data?.reservation
  const customerName = data?.customer
    ? `${data.customer.nombre} ${data.customer.apellido}`
    : reservation
      ? `Cliente #${reservation.cliente_id}`
      : 'Reserva'

  return (
    <>
      <PageHeader
        breadcrumb={<Breadcrumb items={[{ label: 'Reservas', href: '#/reservas' }, { label: `Reserva #${id}` }]} />}
        title={
          reservation ? (
            <>
              Reserva #{reservation.id}{' '}
              <Badge tone={statusTone[reservation.estado]}>{statusLabel[reservation.estado]}</Badge>
            </>
          ) : `Reserva #${id}`
        }
        subtitle="Detalle de la reserva."
        actions={
          <>
            <Button onClick={() => navigate('/reservas')}>Volver</Button>
            {reservation?.estado === 'pendiente' && (
              <Button variant="primary" onClick={() => navigate(`/reservas/${id}/editar`)}>
                Editar
              </Button>
            )}
          </>
        }
      />

      {error && <Alert tone="danger">{error}</Alert>}
      {loading ? (
        <p className="muted">Cargando reserva...</p>
      ) : data ? (
        <div className="stack">
          <Card title="Datos de la reserva">
            <KeyValue label="Cliente" value={customerName} />
            <KeyValue label="Teléfono" value={data.customer?.telefono ?? '—'} />
            <KeyValue label="Fecha" value={reservation?.fecha ?? '—'} />
            <KeyValue label="Hora" value={reservation?.hora.slice(0, 5) ?? '—'} />
            <KeyValue label="Comensales" value={reservation?.cant_comensales ?? '—'} />
            <KeyValue label="Estado" value={reservation ? statusLabel[reservation.estado] : '—'} />
            <KeyValue label="Observaciones" value={reservation?.observaciones || '—'} />
          </Card>

          <Card title="Mesas asignadas">
            {data.tables.length ? (
              <div className="stack">
                {data.tables.map((table) => (
                  <div className="row" key={table.id}>
                    <span>Mesa {table.id}</span>
                    <span className="muted">{table.capacidad} personas</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No hay mesas asignadas.</p>
            )}
          </Card>

          <Card title="Detalle de comanda" subtitle="Productos ficticios por ahora.">
            {data.details.length ? (
              <div className="stack">
                {data.details.map((detail) => (
                  <div className="row" key={detail.producto_id}>
                    <span>{fakeProductNames[detail.producto_id] ?? `Producto #${detail.producto_id}`}</span>
                    <span className="muted">Cantidad: {detail.cantidad_producto}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No hay productos agregados al detalle.</p>
            )}
          </Card>
        </div>
      ) : null}
    </>
  )
}
