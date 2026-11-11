/**
 * EQUIPO: Operación
 * FUNCIONALIDAD: Listado de facturas
 * La lógica vive en `useBillingList`; la pantalla solo renderiza.
 * Las facturas se generan desde el detalle de cada comanda cerrada.
 */
import {
  Alert,
  Badge,
  Button,
  Card,
  DataTable,
  DateInput,
  EmptyState,
  Input,
  PageHeader,
  Pagination,
  Stat,
  Toolbar,
  ToolbarSpacer,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { EyeIcon } from '../../ui/EyeIcon'
import { formatCurrency, formatDateTime } from '../../utils/format'
import { PAYMENT_STATUS_LABEL, PAYMENT_STATUS_TONE } from '../payments/status'
import { useBillingList } from './useBillingList'
import type { BillingRow } from './types'

const columns: DataTableColumn<BillingRow>[] = [
  {
    key: 'id',
    header: 'Factura',
    render: (invoice) => (
      <>
        <div className="cell-main">#{invoice.id}</div>
        <div className="cell-sub">Comanda #{invoice.comanda_id}</div>
      </>
    ),
  },
  {
    key: 'fecha',
    header: 'Fecha de emisión',
    render: (invoice) => formatDateTime(invoice.fecha_hora_emision),
  },
  {
    key: 'total',
    header: 'Total',
    num: true,
    render: (invoice) => formatCurrency(invoice.importe_total),
  },
  {
    key: 'pagado',
    header: 'Pagado',
    num: true,
    render: (invoice) => formatCurrency(invoice.paid),
  },
  {
    key: 'estado',
    header: 'Estado',
    render: (invoice) => (
      <Badge tone={PAYMENT_STATUS_TONE[invoice.paymentStatus]}>
        {PAYMENT_STATUS_LABEL[invoice.paymentStatus]}
      </Badge>
    ),
  },
]

export function BillingListPage() {
  const {
    state,
    invoices,
    total,
    totalAmount,
    averageTicket,
    page,
    pageSize,
    updateSearch,
    updateDate,
    changePage,
  } = useBillingList()

  return (
    <>
      <PageHeader
        title="Facturación"
        subtitle="Facturas emitidas, lo cobrado y su estado de pago."
      />

      {state.error && (
        <Alert tone="danger" title="No se pudieron cargar las facturas">
          {state.error}
        </Alert>
      )}

      <div className="grid-auto">
        <Card flush>
          <Stat label="Facturado" value={formatCurrency(totalAmount)} hint="Según los filtros aplicados" />
        </Card>
        <Card flush>
          <Stat label="Facturas" value={total} hint="Emitidas y vigentes" />
        </Card>
        <Card flush>
          <Stat label="Ticket promedio" value={formatCurrency(averageTicket)} hint="Facturado / facturas" />
        </Card>
      </div>

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar por número de factura o comanda..."
            value={state.search}
            onChange={(event) => updateSearch(event.target.value)}
          />
          <DateInput
            aria-label="Filtrar por fecha de emisión"
            value={state.date}
            onChange={updateDate}
          />
          {state.date && (
            <Button size="sm" onClick={() => updateDate('')}>
              Quitar fecha
            </Button>
          )}
          <ToolbarSpacer />
          <span className="muted text-sm">{total} facturas</span>
        </Toolbar>

        {state.loading ? (
          <p className="muted">Cargando facturas...</p>
        ) : (
          <DataTable
            columns={columns}
            rows={invoices}
            empty={
              <EmptyState title="Sin facturas para mostrar">
                Todavía no hay facturas o ninguna coincide con los filtros elegidos.
              </EmptyState>
            }
            actions={(invoice) => (
              <Button
                size="sm"
                className="btn-icon"
                title="Ver comanda"
                aria-label={`Ver comanda #${invoice.comanda_id}`}
                onClick={() => navigate(`/comandas/${invoice.comanda_id}`)}
              >
                <EyeIcon />
              </Button>
            )}
          />
        )}

        <Pagination
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={changePage}
          label={`Página ${page} · ${total} facturas`}
        />
      </Card>
    </>
  )
}
