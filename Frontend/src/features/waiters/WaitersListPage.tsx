/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Listado de mozos
 * COMPLETAR:
 * 1. Reemplazar DEMO_WAITERS por la llamada a la API.
 * 2. Implementar búsqueda, filtro por estado y paginación.
 * 3. Conectar Editar y Dar de baja con la API.
 */
import { Badge, Button, Card, DataTable, DeleteButton, Input, PageHeader, Pagination, Select, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_WAITERS } from './demo'
import type { Waiter } from './types'

const columns: DataTableColumn<Waiter>[] = [
  {
    key: 'name',
    header: 'Mozo',
    render: (waiter) => <span className="cell-main">{waiter.name}</span>,
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
    key: 'status',
    header: 'Estado',
    render: (waiter) => (
      <Badge tone={waiter.status === 'activo' ? 'success' : 'neutral'}>
        {waiter.status === 'activo' ? 'Activo' : 'Inactivo'}
      </Badge>
    ),
  },
]

export function WaitersListPage() {
  return (
    <>
      <PageHeader
        title="Mozos"
        subtitle="Equipo de salón, datos de contacto y estado de cada mozo."
        actions={
          <Button variant="primary" onClick={() => navigate('/mozos/nuevo')}>
            Nuevo mozo
          </Button>
        }
      />

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar mozo..."
            onChange={() => {
              // TODO(equipo-salon): filtrar mozos por texto.
            }}
          />
          <Select
            defaultValue=""
            onChange={() => {
              // TODO(equipo-salon): filtrar mozos por estado.
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
          rows={DEMO_WAITERS}
          actions={(waiter) => (
            <div className="row">
              <Button size="sm" onClick={() => navigate(`/mozos/${waiter.id}/editar`)}>
                Editar
              </Button>
              <DeleteButton
                label="Dar de baja"
                title="Dar de baja mozo"
                confirmLabel="Dar de baja"
                onConfirm={() => {
                  // TODO(equipo-salon): dar de baja al mozo en la API.
                }}
              >
                ¿Querés dar de baja a <strong>{waiter.name}</strong>?
              </DeleteButton>
            </div>
          )}
        />

        <Pagination
          page={1}
          pageSize={10}
          total={DEMO_WAITERS.length}
          onPageChange={() => {
            // TODO(equipo-salon): implementar la paginación contra la API.
          }}
        />
      </Card>
    </>
  )
}
