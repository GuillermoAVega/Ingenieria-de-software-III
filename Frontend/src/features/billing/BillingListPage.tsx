/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Listado de comprobantes y facturación
 * COMPLETAR:
 * 1. Reemplazar DEMO_INVOICES y DEMO_BILLING_SUMMARY por la API.
 * 2. Implementar filtros por fecha, estado y medio de pago.
 * 3. Definir el contrato de emisión y anulación de comprobantes.
 */
import { Alert, Badge, Button, Card, DataTable, Input, PageHeader, Pagination, Select, Stat, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { BadgeTone, DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_BILLING_SUMMARY, DEMO_INVOICES } from './demo'
import type { Invoice, InvoiceStatus } from './types'

const formatCurrency = (value: number) => `$ ${value.toLocaleString('es-AR')}`

const statusLabel: Record<InvoiceStatus, string> = {
  emitida: 'Emitida',
  anulada: 'Anulada',
  pendiente: 'Pendiente',
}

const statusTone: Record<InvoiceStatus, BadgeTone> = {
  emitida: 'success',
  anulada: 'danger',
  pendiente: 'warning',
}

const columns: DataTableColumn<Invoice>[] = [
  {
    key: 'number',
    header: 'Comprobante',
    render: (invoice) => (
      <>
        <div className="cell-main">{invoice.number}</div>
        <div className="cell-sub">Comanda #{invoice.orderId}</div>
      </>
    ),
  },
  {
    key: 'issuedAt',
    header: 'Fecha',
  },
  {
    key: 'customer',
    header: 'Cliente',
  },
  {
    key: 'paymentMethod',
    header: 'Medio de pago',
  },
  {
    key: 'total',
    header: 'Total',
    num: true,
    render: (invoice) => formatCurrency(invoice.total),
  },
  {
    key: 'status',
    header: 'Estado',
    render: (invoice) => <Badge tone={statusTone[invoice.status]}>{statusLabel[invoice.status]}</Badge>,
  },
]

export function BillingListPage() {
  return (
    <>
      <PageHeader
        title="Facturación"
        subtitle="Comprobantes emitidos y resumen de cobros del día."
        actions={
          <Button
            variant="primary"
            onClick={() => {
              // TODO(equipo-operacion): abrir el flujo de emisión de factura.
            }}
          >
            Emitir factura
          </Button>
        }
      />

      <Alert tone="info" title="Pantalla de referencia">
        La facturación no aparece en el PDF original. Este listado es un contrato propuesto para que el
        equipo de Operación lo complete junto con la API.
      </Alert>

      <div className="grid-auto">
        <Card flush>
          <Stat
            label="Facturado hoy"
            value={formatCurrency(DEMO_BILLING_SUMMARY.totalToday)}
            hint="Incluye todos los medios de pago"
          />
        </Card>
        <Card flush>
          <Stat
            label="Comprobantes"
            value={DEMO_BILLING_SUMMARY.invoiceCount}
            hint="Emitidos durante la jornada"
          />
        </Card>
        <Card flush>
          <Stat
            label="Ticket promedio"
            value={formatCurrency(DEMO_BILLING_SUMMARY.averageTicket)}
            hint="Facturado hoy / comprobantes"
          />
        </Card>
      </div>

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar por comprobante o cliente..."
            onChange={() => {
              // TODO(equipo-operacion): filtrar comprobantes por texto.
            }}
          />
          <Input
            type="date"
            defaultValue="2026-10-16"
            onChange={() => {
              // TODO(equipo-operacion): filtrar comprobantes por fecha.
            }}
          />
          <Select
            defaultValue=""
            onChange={() => {
              // TODO(equipo-operacion): filtrar comprobantes por estado.
            }}
          >
            <option value="">Todos los estados</option>
            <option value="emitida">Emitidos</option>
            <option value="anulada">Anulados</option>
            <option value="pendiente">Pendientes</option>
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">Datos de demostración</span>
        </Toolbar>

        <DataTable
          columns={columns}
          rows={DEMO_INVOICES}
          actions={(invoice) => (
            <Button size="sm" onClick={() => navigate(`/comandas/${invoice.orderId}`)}>
              Ver comanda
            </Button>
          )}
        />

        <Pagination
          page={1}
          pageSize={10}
          total={DEMO_INVOICES.length}
          onPageChange={() => {
            // TODO(equipo-operacion): implementar la paginación contra la API.
          }}
        />
      </Card>
    </>
  )
}
