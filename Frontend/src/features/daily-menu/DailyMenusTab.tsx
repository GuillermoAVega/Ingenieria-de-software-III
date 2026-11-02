/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Listado de menús del día
 * La lógica vive en `useDailyMenusList`; el componente solo renderiza.
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
  Toolbar,
  ToolbarSpacer,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { formatDate, tipoLabel } from '../menus/format'
import { useDailyMenusList } from './useDailyMenusList'
import type { ProductoMenuDetalle } from './api'

const columns: DataTableColumn<ProductoMenuDetalle>[] = [
  {
    key: 'fecha',
    header: 'Fecha',
    render: (menu) => <span className="cell-main">{formatDate(menu.fecha)}</span>,
  },
  {
    key: 'producto',
    header: 'Producto',
    render: (menu) => (
      <div className="row">
        <span>{menu.producto_nombre}</span>
        {menu.producto_dado_de_baja && <Badge tone="warning">Dado de baja</Badge>}
      </div>
    ),
  },
  {
    key: 'tipo',
    header: 'Tipo',
    render: (menu) => tipoLabel(menu.producto_tipo),
  },
]

export function DailyMenusTab() {
  const { state, menus, updateSearch, remove } = useDailyMenusList()

  return (
    <>
      {state.error && (
        <Alert tone="danger" title="No se pudieron cargar los menús del día">
          {state.error}
        </Alert>
      )}

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar por producto, tipo o fecha..."
            value={state.search}
            onChange={(event) => updateSearch(event.target.value)}
          />
          <ToolbarSpacer />
          <Button variant="primary" onClick={() => navigate('/menus/dia/nuevo')}>
            Nuevo menú del día
          </Button>
        </Toolbar>

        {state.loading ? (
          <p className="muted">Cargando menús del día...</p>
        ) : (
          <DataTable
            columns={columns}
            rows={menus}
            empty={
              <EmptyState title="Sin menús del día">
                Todavía no hay fechas con menú del día cargado.
              </EmptyState>
            }
            actions={(menu) => (
              <div className="row">
                <Button
                  size="sm"
                  onClick={() => navigate(`/menus/dia/${menu.id}/editar`)}
                  disabled={state.deletingId === menu.id}
                >
                  Editar
                </Button>
                <DeleteButton
                  title="Eliminar menú del día"
                  onConfirm={() => {
                    void remove(menu.id)
                  }}
                >
                  ¿Querés eliminar el menú del <strong>{formatDate(menu.fecha)}</strong>? Esta
                  acción no se puede deshacer.
                </DeleteButton>
              </div>
            )}
          />
        )}
      </Card>
    </>
  )
}
