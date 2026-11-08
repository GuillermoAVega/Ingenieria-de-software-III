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
  DateInput,
  DeleteButton,
  EmptyState,
  Input,
  Toolbar,
  ToolbarSpacer,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { formatDate } from '../menus/format'
import { useDailyMenusList } from './useDailyMenusList'
import type { ProductoMenuDetalle } from './api'

const columns: DataTableColumn<ProductoMenuDetalle>[] = [
  {
    key: 'fecha',
    header: 'Fecha',
    render: (menu) => <span className="cell-main">{formatDate(menu.fecha)}</span>,
  },
  {
    key: 'menu_del_dia',
    header: 'Menú del día',
    render: (menu) => (
      <div className="row">
        <span>{menu.menu_del_dia_nombre}</span>
        {menu.menu_del_dia_dado_de_baja && <Badge tone="warning">Dado de baja</Badge>}
      </div>
    ),
  },
]

export function DailyMenusTab() {
  const { state, menus, hasFilters, updateSearch, updateDateFilter, clearFilters, remove } = useDailyMenusList()

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
            placeholder="Buscar por menú del día"
            value={state.search}
            onChange={(event) => updateSearch(event.target.value)}
          />
          <div className="toolbar-filter">
            <span className="muted">Filtrar por fecha</span>
            <DateInput
              aria-label="Filtrar por fecha"
              value={state.dateFilter}
              onChange={updateDateFilter}
            />
          </div>
          {hasFilters && (
            <Button size="sm" onClick={clearFilters}>
              Limpiar
            </Button>
          )}
          <ToolbarSpacer />
          <Button onClick={() => navigate('/menus/dia/nuevo')}>Asignar menú del día</Button>
          <Button variant="primary" onClick={() => navigate('/productos/menus-del-dia/nuevo')}>
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
