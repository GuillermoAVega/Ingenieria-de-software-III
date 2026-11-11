/**
 * EQUIPO: Administración
 * FUNCIONALIDAD: Listado de medios de pago
 * La lógica vive en `usePaymentMethodsList`; la pantalla solo renderiza.
 */
import {
  Alert,
  Button,
  Card,
  DataTable,
  DeleteButton,
  EmptyState,
  Input,
  PageHeader,
  Pagination,
  Toolbar,
  ToolbarSpacer,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { PencilIcon } from '../../ui/PencilIcon'
import { TrashIcon } from '../../ui/TrashIcon'
import { usePaymentMethodsList } from './usePaymentMethodsList'
import type { PaymentMethod } from './types'

const columns: DataTableColumn<PaymentMethod>[] = [
  {
    key: 'descripcion',
    header: 'Medio de pago',
    render: (method) => <span className="cell-main">{method.descripcion}</span>,
  },
]

export function PaymentMethodsListPage() {
  const { state, methods, total, page, pageSize, updateSearch, changePage, remove } =
    usePaymentMethodsList()

  return (
    <>
      <PageHeader
        title="Medios de pago"
        subtitle="Formas de cobro disponibles para los comprobantes de pago."
        actions={
          <Button variant="primary" onClick={() => navigate('/medios-de-pago/nuevo')}>
            Nuevo medio de pago
          </Button>
        }
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {state.error}
        </Alert>
      )}

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar medio de pago..."
            value={state.search}
            onChange={(event) => updateSearch(event.target.value)}
          />
          <ToolbarSpacer />
          <span className="muted text-sm">{total} medios de pago</span>
        </Toolbar>

        {state.loading ? (
          <p className="muted">Cargando medios de pago...</p>
        ) : (
          <DataTable
            columns={columns}
            rows={methods}
            empty={
              <EmptyState title="Sin medios de pago">
                No hay medios de pago que coincidan con la búsqueda.
              </EmptyState>
            }
            actions={(method) => (
              <div className="row row-icons">
                <Button
                  size="sm"
                  className="btn-icon"
                  title="Editar"
                  aria-label={`Editar ${method.descripcion}`}
                  onClick={() => navigate(`/medios-de-pago/${method.id}/editar`)}
                  disabled={state.deletingId === method.id}
                >
                  <PencilIcon />
                </Button>
                <DeleteButton
                  label="Dar de baja"
                  icon={<TrashIcon />}
                  title="Dar de baja medio de pago"
                  confirmLabel="Dar de baja"
                  onConfirm={() => {
                    void remove(method.id)
                  }}
                >
                  ¿Querés dar de baja <strong>{method.descripcion}</strong>? No se puede dar de baja
                  si tiene comprobantes de pago asociados.
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
          label={`Página ${page} · ${total} medios de pago`}
        />
      </Card>
    </>
  )
}
