/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Detalle de una comanda
 * COMPLETAR:
 * 1. Reemplazar DEMO_ORDERS por la llamada a la API usando el id de la ruta.
 * 2. Implementar Cerrar comanda y Generar factura.
 * 3. Conectar la edición de ítems y el estado de cada producto.
 */
import {
  Badge,
  Breadcrumb,
  Button,
  Card,
  DataTable,
  DeleteButton,
  Field,
  KeyValue,
  PageHeader,
  Select,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { DEMO_CUSTOMERS } from '../customers/demo'
import { DEMO_RESERVATIONS } from '../reservations/demo'
import { DEMO_TABLES } from '../tables/demo'
import { DEMO_WAITERS } from '../waiters/demo'
import { DEMO_ORDERS } from './demo'
import type { OrderItem } from './types'

const formatCurrency = (value: number) => `$ ${value.toLocaleString('es-AR')}`

const itemColumns: DataTableColumn<OrderItem>[] = [
  {
    key: 'name',
    header: 'Producto',
    render: (item) => (
      <>
        <div className="cell-main">{item.name}</div>
        <div className="cell-sub">{formatCurrency(item.unitPrice)} c/u</div>
      </>
    ),
  },
  {
    key: 'quantity',
    header: 'Cant.',
    num: true,
  },
  {
    key: 'note',
    header: 'Observaciones',
    render: (item) => item.note ?? '—',
  },
  {
    key: 'total',
    header: 'Subtotal',
    num: true,
    render: (item) => formatCurrency(item.quantity * item.unitPrice),
  },
  {
    key: 'status',
    header: 'Entrega',
    render: (item) => (
      <Badge tone={item.status === 'pendiente' ? 'warning' : 'success'}>
        {item.status === 'pendiente' ? 'Pendiente' : 'Entregado'}
      </Badge>
    ),
  },
]

export function OrderDetailPage({ id }: { id: string }) {
  const order = DEMO_ORDERS.find((candidate) => candidate.id === id) ?? DEMO_ORDERS[0]
  const pendingItems = order.items.filter((item) => item.status === 'pendiente').length
  const itemsSummary = `${order.items.length} ítems${
    pendingItems > 0
      ? ` · ${pendingItems} ${pendingItems === 1 ? 'pendiente' : 'pendientes'} de entrega`
      : ''
  }`

  // TODO(equipo-operacion): cargar las opciones desde la API.
  return (
    <>
      <PageHeader
        breadcrumb={<Breadcrumb items={[{ label: 'Comandas', href: '#/comandas' }, { label: `#${order.id}` }]} />}
        title={
          <>
            Comanda #{order.id}{' '}
            <Badge tone={order.status === 'abierta' ? 'warning' : 'success'}>
              {order.status === 'abierta' ? 'Abierta' : 'Cerrada'}
            </Badge>
          </>
        }
        subtitle={`${order.table} · ${order.sector} · abierta a las ${order.openedAt}`}
        actions={
          <DeleteButton
            label="Eliminar comanda"
            title="Eliminar comanda"
            confirmLabel="Eliminar comanda"
            onConfirm={() => {
              // TODO(equipo-operacion): eliminar la comanda en la API.
            }}
          >
            ¿Querés eliminar la comanda <strong>#{order.id}</strong>?
          </DeleteButton>
        }
      />

      <div className="layout-aside">
        <div className="primary stack">
          <Card title="Datos de la comanda">
            <div className="form-grid">
              <Field label="Mesa">
                <Select defaultValue={order.table}>
                  {DEMO_TABLES.map((table) => (
                    <option key={table.id} value={table.number}>
                      {table.number}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="Mozo">
                <Select defaultValue={order.waiter}>
                  {DEMO_WAITERS.map((waiter) => (
                    <option key={waiter.id} value={waiter.name}>
                      {waiter.name}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="Cliente">
                <Select defaultValue={order.customer ?? 'Cliente ocasional'}>
                  <option value="Cliente ocasional">Cliente ocasional</option>
                  {DEMO_CUSTOMERS.map((customer) => (
                    <option key={customer.id} value={customer.name}>
                      {customer.name}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="Reserva">
                <Select defaultValue={order.reservation ?? 'Sin reserva asociada'}>
                  <option value="Sin reserva asociada">Sin reserva asociada</option>
                  {DEMO_RESERVATIONS.map((reservation) => (
                    <option
                      key={reservation.id}
                      value={`${reservation.time} · ${reservation.customer}`}
                    >
                      {reservation.time} · {reservation.customer}
                    </option>
                  ))}
                </Select>
              </Field>
            </div>
          </Card>

          <Card
            title="Productos pedidos"
            subtitle={itemsSummary}
            flush
            actions={
              <Button
                size="sm"
                onClick={() => {
                  // TODO(equipo-operacion): abrir el selector de productos de la carta.
                }}
              >
                Agregar producto
              </Button>
            }
          >
            <DataTable
              columns={itemColumns}
              rows={order.items}
              actions={() => (
                <div className="row">
                  <Button
                    size="sm"
                    onClick={() => {
                      // TODO(equipo-operacion): editar el ítem de la comanda.
                    }}
                  >
                    Editar
                  </Button>
                  <Button
                    size="sm"
                    variant="danger-ghost"
                    onClick={() => {
                      // TODO(equipo-operacion): quitar el ítem de la comanda.
                    }}
                  >
                    Quitar
                  </Button>
                </div>
              )}
            />
          </Card>
        </div>

        <aside className="aside stack">
          <Card title="Resumen">
            <KeyValue label="Subtotal" value={formatCurrency(order.subtotal)} />
            {order.discount > 0 && (
              <KeyValue
                label={order.discountLabel ?? 'Descuento'}
                value={`− ${formatCurrency(order.discount)}`}
              />
            )}
            <KeyValue label="Total" value={formatCurrency(order.total)} total />
            <p className="hint">La factura se genera una vez cerrada la comanda.</p>
            <div className="stack">
              <Button
                variant="primary"
                block
                onClick={() => {
                  // TODO(equipo-operacion): cerrar la comanda en la API.
                }}
              >
                Cerrar comanda
              </Button>
              <Button
                block
                disabled={order.status === 'abierta'}
                onClick={() => {
                  // TODO(equipo-operacion): generar la factura de la comanda.
                }}
              >
                Generar factura
              </Button>
            </div>
          </Card>
        </aside>
      </div>
    </>
  )
}
