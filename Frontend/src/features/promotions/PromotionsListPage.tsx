/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Listado de promociones
 * COMPLETAR:
 * 1. Reemplazar DEMO_PROMOTIONS por la llamada a la API.
 * 2. Implementar búsqueda, filtro por estado y paginación.
 * 3. Conectar Editar y Eliminar con la API.
 */
import { Badge, Button, Card, DataTable, DeleteButton, Input, PageHeader, Pagination, Select, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_PROMOTIONS } from './demo'
import type { Promotion } from './types'

const formatCurrency = (value: number) => `$ ${value.toLocaleString('es-AR')}`

const formatDiscount = (promotion: Promotion) =>
  promotion.discountType === 'Porcentaje'
    ? `${promotion.discountValue}%`
    : formatCurrency(promotion.discountValue)

const columns: DataTableColumn<Promotion>[] = [
  {
    key: 'name',
    header: 'Nombre',
    render: (promotion) => <span className="cell-main">{promotion.name}</span>,
  },
  {
    key: 'appliesTo',
    header: 'Aplica a',
  },
  {
    key: 'discountValue',
    header: 'Descuento',
    num: true,
    render: (promotion) => formatDiscount(promotion),
  },
  {
    key: 'from',
    header: 'Vigencia',
    render: (promotion) => `${promotion.from} → ${promotion.to}`,
  },
  {
    key: 'active',
    header: 'Estado',
    render: (promotion) => (
      <Badge tone={promotion.active ? 'success' : 'neutral'}>
        {promotion.active ? 'Activa' : 'Inactiva'}
      </Badge>
    ),
  },
]

export function PromotionsListPage() {
  return (
    <>
      <PageHeader
        title="Promociones"
        subtitle="Descuentos vigentes sobre productos y combinaciones de la carta."
        actions={
          <Button variant="primary" onClick={() => navigate('/promociones/nueva')}>
            Nueva promoción
          </Button>
        }
      />

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar promoción..."
            onChange={() => {
              // TODO(equipo-carta): filtrar promociones por texto.
            }}
          />
          <Select
            defaultValue=""
            onChange={() => {
              // TODO(equipo-carta): filtrar promociones por estado.
            }}
          >
            <option value="">Todos los estados</option>
            <option value="activa">Activas</option>
            <option value="inactiva">Inactivas</option>
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">Datos de demostración</span>
        </Toolbar>

        <DataTable
          columns={columns}
          rows={DEMO_PROMOTIONS}
          actions={(promotion) => (
            <div className="row">
              <Button size="sm" onClick={() => navigate(`/promociones/${promotion.id}/editar`)}>
                Editar
              </Button>
              <DeleteButton
                title="Eliminar promoción"
                onConfirm={() => {
                  // TODO(equipo-carta): eliminar la promoción en la API.
                }}
              >
                ¿Querés eliminar <strong>{promotion.name}</strong>?
              </DeleteButton>
            </div>
          )}
        />

        <Pagination
          page={1}
          pageSize={10}
          total={DEMO_PROMOTIONS.length}
          onPageChange={() => {
            // TODO(equipo-carta): implementar la paginación contra la API.
          }}
        />
      </Card>
    </>
  )
}
