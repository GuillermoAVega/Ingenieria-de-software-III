/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Listado de reservas
 * COMPLETAR:
 * 1. Reemplazar DEMO_RESERVATIONS por la llamada a la API.
 * 2. Implementar búsqueda, filtro por fecha y estado, y paginación.
 * 3. Conectar Crear comanda, Editar y Cancelar con la API.
 */
import { Badge, Button, Card, DataTable, Input, PageHeader, Pagination, Select, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { BadgeTone, DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_RESERVATIONS } from './demo'
import type { Reservation, ReservationStatus } from './types'

const statusLabel: Record<ReservationStatus, string> = {
  confirmada: 'Confirmada',
  'con-comanda': 'Con comanda',
  cancelada: 'Cancelada',
  ausente: 'Ausente',
  pendiente: 'Pendiente',
}

const statusTone: Record<ReservationStatus, BadgeTone> = {
  confirmada: 'success',
  'con-comanda': 'info',
  cancelada: 'danger',
  ausente: 'warning',
  pendiente: 'neutral',
}

const columns: DataTableColumn<Reservation>[] = [
  {
    key: 'time',
    header: 'Hora',
  },
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
  {
    key: 'guests',
    header: 'Comensales',
    num: true,
  },
  {
    key: 'table',
    header: 'Mesa',
  },
  {
    key: 'status',
    header: 'Estado',
    render: (reservation) => (
      <Badge tone={statusTone[reservation.status]}>{statusLabel[reservation.status]}</Badge>
    ),
  },
]

export function ReservationsListPage() {
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
            onChange={() => {
              // TODO(equipo-operacion): filtrar reservas por texto.
            }}
          />
          <Input
            type="date"
            defaultValue="2026-10-16"
            onChange={() => {
              // TODO(equipo-operacion): filtrar reservas por fecha.
            }}
          />
          <Select
            defaultValue=""
            onChange={() => {
              // TODO(equipo-operacion): filtrar reservas por estado.
            }}
          >
            <option value="">Todos los estados</option>
            <option value="confirmada">Confirmadas</option>
            <option value="con-comanda">Con comanda</option>
            <option value="cancelada">Canceladas</option>
            <option value="ausente">Ausentes</option>
            <option value="pendiente">Pendientes</option>
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">Datos de demostración</span>
        </Toolbar>

        <DataTable
          columns={columns}
          rows={DEMO_RESERVATIONS}
          actions={(reservation) => (
            <div className="row">
              <Button size="sm" onClick={() => navigate('/comandas/nueva')}>
                Crear comanda
              </Button>
              <Button size="sm" onClick={() => navigate(`/reservas/${reservation.id}/editar`)}>
                Editar
              </Button>
              <Button
                size="sm"
                variant="danger-ghost"
                onClick={() => {
                  // TODO(equipo-operacion): cancelar la reserva en la API.
                }}
              >
                Cancelar
              </Button>
            </div>
          )}
        />

        <Pagination
          page={1}
          pageSize={10}
          total={DEMO_RESERVATIONS.length}
          onPageChange={() => {
            // TODO(equipo-operacion): implementar la paginación contra la API.
          }}
        />
      </Card>
    </>
  )
}
