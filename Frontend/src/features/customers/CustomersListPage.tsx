/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Listado de clientes
 * COMPLETAR:
 * 1. Reemplazar DEMO_CUSTOMERS por la llamada a la API.
 * 2. Implementar búsqueda, orden por visitas y paginación.
 * 3. Conectar Editar y el historial de visitas con la API.
 */
import { Button, Card, DataTable, DeleteButton, Input, PageHeader, Pagination, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_CUSTOMERS } from './demo'
import type { Customer } from './types'

const columns: DataTableColumn<Customer>[] = [
  {
    key: 'name',
    header: 'Cliente',
    render: (customer) => <span className="cell-main">{customer.name}</span>,
  },
  {
    key: 'phone',
    header: 'Teléfono',
  },
  {
    key: 'email',
    header: 'Email',
  },
  {
    key: 'visits',
    header: 'Visitas',
    num: true,
  },
  {
    key: 'lastVisit',
    header: 'Última visita',
  },
]

export function CustomersListPage() {
  return (
    <>
      <PageHeader
        title="Clientes"
        subtitle="Ficha de clientes frecuentes, contacto e historial de visitas."
        actions={
          <Button variant="primary" onClick={() => navigate('/clientes/nuevo')}>
            Nuevo cliente
          </Button>
        }
      />

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar cliente por nombre o teléfono..."
            onChange={() => {
              // TODO(equipo-salon): filtrar clientes por texto.
            }}
          />
          <ToolbarSpacer />
          <span className="muted text-sm">Datos de demostración</span>
        </Toolbar>

        <DataTable
          columns={columns}
          rows={DEMO_CUSTOMERS}
          actions={(customer) => (
            <div className="row">
              <Button size="sm" onClick={() => navigate(`/clientes/${customer.id}/editar`)}>
                Editar
              </Button>
              <DeleteButton
                title="Eliminar cliente"
                onConfirm={() => {
                  // TODO(equipo-salon): eliminar el cliente en la API.
                }}
              >
                ¿Querés eliminar <strong>{customer.name}</strong>?
              </DeleteButton>
            </div>
          )}
        />

        <Pagination
          page={1}
          pageSize={10}
          total={DEMO_CUSTOMERS.length}
          onPageChange={() => {
            // TODO(equipo-salon): implementar la paginación contra la API.
          }}
        />
      </Card>
    </>
  )
}
