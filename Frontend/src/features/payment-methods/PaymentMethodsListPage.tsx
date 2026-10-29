/**
 * EQUIPO: Administración
 * FUNCIONALIDAD: Listado de medios de pago
 * COMPLETAR:
 * 1. Reemplazar DEMO_PAYMENT_METHODS por la llamada a la API.
 * 2. Implementar búsqueda, filtro por estado y paginación.
 * 3. Conectar Editar y Dar de baja con la API.
 */
import { Badge, Button, Card, DataTable, DeleteButton, Input, PageHeader, Pagination, Select, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_PAYMENT_METHODS } from './demo'
import type { PaymentMethod } from './types'

const columns: DataTableColumn<PaymentMethod>[] = [
  {
    key: 'name',
    header: 'Medio de pago',
    render: (method) => <span className="cell-main">{method.name}</span>,
  },
  {
    key: 'type',
    header: 'Tipo',
  },
  {
    key: 'surcharge',
    header: 'Recargo',
    num: true,
    render: (method) => `${method.surcharge}%`,
  },
  {
    key: 'active',
    header: 'Estado',
    render: (method) => (
      <Badge tone={method.active ? 'success' : 'neutral'}>
        {method.active ? 'Activo' : 'Inactivo'}
      </Badge>
    ),
  },
]

export function PaymentMethodsListPage() {
  return (
    <>
      <PageHeader
        title="Medios de pago"
        subtitle="Formas de cobro disponibles, recargos y estado de cada medio."
        actions={
          <Button variant="primary" onClick={() => navigate('/medios-de-pago/nuevo')}>
            Nuevo medio de pago
          </Button>
        }
      />

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar medio de pago..."
            onChange={() => {
              // TODO(equipo-administracion): filtrar medios de pago por texto.
            }}
          />
          <Select
            defaultValue=""
            onChange={() => {
              // TODO(equipo-administracion): filtrar medios de pago por estado.
            }}
          >
            <option value="">Todos los estados</option>
            <option value="activo">Activos</option>
            <option value="inactivo">Inactivos</option>
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">Datos de demostración</span>
        </Toolbar>

        <DataTable
          columns={columns}
          rows={DEMO_PAYMENT_METHODS}
          actions={(method) => (
            <div className="row">
              <Button size="sm" onClick={() => navigate(`/medios-de-pago/${method.id}/editar`)}>
                Editar
              </Button>
              <DeleteButton
                label="Dar de baja"
                title="Dar de baja medio de pago"
                confirmLabel="Dar de baja"
                onConfirm={() => {
                  // TODO(equipo-administracion): dar de baja el medio de pago en la API.
                }}
              >
                ¿Querés dar de baja <strong>{method.name}</strong>?
              </DeleteButton>
            </div>
          )}
        />

        <Pagination
          page={1}
          pageSize={10}
          total={DEMO_PAYMENT_METHODS.length}
          onPageChange={() => {
            // TODO(equipo-administracion): implementar la paginación contra la API.
          }}
        />
      </Card>
    </>
  )
}
