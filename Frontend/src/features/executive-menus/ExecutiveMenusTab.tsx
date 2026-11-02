/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Listado de menús ejecutivos
 * La lógica vive en `useExecutiveMenusList`; el componente solo renderiza.
 */
import {
  Alert,
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
import { formatCurrency } from '../menus/format'
import { useExecutiveMenusList } from './useExecutiveMenusList'
import type { MenuEjecutivoRespuesta } from './api'

export function ExecutiveMenusTab() {
  const { state, menus, platoById, postreById, seccionById, updateSearch, remove } =
    useExecutiveMenusList()

  const columns: DataTableColumn<MenuEjecutivoRespuesta>[] = [
    {
      key: 'nombre',
      header: 'Menú',
      render: (menu) => <span className="cell-main">{menu.nombre}</span>,
    },
    {
      key: 'plato',
      header: 'Plato',
      render: (menu) => platoById.get(menu.plato_id) ?? `#${menu.plato_id}`,
    },
    {
      key: 'postre',
      header: 'Postre',
      render: (menu) => postreById.get(menu.postre_id) ?? `#${menu.postre_id}`,
    },
    {
      key: 'precio',
      header: 'Precio',
      num: true,
      render: (menu) => formatCurrency(menu.precio),
    },
    {
      key: 'seccion',
      header: 'Sección',
      render: (menu) =>
        menu.seccion_id === null ? '—' : (seccionById.get(menu.seccion_id) ?? '—'),
    },
  ]

  return (
    <>
      {state.error && (
        <Alert tone="danger" title="No se pudieron cargar los menús ejecutivos">
          {state.error}
        </Alert>
      )}

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar por menú, plato o postre..."
            value={state.search}
            onChange={(event) => updateSearch(event.target.value)}
          />
          <ToolbarSpacer />
          <Button variant="primary" onClick={() => navigate('/menus/ejecutivos/nuevo')}>
            Nuevo menú ejecutivo
          </Button>
        </Toolbar>

        {state.loading ? (
          <p className="muted">Cargando menús ejecutivos...</p>
        ) : (
          <DataTable
            columns={columns}
            rows={menus}
            empty={
              <EmptyState title="Sin menús ejecutivos">
                Todavía no hay menús ejecutivos activos cargados.
              </EmptyState>
            }
            actions={(menu) => (
              <div className="row">
                <Button
                  size="sm"
                  onClick={() => navigate(`/menus/ejecutivos/${menu.id}/editar`)}
                  disabled={state.deletingId === menu.id}
                >
                  Editar
                </Button>
                <DeleteButton
                  title="Dar de baja menú ejecutivo"
                  onConfirm={() => {
                    void remove(menu.id)
                  }}
                >
                  ¿Querés dar de baja <strong>{menu.nombre}</strong>? Dejará de mostrarse en la
                  carta.
                </DeleteButton>
              </div>
            )}
          />
        )}
      </Card>
    </>
  )
}
