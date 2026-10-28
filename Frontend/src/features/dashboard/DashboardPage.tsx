/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Panel de inicio
 * COMPLETAR:
 * 1. Reemplazar DEMO_ORDERS, DEMO_RESERVATIONS y las métricas por la API.
 * 2. Implementar el rango de fechas y el refresco de indicadores.
 * 3. Conectar los accesos rápidos con los flujos reales.
 */
import { Badge, Button, Card, DataTable, PageHeader, Stat } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_ORDERS } from '../orders/demo'
import type { Order } from '../orders/types'
import { DEMO_RESERVATIONS } from '../reservations/demo'

const formatCurrency = (value: number) => `$ ${value.toLocaleString('es-AR')}`

const upcomingReservations = DEMO_RESERVATIONS.filter((reservation) => reservation.status === 'confirmada')

const orderColumns: DataTableColumn<Order>[] = [
  {
    key: 'id',
    header: 'Comanda',
    render: (order) => <span className="cell-main">#{order.id}</span>,
  },
  {
    key: 'table',
    header: 'Mesa',
    render: (order) => (
      <>
        <div className="cell-main">{order.table}</div>
        <div className="cell-sub">{order.sector}</div>
      </>
    ),
  },
  {
    key: 'waiter',
    header: 'Mozo',
  },
  {
    key: 'openedAt',
    header: 'Hora',
  },
  {
    key: 'total',
    header: 'Total',
    num: true,
    render: (order) => formatCurrency(order.total),
  },
  {
    key: 'status',
    header: 'Estado',
    render: (order) => (
      <Badge tone={order.status === 'abierta' ? 'warning' : 'success'}>
        {order.status === 'abierta' ? 'Abierta' : 'Cerrada'}
      </Badge>
    ),
  },
]

export function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Inicio"
        subtitle="Viernes 16 de octubre · estado del salón en este momento"
        actions={
          <>
            <Button onClick={() => navigate('/reservas/nueva')}>Nueva reserva</Button>
            <Button variant="primary" onClick={() => navigate('/comandas/nueva')}>
              Nueva comanda
            </Button>
          </>
        }
      />

      <div className="grid-auto">
        <Card flush>
          <Stat label="Comandas abiertas" value={7} hint="3 con productos pendientes" />
        </Card>
        <Card flush>
          <Stat label="Mesas ocupadas" value="9 de 18" hint="2 reservadas" />
        </Card>
        <Card flush>
          <Stat label="Reservas de hoy" value={12} hint="4 aún por llegar" />
        </Card>
        <Card flush>
          <Stat label="Facturado hoy" value={formatCurrency(482300)} hint="21 comprobantes" />
        </Card>
      </div>

      <div className="layout-aside">
        <div className="primary">
          <Card
            title="Comandas abiertas"
            subtitle="Ordenadas por hora de apertura."
            flush
            actions={
              <Button size="sm" onClick={() => navigate('/comandas')}>
                Ver todas
              </Button>
            }
          >
            <DataTable
              columns={orderColumns}
              rows={DEMO_ORDERS}
              actions={(order) => (
                <Button size="sm" onClick={() => navigate(`/comandas/${order.id}`)}>
                  Ver
                </Button>
              )}
            />
          </Card>
        </div>

        <aside className="aside">
          <Card
            title="Próximas reservas"
            subtitle="Hoy"
            actions={
              <Button size="sm" onClick={() => navigate('/reservas')}>
                Ver todas
              </Button>
            }
          >
            <div className="stack">
              {upcomingReservations.map((reservation) => (
                <div className="row" key={reservation.id}>
                  <span className="cell-main">{reservation.time}</span>
                  <div className="grow">
                    <div className="cell-main">{reservation.customer}</div>
                    <div className="cell-sub">
                      {reservation.guests} comensales · {reservation.table}
                    </div>
                  </div>
                  <Badge tone="success">Confirmada</Badge>
                </div>
              ))}
            </div>
          </Card>
        </aside>
      </div>
    </>
  )
}
