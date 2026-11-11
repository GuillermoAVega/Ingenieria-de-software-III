/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Listado de comandas
 * La lógica vive en `useOrdersList`; la pantalla solo renderiza.
 */
import {
  Alert,
  Badge,
  Button,
  Card,
  DataTable,
  DeleteButton,
  EmptyState,
  Input,
  PageHeader,
  Pagination,
  Select,
  Toolbar,
  ToolbarSpacer,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { EyeIcon } from '../../ui/EyeIcon'
import { TrashIcon } from '../../ui/TrashIcon'
import { formatDate, formatTime } from '../../utils/format'
import { ORDER_STATUS_LABEL, ORDER_STATUS_TONE } from './status'
import { useOrdersList } from './useOrdersList'
import type { OrderListItem } from './types'

const columns: DataTableColumn<OrderListItem>[] = [
  {
    key: 'id',
    header: 'Comanda',
    render: (order) => <span className="cell-main">#{order.id}</span>,
  },
  {
    key: 'mesa',
    header: 'Mesa',
    render: (order) => `Mesa ${order.mesa_id}`,
  },
  {
    key: 'mozo',
    header: 'Mozo',
    render: (order) =>
      order.waiterName ?? (order.mozo_id === null ? 'Sin mozo' : `Mozo #${order.mozo_id}`),
  },
  {
    key: 'fecha',
    header: 'Fecha',
    render: (order) => formatDate(order.fecha),
  },
  {
    key: 'hora',
    header: 'Hora',
    render: (order) => formatTime(order.hora),
  },
  {
    key: 'items',
    header: 'Ítems',
    num: true,
    render: (order) => order.detalles.length,
  },
  {
    key: 'estado',
    header: 'Estado',
    render: (order) => (
      <Badge tone={ORDER_STATUS_TONE[order.estado]}>{ORDER_STATUS_LABEL[order.estado]}</Badge>
    ),
  },
]

export function OrdersListPage() {
  const { state, orders, total, page, pageSize, updateSearch, updateStatus, changePage, remove } =
    useOrdersList()

  return (
    <>
      <PageHeader
        title="Comandas"
        subtitle="Pedidos de cada mesa, abiertos y cerrados."
        actions={
          <Button variant="primary" onClick={() => navigate('/comandas/nueva')}>
            Nueva comanda
          </Button>
        }
      />

      {state.error && (
        <Alert tone="danger" title="No se pudieron cargar las comandas">
          {state.error}
        </Alert>
      )}

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar por número, mesa o mozo..."
            value={state.search}
            onChange={(event) => updateSearch(event.target.value)}
          />
          <Select value={state.statusFilter} onChange={(event) => updateStatus(event.target.value)}>
            <option value="">Todos los estados</option>
            <option value="abierta">Abiertas</option>
            <option value="cerrada">Cerradas</option>
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">{total} comandas</span>
        </Toolbar>

        {state.loading ? (
          <p className="muted">Cargando comandas...</p>
        ) : (
          <DataTable
            columns={columns}
            rows={orders}
            empty={
              <EmptyState title="Sin comandas para mostrar">
                No hay comandas que coincidan con los filtros elegidos.
              </EmptyState>
            }
            actions={(order) => (
              <div className="row row-icons">
                <Button
                  size="sm"
                  className="btn-icon"
                  title="Ver comanda"
                  aria-label={`Ver comanda #${order.id}`}
                  onClick={() => navigate(`/comandas/${order.id}`)}
                >
                  <EyeIcon />
                </Button>
                <DeleteButton
                  label="Eliminar comanda"
                  icon={<TrashIcon />}
                  title="Eliminar comanda"
                  onConfirm={() => {
                    void remove(order.id)
                  }}
                >
                  ¿Querés eliminar la comanda <strong>#{order.id}</strong>?
                </DeleteButton>
              </div>
            )}
          />
        )}

        <Pagination
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={changePage}
          label={`Página ${page} · ${total} comandas`}
        />
      </Card>
    </>
  )
}
