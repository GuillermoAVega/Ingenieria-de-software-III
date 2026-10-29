/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Listado de productos de la carta
 * COMPLETAR:
 * 1. Reemplazar DEMO_PRODUCTS y DEMO_PRODUCT_TABS por la llamada a la API.
 * 2. Implementar las tabs, la búsqueda, el filtro por sección y la paginación.
 * 3. Conectar Editar y Eliminar con la API.
 */
import { useState } from 'react'
import {
  Button,
  Card,
  DataTable,
  DeleteButton,
  EmptyState,
  Input,
  PageHeader,
  Pagination,
  Select,
  Tabs,
  Toolbar,
  ToolbarSpacer,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_PRODUCTS, DEMO_PRODUCT_SECTIONS, DEMO_PRODUCT_TABS } from './demo'
import type { Product, ProductTabId } from './types'

const formatCurrency = (value: number) => `$ ${value.toLocaleString('es-AR')}`

const columns: DataTableColumn<Product>[] = [
  {
    key: 'name',
    header: 'Producto',
    render: (product) => <span className="cell-main">{product.name}</span>,
  },
  {
    key: 'section',
    header: 'Sección',
  },
  {
    key: 'price',
    header: 'Precio',
    num: true,
    render: (product) => formatCurrency(product.price),
  },
]

export function ProductsListPage() {
  const [activeTab, setActiveTab] = useState<ProductTabId>('platos')

  const rows = activeTab === 'platos' ? DEMO_PRODUCTS : []

  return (
    <>
      <PageHeader
        title="Productos"
        subtitle="Carta vigente, precios y secciones de cada producto."
        actions={
          <Button variant="primary" onClick={() => navigate('/productos/nuevo')}>
            Nuevo plato
          </Button>
        }
      />

      <Card flush>
        <Tabs
          tabs={DEMO_PRODUCT_TABS}
          active={activeTab}
          onChange={(id) => setActiveTab(id as ProductTabId)}
        />

        <Toolbar>
          <Input
            placeholder="Buscar producto..."
            onChange={() => {
              // TODO(equipo-carta): filtrar productos por texto.
            }}
          />
          <Select
            defaultValue=""
            onChange={() => {
              // TODO(equipo-carta): filtrar productos por sección.
            }}
          >
            <option value="">Todas las secciones</option>
            {DEMO_PRODUCT_SECTIONS.map((section) => (
              <option key={section} value={section}>
                {section}
              </option>
            ))}
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">Datos de demostración</span>
        </Toolbar>

        <DataTable
          columns={columns}
          rows={rows}
          empty={
            <EmptyState title="Sin productos en esta categoría">
              La categoría todavía no tiene productos cargados.
            </EmptyState>
          }
          actions={(product) => (
            <div className="row">
              <Button size="sm" onClick={() => navigate(`/productos/${product.id}/editar`)}>
                Editar
              </Button>
              <DeleteButton
                title="Eliminar plato"
                onConfirm={() => {
                  // TODO(equipo-carta): eliminar el producto en la API y refrescar el listado.
                }}
              >
                ¿Querés eliminar <strong>{product.name}</strong> de la carta? Esta acción no se puede
                deshacer.
              </DeleteButton>
            </div>
          )}
        />

        <Pagination
          page={1}
          pageSize={10}
          total={rows.length}
          onPageChange={() => {
            // TODO(equipo-carta): implementar la paginación contra la API.
          }}
        />
      </Card>
    </>
  )
}
