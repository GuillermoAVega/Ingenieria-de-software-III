import { useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Badge,
  Button,
  Card,
  DataTable,
  DeleteButton,
  Input,
  PageHeader,
  Pagination,
  Select,
  Toolbar,
  ToolbarSpacer,
} from '../../ui/ui'
import type { BadgeTone, DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { cancelReservation, listCustomers, listReservations, listTables } from './api'
import type { Reservation, ReservationStatus, CustomerRecord, ReservationRecord, TableRecord } from './types'

const pageSize = 10

const statusLabel: Record<ReservationStatus, string> = {
  pendiente: 'Pendiente',
  con_comanda: 'Con comanda',
  cancelada: 'Cancelada',
  ausente: 'Ausente',
}

const statusTone: Record<ReservationStatus, BadgeTone> = {
  pendiente: 'neutral',
  con_comanda: 'info',
  cancelada: 'danger',
  ausente: 'warning',
}

function toReservation(
  reservation: ReservationRecord,
  customers: Map<number, CustomerRecord>,
  tables: Map<number, TableRecord>,
): Reservation {
  const customer = customers.get(reservation.cliente_id)
  return {
    id: String(reservation.id),
    time: reservation.hora.slice(0, 5),
    date: reservation.fecha,
    customer: customer ? `${customer.nombre} ${customer.apellido}` : `Cliente #${reservation.cliente_id}`,
    phone: customer?.telefono ?? '—',
    guests: reservation.cant_comensales,
    table: reservation.mesa_ids
      .map((id) => (tables.has(id) ? `Mesa ${id}` : `Mesa #${id}`))
      .join(', ') || 'Sin mesa asignada',
    status: reservation.estado,
  }
}

const columns: DataTableColumn<Reservation>[] = [
  { key: 'date', header: 'Fecha' },
  { key: 'time', header: 'Hora' },
  {
    key: 'customer',
    header: 'Cliente',
    render: (reservation) => (
      <>
        <div className="cell-main">{reservation.customer}</div>
        <div className="cell-sub">{reservation.phone}</div>
      </>
    ),
  },
  { key: 'guests', header: 'Comensales', num: true },
  { key: 'table', header: 'Mesas' },
  {
    key: 'status',
    header: 'Estado',
    render: (reservation) => (
      <Badge tone={statusTone[reservation.status]}>{statusLabel[reservation.status]}</Badge>
    ),
  },
]

export function ReservationsListPage() {
  const [reservations, setReservations] = useState<Reservation[]>([])
  const [search, setSearch] = useState('')
  const [date, setDate] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    Promise.all([
        listReservations(),
        listCustomers(),
        listTables(),
      ])
      .then(([reservationRecords, customerRecords, tableRecords]) => {
        if (cancelled) return
        const customers = new Map(customerRecords.map((customer) => [customer.id, customer]))
        const tables = new Map(tableRecords.map((table) => [table.id, table]))
        setReservations(reservationRecords.map((reservation) => toReservation(reservation, customers, tables)))
        setError(null)
      })
      .catch((cause: unknown) => {
        if (!cancelled) setError(cause instanceof Error ? cause.message : 'No se pudieron cargar las reservas.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [refreshKey])

  const filteredReservations = useMemo(() => {
    const query = search.trim().toLocaleLowerCase()
    return reservations.filter((reservation) => {
      const matchesSearch = [reservation.customer, reservation.phone]
        .some((value) => value.toLocaleLowerCase().includes(query))
      return matchesSearch &&
        (!date || reservation.date === date) &&
        (!status || reservation.status === status)
    })
  }, [reservations, search, date, status])

  const visibleReservations = filteredReservations.slice((page - 1) * pageSize, page * pageSize)

  async function handleCancel(reservation: Reservation) {
    setError(null)
    try {
      await cancelReservation(Number(reservation.id))
      setLoading(true)
      setRefreshKey((current) => current + 1)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo cancelar la reserva.')
    }
  }

  return (
    <>
      <PageHeader
        title="Reservas"
        subtitle="Agenda del servicio, estado de cada reserva y mesas asignadas."
        actions={
          <Button variant="primary" onClick={() => navigate('/reservas/nueva')}>
            Nueva reserva
          </Button>
        }
      />

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar por cliente o teléfono..."
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setPage(1)
            }}
          />
          <Input
            type="date"
            aria-label="Filtrar por fecha"
            value={date}
            onChange={(event) => {
              setDate(event.target.value)
              setPage(1)
            }}
          />
          <Select
            aria-label="Filtrar por estado"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value)
              setPage(1)
            }}
          >
            <option value="">Todos los estados</option>
            <option value="pendiente">Pendientes</option>
            <option value="con_comanda">Con comanda</option>
            <option value="cancelada">Canceladas</option>
            <option value="ausente">Ausentes</option>
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">{loading ? 'Cargando...' : `${reservations.length} reservas`}</span>
        </Toolbar>

        {error && <Alert tone="danger">{error}</Alert>}

        <DataTable
          columns={columns}
          rows={visibleReservations}
          empty={<div className="empty"><span className="empty-title">{loading ? 'Cargando reservas...' : 'No hay reservas para mostrar'}</span></div>}
          actions={(reservation) => (
            <div className="row">
              <Button size="sm" onClick={() => navigate(`/reservas/${reservation.id}`)}>
                Ver
              </Button>
              {reservation.status === 'pendiente' && (
                <Button size="sm" aria-label={`Crear comanda para ${reservation.customer}`}>
                  Crear comanda
                </Button>
              )}
              {reservation.status === 'pendiente' && (
                <Button size="sm" onClick={() => navigate(`/reservas/${reservation.id}/editar`)}>
                  Editar
                </Button>
              )}
              {reservation.status === 'pendiente' && (
                <DeleteButton
                  label="Cancelar"
                  title="Cancelar reserva"
                  confirmLabel="Cancelar reserva"
                  onConfirm={() => void handleCancel(reservation)}
                >
                  ¿Querés cancelar la reserva de <strong>{reservation.customer}</strong>?
                </DeleteButton>
              )}
            </div>
          )}
        />

        <Pagination
          page={page}
          pageSize={pageSize}
          total={filteredReservations.length}
          onPageChange={setPage}
        />
      </Card>
    </>
  )
}
