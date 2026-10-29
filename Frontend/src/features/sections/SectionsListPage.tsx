/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Listado de secciones
 * COMPLETAR:
 * 1. Reemplazar DEMO_SECTIONS por la llamada a la API.
 * 2. Implementar búsqueda y paginación.
 * 3. Conectar Editar y Eliminar con la API.
 */
import { Button, Card, DataTable, DeleteButton, Input, PageHeader, Pagination, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_SECTIONS } from './demo'
import type { Section } from './types'

const columns: DataTableColumn<Section>[] = [
  {
    key: 'name',
    header: 'Nombre',
    render: (section) => <span className="cell-main">{section.name}</span>,
  },
  {
    key: 'floor',
    header: 'Planta',
  },
  {
    key: 'condition',
    header: 'Condición',
  },
  {
    key: 'tableCount',
    header: 'Mesas',
    num: true,
  },
]

export function SectionsListPage() {
  return (
    <>
      <PageHeader
        title="Secciones"
        subtitle="Organización de los sectores que agrupan mesas y productos de la carta."
        actions={
          <Button variant="primary" onClick={() => navigate('/secciones/nueva')}>
            Nueva sección
          </Button>
        }
      />

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar sección..."
            onChange={() => {
              // TODO(equipo-carta): filtrar secciones por texto.
            }}
          />
          <ToolbarSpacer />
          <span className="muted text-sm">Datos de demostración</span>
        </Toolbar>

        <DataTable
          columns={columns}
          rows={DEMO_SECTIONS}
          actions={(section) => (
            <div className="row">
              <Button size="sm" onClick={() => navigate(`/secciones/${section.id}/editar`)}>
                Editar
              </Button>
              <DeleteButton
                title="Eliminar sección"
                onConfirm={() => {
                  // TODO(equipo-carta): eliminar la sección en la API.
                }}
              >
                ¿Querés eliminar <strong>{section.name}</strong>?
              </DeleteButton>
            </div>
          )}
        />

        <Pagination
          page={1}
          pageSize={10}
          total={DEMO_SECTIONS.length}
          onPageChange={() => {
            // TODO(equipo-carta): implementar la paginación contra la API.
          }}
        />
      </Card>
    </>
  )
}
