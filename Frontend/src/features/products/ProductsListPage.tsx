/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Listado de productos de la carta
 * La lógica vive en `useProductsList`; la pantalla solo renderiza.
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
  Select,
  Tabs,
  Toolbar,
  ToolbarSpacer,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { PRODUCT_TABS, useProductsList } from './useProductsList'
import type { ProductListItem } from './useProductsList'

const formatCurrency = (value: string) => `$ ${Number(value).toLocaleString('es-AR')}`

const SINGULAR: Record<string, string> = {
  platos: 'plato',
  bebidas: 'bebida',
  postres: 'postre',
}

export function ProductsListPage() {
  const { state, products, updateTab, updateSearch, updateSection, remove } = useProductsList()

  const sectionsById = new Map(state.sections.map((section) => [section.id, section.nombre]))
  const tabs = PRODUCT_TABS.map((tab) => ({ ...tab }))

  const columns: DataTableColumn<ProductListItem>[] = [
    {
      key: 'nombre',
      header: 'Producto',
      render: (product) => <span className="cell-main">{product.nombre}</span>,
    },
    {
      key: 'seccion',
      header: 'Sección',
      render: (product) =>
        product.seccion_id === null ? '—' : (sectionsById.get(product.seccion_id) ?? '—'),
    },
    {
      key: 'precio',
      header: 'Precio',
      num: true,
      render: (product) => formatCurrency(product.precio),
    },
  ]

  return (
    <>
      <PageHeader
        title="Productos"
        subtitle="Carta vigente, precios y secciones de cada producto."
        actions={
          <Button
            variant="primary"
            onClick={() => navigate(`/productos/${state.activeTab}/nuevo`)}
          >
            Nuevo {SINGULAR[state.activeTab]}
          </Button>
        }
      />

      {state.error && (
        <Alert tone="danger" title="No se pudieron cargar los productos">
          {state.error}
        </Alert>
      )}

      <Card flush>
        <Tabs tabs={tabs} active={state.activeTab} onChange={updateTab} />

        <Toolbar>
          <Input
            placeholder="Buscar producto..."
            value={state.search}
            onChange={(event) => updateSearch(event.target.value)}
          />
          <Select
            value={state.sectionId}
            onChange={(event) => updateSection(event.target.value)}
            disabled={state.sectionsLoading}
          >
            <option value="">Todas las secciones</option>
            {state.sections.map((section) => (
              <option key={section.id} value={section.id}>
                {section.nombre}
              </option>
            ))}
          </Select>
          <ToolbarSpacer />
        </Toolbar>

        {state.loading ? (
          <p className="muted">Cargando productos...</p>
        ) : (
          <DataTable
            columns={columns}
            rows={products}
            empty={
              <EmptyState title="Sin productos en esta categoría">
                La categoría todavía no tiene productos activos cargados.
              </EmptyState>
            }
            actions={(product) => (
              <div className="row">
                <Button
                  size="sm"
                  onClick={() => navigate(`/productos/${state.activeTab}/${product.id}/editar`)}
                  disabled={state.deletingId === product.id}
                >
                  Editar
                </Button>
                <DeleteButton
                  title={`Eliminar ${SINGULAR[state.activeTab]}`}
                  onConfirm={() => {
                    void remove(product.id)
                  }}
                >
                  ¿Querés eliminar <strong>{product.nombre}</strong> de la carta? Esta acción no se
                  puede deshacer.
                </DeleteButton>
              </div>
            )}
          />
        )}
      </Card>
    </>
  )
}
