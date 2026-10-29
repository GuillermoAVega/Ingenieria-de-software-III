/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Listado de comandas
 * COMPLETAR:
 * 1. Reemplazar DEMO_ORDERS por la llamada a la API.
 * 2. Implementar búsqueda, filtro por estado y paginación.
 * 3. Conectar las acciones de fila con el detalle real de la comanda.
 */
import { Badge, Button, Card, DataTable, Input, PageHeader, Pagination, Select, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_ORDERS } from './demo'
import type { Order } from './types'

const formatCurrency = (value: number) => `$ ${value.toLocaleString('es-AR')}`

const columns: DataTableColumn<Order>[] = [
  {
    key: 'id',
    header: 'Comanda',
    render: (order) => <span className="cell-main">#{order.id}</span>,
  },
  {
    key: 'table',
    header: 'Mesa / mozo',
    render: (order) => (
      <>
        <div className="cell-main">{order.table}</div>
        <div className="cell-sub">{order.waiter}</div>
      </>
    ),
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

export function OrdersListPage() {
  return (
    <>
      <PageHeader
        title="Comandas"
        subtitle="Seguimiento de las comandas abiertas y cerradas del servicio."
        actions={
          <Button variant="primary" onClick={() => navigate('/comandas/nueva')}>
            Nueva comanda
          </Button>
        }
      />

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar por mesa, mozo o número..."
            onChange={() => {
              // TODO(equipo-operacion): filtrar comandas por texto.
            }}
          />
          <Select
            defaultValue=""
            onChange={() => {
              // TODO(equipo-operacion): filtrar comandas por estado.
            }}
          >
            <option value="">Todos los estados</option>
            <option value="abierta">Abiertas</option>
            <option value="cerrada">Cerradas</option>
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">Datos de demostración</span>
        </Toolbar>

        <DataTable
          columns={columns}
          rows={DEMO_ORDERS}
          actions={(order) => (
            <Button size="sm" onClick={() => navigate(`/comandas/${order.id}`)}>
              Ver
            </Button>
          )}
        />

        <Pagination
          page={1}
          pageSize={10}
          total={DEMO_ORDERS.length}
          onPageChange={() => {
            // TODO(equipo-operacion): implementar la paginación contra la API.
          }}
        />
      </Card>
    </>
  )
}
