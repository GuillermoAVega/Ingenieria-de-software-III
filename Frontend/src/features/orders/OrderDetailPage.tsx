/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Detalle de una comanda
 * La lógica vive en los hooks de la feature; la pantalla solo renderiza.
 */
import {
  Alert,
  Badge,
  Breadcrumb,
  Button,
  Card,
  DataTable,
  DeleteButton,
  Field,
  Input,
  KeyValue,
  Modal,
  Select,
  PageHeader,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { formatCurrency, formatDate, formatTime } from '../../utils/format'
import { ORDER_STATUS_LABEL, ORDER_STATUS_TONE } from './status'
import { useOrderDetail } from './useOrderDetail'
import { useOrderHeaderForm } from './useOrderHeaderForm'
import { useOrderItems } from './useOrderItems'
import { useOrderCatalog } from './useOrderCatalog'
import type { Order, OrderItem } from './types'

export function OrderDetailPage({ id }: { id: string }) {
  const numericId = Number(id)

  if (!Number.isInteger(numericId) || numericId <= 0) {
    return (
      <Alert tone="danger" title="Comanda inválida">
        El identificador de la comanda no es válido.
      </Alert>
    )
  }

  return <OrderDetail key={numericId} id={numericId} />
}

function OrderDetail({ id }: { id: number }) {
  const detail = useOrderDetail(id)
  const catalog = useOrderCatalog()
  const items = useOrderItems(id, detail.reload, catalog.state.products)
  const order = detail.state.order

  if (detail.state.loading && !order) {
    return (
      <Card>
        <p className="muted">Cargando comanda...</p>
      </Card>
    )
  }

  if (!order) {
    return (
      <Alert tone="danger" title="No se pudo cargar la comanda">
        {detail.state.error ?? 'La comanda solicitada no existe o fue eliminada.'}
      </Alert>
    )
  }

  const abierta = order.estado === 'abierta'
  const pendientes = order.detalles.filter((item) => !item.entregado).length
  const unidades = order.detalles.reduce((sum, item) => sum + item.cantidad, 0)
  const invoiceComplete = order.detalles.every((item) =>
    Boolean(detail.state.invoicePrices[item.id]?.trim()),
  )
  const invoiceTotal = order.detalles.reduce(
    (total, item) => total + Number(detail.state.invoicePrices[item.id] || 0) * item.cantidad,
    0,
  )

  const itemColumns: DataTableColumn<OrderItem>[] = [
    {
      key: 'producto',
      header: 'Producto',
      render: (item) => {
        const product = catalog.state.products.find((candidate) => candidate.id === item.producto_id)
        return (
          <span>
            <span className="cell-main">{product?.name ?? `Producto #${item.producto_id}`}</span>
            {product && <span className="cell-sub">{product.type}</span>}
          </span>
        )
      },
    },
    {
      key: 'cantidad',
      header: 'Cant.',
      num: true,
    },
    {
      key: 'observaciones',
      header: 'Observaciones',
      render: (item) => item.observaciones || '—',
    },
    {
      key: 'entrega',
      header: 'Entrega',
      render: (item) => (
        <Button
          size="sm"
          variant="ghost"
          className="delivery-status-button"
          onClick={() => {
            void items.toggleDelivered(item)
          }}
          disabled={items.state.deliveryUpdatingId === item.id}
          title={item.entregado ? 'Marcar como pendiente' : 'Marcar como entregado'}
          aria-label={item.entregado ? 'Marcar como pendiente' : 'Marcar como entregado'}
        >
          <Badge tone={item.entregado ? 'success' : 'warning'}>
            {item.entregado ? 'Entregado' : 'Pendiente'}
          </Badge>
        </Button>
      ),
    },
  ]

  return (
    <>
      <div className="order-detail-header">
      <PageHeader
        breadcrumb={<Breadcrumb items={[{ label: 'Comandas', href: '#/comandas' }, { label: `#${order.id}` }]} />}
        title={
          <>
            Comanda #{order.id} <Badge tone={ORDER_STATUS_TONE[order.estado]}>{ORDER_STATUS_LABEL[order.estado]}</Badge>
          </>
        }
        subtitle={`Mesa ${order.mesa_id} · ${formatDate(order.fecha)} · ${formatTime(order.hora)}`}
        actions={
          <DeleteButton
            label="Eliminar comanda"
            variant="danger"
            title="Eliminar comanda"
            confirmLabel="Eliminar comanda"
            onConfirm={() => {
              void detail.remove()
            }}
          >
            ¿Querés eliminar la comanda <strong>#{order.id}</strong>? Esta acción no se puede
            deshacer.
          </DeleteButton>
        }
      />
      </div>

      {detail.state.error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {detail.state.error}
        </Alert>
      )}

      {detail.state.success && <div className="order-notification"><Alert tone="success" title="Operación realizada">{detail.state.success}</Alert></div>}

      <div className="layout-aside">
        <div className="primary stack">
          <OrderHeaderCard
            key={`${order.id}-${order.mesa_id}-${order.mozo_id}-${order.cliente_id}-${order.reserva_id}`}
            order={order}
            onSaved={detail.reload}
            catalog={catalog}
          />

          <Card
            title="Productos pedidos"
            subtitle={`${order.detalles.length} ítems · ${pendientes} pendientes de entrega`}
            flush
            actions={
              <Button size="sm" disabled={!abierta} onClick={items.openNew}>
                Agregar producto
              </Button>
            }
          >
            <DataTable
              columns={itemColumns}
              rows={order.detalles}
              empty={
                <div className="empty">
                  <span className="empty-title">Todavía no se agregaron productos</span>
                </div>
              }
              actions={(item) => (
                <div className="row">
                  <Button size="sm" disabled={!abierta} onClick={() => items.openEdit(item)}>
                    Editar
                  </Button>
                  <DeleteButton
                    label="Quitar"
                    title="Quitar producto"
                    confirmLabel="Quitar producto"
                    onConfirm={() => {
                      void items.remove(item)
                    }}
                  >
                    ¿Querés quitar <strong>{catalog.state.products.find((product) => product.id === item.producto_id)?.name ?? `Producto #${item.producto_id}`}</strong> de la comanda?
                  </DeleteButton>
                </div>
              )}
            />

            {items.state.error && !items.state.modal && (
              <div className="card-body">
                <Alert tone="danger" title="No se pudo modificar el producto">
                  {items.state.error}
                </Alert>
              </div>
            )}
          </Card>
        </div>

        <aside className="aside">
          <Card title="Resumen">
            <KeyValue label="Ítems" value={`${unidades} unidades`} />
            <KeyValue label="Pendientes" value={pendientes} />
            {detail.state.invoice && (
              <>
                <KeyValue label="Factura" value={`#${detail.state.invoice.id}`} />
                <KeyValue label="Total facturado" value={formatCurrency(detail.state.invoice.importe_total)} total />
              </>
            )}

            {abierta ? (
              <Button
                variant="primary"
                block
                disabled={detail.state.statusSaving || order.detalles.length === 0}
                onClick={() => {
                  detail.requestClose()
                }}
              >
                {detail.state.statusSaving ? 'Guardando...' : 'Cerrar comanda'}
              </Button>
            ) : (
              <Button
                block
                disabled={detail.state.statusSaving || Boolean(detail.state.invoice)}
                onClick={() => {
                  void detail.changeStatus('abierta')
                }}
              >
                {detail.state.statusSaving ? 'Guardando...' : 'Reabrir comanda'}
              </Button>
            )}

            {detail.state.invoice ? (
              <Button block onClick={() => navigate('/facturacion')}>
                Ir a facturación
              </Button>
            ) : (
              <Button
                block
                disabled={abierta}
                onClick={() => detail.openInvoiceModal(Object.fromEntries(catalog.state.products.map((product) => [product.id, product.price])))}
              >
                Generar factura
              </Button>
            )}

            {!detail.state.invoice && abierta && (
              <p className="hint">{pendientes > 0 ? 'Entregá todos los productos para cerrar la comanda.' : 'La factura se genera una vez cerrada la comanda.'}</p>
            )}
          </Card>
        </aside>
      </div>

      <Modal
        open={items.state.modal !== null}
        title={items.state.modal?.mode === 'edit' ? 'Editar producto' : 'Agregar producto'}
        onClose={items.closeModal}
        footer={
          <>
            <Button onClick={items.closeModal} disabled={items.state.saving}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                void items.save()
              }}
              disabled={items.state.saving}
            >
              {items.state.saving ? 'Guardando...' : 'Guardar'}
            </Button>
          </>
        }
      >
        {items.state.error && (
          <Alert tone="danger" title="No se pudo guardar el producto">
            {items.state.error}
          </Alert>
        )}
        <Field label="Producto" required hint="Número de producto." error={items.state.fieldErrors.producto_id}>
          <div className="product-autocomplete">
            <Input
              value={items.state.productoQuery}
              onChange={(event) => items.updateField('productoQuery', event.target.value)}
              onFocus={items.openProductList}
              onBlur={items.closeProductList}
              autoFocus
            />
            {items.state.productListOpen && <div className="product-autocomplete-list">
              {catalog.state.products
                .filter((product) => product.name.toLocaleLowerCase().includes(items.state.productoQuery.toLocaleLowerCase()))
                .map((product) => (
                  <button
                    className="product-autocomplete-option"
                    key={product.id}
                    type="button"
                    onMouseDown={(event) => event.preventDefault()}
                    onClick={() => {
                      items.updateField('productoQuery', product.name)
                      items.closeProductList()
                    }}
                  >
                    <span>{product.name}</span>
                    <small>{product.type}</small>
                  </button>
                ))}
            </div>}
          </div>
        </Field>
        <Field label="Cantidad" required error={items.state.fieldErrors.cantidad}>
          <Input
            type="number"
            min={1}
            value={items.state.cantidad}
            onChange={(event) => items.updateField('cantidad', event.target.value)}
          />
        </Field>
        <Field label="Observaciones" error={items.state.fieldErrors.observaciones}>
          <Input
            value={items.state.observaciones}
            maxLength={255}
            onChange={(event) => items.updateField('observaciones', event.target.value)}
            placeholder="Ej.: Sin jamón"
          />
        </Field>
      </Modal>

      <Modal
        open={detail.state.invoiceModalOpen}
        className="invoice-modal"
        title="Generar factura"
        onClose={detail.closeInvoiceModal}
        footer={
          <>
            <Button onClick={detail.closeInvoiceModal} disabled={detail.state.invoiceSaving}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                void detail.generateInvoice()
              }}
              disabled={detail.state.invoiceSaving || !invoiceComplete}
            >
              {detail.state.invoiceSaving ? 'Generando...' : 'Generar factura'}
            </Button>
          </>
        }
      >
        {detail.state.invoiceError && (
          <Alert tone="danger" title="No se pudo generar la factura">
            {detail.state.invoiceError}
          </Alert>
        )}
        <p className="hint">Los precios se toman automáticamente de la carta.</p>
        {!invoiceComplete && <p className="error-text">Todos los productos deben tener un precio cargado para generar la factura.</p>}
        {order.detalles.map((item) => {
          const product = catalog.state.products.find((candidate) => candidate.id === item.producto_id)
          const unitPrice = detail.state.invoicePrices[item.id]
          const subtotal = Number(unitPrice || 0) * item.cantidad
          return (
          <Field key={item.id} required label={product ? `${product.name} · ${product.type} · Cantidad: ${item.cantidad}` : `Producto #${item.producto_id} · Cantidad: ${item.cantidad}`}>
            <div className="invoice-price-readonly">
              <span>{unitPrice ? `Precio unitario: ${formatCurrency(Number(unitPrice))}` : 'Sin precio cargado'}</span>
              {unitPrice && <strong>Subtotal: {formatCurrency(subtotal)}</strong>}
            </div>
          </Field>
          )
        })}
        <KeyValue label="Total de la factura" value={formatCurrency(invoiceTotal)} total />
      </Modal>

      <Modal
        open={detail.state.closeConfirmationOpen}
        title="Hay productos pendientes"
        onClose={detail.cancelClose}
        footer={
          <>
            <Button onClick={detail.cancelClose} disabled={detail.state.statusSaving}>Cancelar</Button>
            <Button variant="primary" onClick={() => void detail.confirmCloseWithPending()} disabled={detail.state.statusSaving}>
              {detail.state.statusSaving ? 'Cerrando...' : 'Cerrar igualmente'}
            </Button>
          </>
        }
      >
        <p>
          Todavía hay {pendientes} {pendientes === 1 ? 'producto pendiente' : 'productos pendientes'} de entrega.
          Si continuás, se marcarán automáticamente como entregados y la comanda se cerrará.
        </p>
      </Modal>
    </>
  )
}

function OrderHeaderCard({ order, onSaved, catalog }: { order: Order; onSaved: () => void; catalog: ReturnType<typeof useOrderCatalog> }) {
  const availableWaiters = catalog.getAvailableWaiters(order)
  const { state, isDirty, updateField, submit } = useOrderHeaderForm(order, onSaved)
  const bloqueada = order.estado !== 'abierta'
  const tableLabel = order.mesa_ids.length ? order.mesa_ids.map((mesaId) => `Mesa ${mesaId}`).join(', ') : 'Sin mesa'
  const customer = catalog.state.customers.find((candidate) => candidate.id === order.cliente_id)
  const customerLabel = customer ? `${customer.nombre} ${customer.apellido}` : order.cliente_id === null ? 'Sin cliente' : `Cliente #${order.cliente_id}`

  return (
    <Card
      title="Datos de la comanda"
      actions={
        <Button
          disabled={bloqueada || !isDirty || state.saving}
          onClick={() => {
            void submit()
          }}
        >
          {state.saving ? 'Guardando...' : 'Guardar cambios'}
        </Button>
      }
    >
      {state.error && (
        <Alert tone="danger" title="No se pudieron guardar los datos">
          {state.error}
        </Alert>
      )}

      <div className="form-grid">
        <Field label="Mesa" hint="Número de mesa." error={state.fieldErrors.mesa_id}>
          <Input
            type="text"
            min={1}
            value={tableLabel}
            readOnly
            disabled={bloqueada}
          />
        </Field>
        <Field label="Mozo" hint="Número de mozo." error={state.fieldErrors.mozo_id}>
          <Select value={state.mozoId} onChange={(event) => updateField('mozoId', event.target.value)} disabled={bloqueada}>
            <option value="">Sin mozo asignado</option>
            {availableWaiters.map((waiter) => <option key={waiter.id} value={waiter.id}>{waiter.name}</option>)}
          </Select>
        </Field>
        <Field
          label="Cliente"
          hint={order.reserva_id === null ? 'Opcional. Podés asociar un cliente.' : 'Cliente asociado a la reserva.'}
          error={state.fieldErrors.cliente_id}
        >
          {order.reserva_id === null ? (
            <Select value={state.clienteId} onChange={(event) => updateField('clienteId', event.target.value)} disabled={bloqueada}>
              <option value="">Sin cliente</option>
              {catalog.state.customers.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>{candidate.nombre} {candidate.apellido}</option>
              ))}
            </Select>
          ) : <div className="readonly-field">{customerLabel}</div>}
        </Field>
        <Field
          label="Reserva"
          hint="Opcional. Vacío = sin reserva."
          error={state.fieldErrors.reserva_id}
        >
          <Input
            type="text"
            min={1}
            value={order.reserva_id === null ? 'Sin reserva' : `Reserva #${order.reserva_id}`}
            readOnly
            disabled={bloqueada}
          />
        </Field>
      </div>
    </Card>
  )
}
