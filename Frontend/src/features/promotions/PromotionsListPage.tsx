/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Listado de promociones
 * La lógica vive en `usePromotionsList`; la pantalla solo renderiza.
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
  PageHeader,
  Select,
  Toolbar,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { usePromotionsList } from './usePromotionsList'
import type { PromotionStatusFilter } from './usePromotionsList'
import { formatBenefit } from './format'
import type { Promotion } from './types'

const IN_USE_REASON =
  'Ya se aplicó en facturas, por eso no se puede editar. Podés darla de baja y crear una nueva.'

const columns: DataTableColumn<Promotion>[] = [
  {
    key: 'nombre',
    header: 'Nombre',
    render: (promotion) => <span className="cell-main">{promotion.nombre}</span>,
  },
  {
    key: 'beneficio',
    header: 'Beneficio',
    render: (promotion) => formatBenefit(promotion),
  },
  {
    key: 'productos',
    header: 'Productos',
    num: true,
    render: (promotion) => promotion.productos_ids.length,
  },
  {
    key: 'vigencia',
    header: 'Vigencia',
    render: (promotion) => `${promotion.fecha_desde} → ${promotion.fecha_hasta}`,
  },
  {
    key: 'estado',
    header: 'Estado',
    render: (promotion) => (
      <Badge tone={promotion.dado_de_baja ? 'neutral' : 'success'}>
        {promotion.dado_de_baja ? 'De baja' : 'Activa'}
      </Badge>
    ),
  },
  {
    key: 'uso',
    header: 'Uso',
    render: (promotion) =>
      promotion.en_uso ? (
        <span title={IN_USE_REASON}>
          <Badge tone="info">En uso</Badge>
        </span>
      ) : null,
  },
]

export function PromotionsListPage() {
  const { state, promotions, updateSearch, updateStatusFilter, remove } = usePromotionsList()

  return (
    <>
      <PageHeader
        title="Promociones"
        subtitle="Descuentos vigentes sobre productos y combinaciones de la carta."
        actions={
          <>
            <Button variant="primary" onClick={() => navigate('/promociones/nueva')}>
              Nueva promoción
            </Button>
          </>
        }
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {state.error}
        </Alert>
      )}

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar promoción..."
            value={state.search}
            onChange={(event) => updateSearch(event.target.value)}
          />
          <Select
            value={state.statusFilter}
            onChange={(event) => updateStatusFilter(event.target.value as PromotionStatusFilter)}
          >
            <option value="activas">Solo activas</option>
            <option value="todas">Incluir dadas de baja</option>
            <option value="bajas">Solo dadas de baja</option>
          </Select>
        </Toolbar>

        {state.loading ? (
          <p className="muted">Cargando promociones...</p>
        ) : (
          <DataTable
            columns={columns}
            rows={promotions}
            empty={
              <EmptyState title="Sin promociones">
                Todavía no hay promociones cargadas.
              </EmptyState>
            }
            actions={(promotion) => (
              <div className="row">
                {!promotion.en_uso && (
                  <Button
                    size="sm"
                    onClick={() => navigate(`/promociones/${promotion.id}/editar`)}
                    disabled={state.deletingId === promotion.id}
                  >
                    Editar
                  </Button>
                )}
                {!promotion.dado_de_baja && (
                  <DeleteButton
                    title="Dar de baja promoción"
                    onConfirm={() => {
                      void remove(promotion.id)
                    }}
                  >
                    ¿Querés dar de baja <strong>{promotion.nombre}</strong>? Dejará de aplicarse a
                    nuevas facturas.
                  </DeleteButton>
                )}
              </div>
            )}
          />
        )}
      </Card>
    </>
  )
}
