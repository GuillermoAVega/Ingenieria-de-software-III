/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Listado de secciones
 * La lógica vive en `useSectionsList`; la pantalla solo renderiza.
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
  Toolbar,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useSectionsList } from './useSectionsList'
import type { SeccionRespuesta } from './api'

const columns: DataTableColumn<SeccionRespuesta>[] = [
  {
    key: 'nombre',
    header: 'Nombre',
    render: (section) => <span className="cell-main">{section.nombre}</span>,
  },
  {
    key: 'subtitulo',
    header: 'Subtítulo',
    render: (section) => section.subtitulo ?? '—',
  },
  {
    key: 'posicion',
    header: 'Posición',
    num: true,
  },
  {
    key: 'productos',
    header: 'Productos',
    num: true,
    render: (section) => section.productos_ids.length,
  },
]

export function SectionsListPage() {
  const { state, sections, updateSearch, remove } = useSectionsList()

  return (
    <>
      <PageHeader
        title="Secciones"
        subtitle="Sectores de la carta y productos asignados a cada uno."
        actions={
          <Button variant="primary" onClick={() => navigate('/secciones/nueva')}>
            Nueva sección
          </Button>
        }
      />

      {state.error && (
        <Alert tone="danger" title="No se pudieron cargar las secciones">
          {state.error}
        </Alert>
      )}

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar sección..."
            value={state.search}
            onChange={(event) => updateSearch(event.target.value)}
          />
        </Toolbar>

        {state.loading ? (
          <p className="muted">Cargando secciones...</p>
        ) : (
          <DataTable
            columns={columns}
            rows={sections}
            empty={
              <EmptyState title="Sin secciones">
                Todavía no hay secciones cargadas en la carta.
              </EmptyState>
            }
            actions={(section) => (
              <div className="row">
                <Button
                  size="sm"
                  onClick={() => navigate(`/secciones/${section.id}/editar`)}
                  disabled={state.deletingId === section.id}
                >
                  Editar
                </Button>
                <DeleteButton
                  title="Eliminar sección"
                  onConfirm={() => {
                    void remove(section.id)
                  }}
                >
                  ¿Querés eliminar <strong>{section.nombre}</strong>? Los productos asignados quedarán
                  sin sección.
                </DeleteButton>
              </div>
            )}
          />
        )}
      </Card>
    </>
  )
}
