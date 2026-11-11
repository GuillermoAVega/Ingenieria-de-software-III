import { Alert, Badge, Button, Card, DataTable, EmptyState, PageHeader } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { PencilIcon } from '../../ui/PencilIcon'
import type { UserRecord } from './types'
import { useUsersList } from './useUsersList'

const columns: DataTableColumn<UserRecord>[] = [
  { key: 'nombre', header: 'Nombre', render: (user) => <span className="cell-main">{user.nombre}</span> },
  { key: 'usuario', header: 'Usuario', render: (user) => user.nombre_usuario },
  {
    key: 'rol',
    header: 'Rol',
    render: (user) => (user.rol === 'administrador' ? 'Administrador' : 'Operario'),
  },
  {
    key: 'estado',
    header: 'Estado',
    render: (user) => <Badge tone={user.activo ? 'success' : 'danger'}>{user.activo ? 'Activo' : 'Inactivo'}</Badge>,
  },
]

export function UsersListPage() {
  const state = useUsersList()
  return (
    <>
      <PageHeader
        title="Usuarios"
        subtitle="Accesos y roles habilitados para utilizar el sistema."
        actions={<Button variant="primary" onClick={() => navigate('/usuarios/nuevo')}>Nuevo usuario</Button>}
      />
      {state.error && <Alert tone="danger" title="No se pudieron cargar los usuarios">{state.error}</Alert>}
      <Card flush>
        {state.loading ? <p className="muted">Cargando usuarios...</p> : (
          <DataTable
            columns={columns}
            rows={state.users}
            empty={<EmptyState title="Sin usuarios">No hay usuarios registrados.</EmptyState>}
            actions={(user) => (
              <Button
                size="sm"
                className="btn-icon"
                title="Editar"
                aria-label={`Editar ${user.nombre}`}
                onClick={() => navigate(`/usuarios/${user.id}/editar`)}
              >
                <PencilIcon />
              </Button>
            )}
          />
        )}
      </Card>
    </>
  )
}
