/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Tabla de combos (pestaña Combos de Productos)
 * La lógica vive en `useCombosList`; el componente solo renderiza.
 */
import { Alert, Button, DataTable, DeleteButton, EmptyState } from '../../ui/ui'
import { PencilIcon } from '../../ui/PencilIcon'
import { TrashIcon } from '../../ui/TrashIcon'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import type { ComboListado } from '../products/api'
import { useCombosList } from './useCombosList'

const formatCurrency = (value: string) => `$ ${Number(value).toLocaleString('es-AR')}`

export function CombosTable({ search, sectionId }: { search: string; sectionId: string }) {
  const { state, combos, remove, describe } = useCombosList(search, sectionId)

  const columns: DataTableColumn<ComboListado>[] = [
    {
      key: 'nombre',
      header: 'Nombre',
      render: (combo) => <span className="cell-main">{combo.nombre}</span>,
    },
    {
      key: 'componentes',
      header: 'Componentes',
      render: (combo) => describe(combo),
    },
    {
      key: 'precio',
      header: 'Precio',
      num: true,
      render: (combo) => formatCurrency(combo.precio),
    },
    {
      key: 'vigencia',
      header: 'Vigencia',
      render: (combo) => `${combo.fecha_desde} → ${combo.fecha_hasta}`,
    },
  ]

  return (
    <>
      {state.error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {state.error}
        </Alert>
      )}

      {state.loading ? (
        <p className="muted">Cargando combos...</p>
      ) : (
        <DataTable
          columns={columns}
          rows={combos}
          empty={<EmptyState title="Sin combos">Todavía no hay combos cargados.</EmptyState>}
          actions={(combo) => (
            <div className="row row-icons">
              <Button
                size="sm"
                className="btn-icon"
                title="Editar"
                aria-label={`Editar ${combo.nombre}`}
                onClick={() => navigate(`/productos/combos/${combo.id}/editar`)}
                disabled={state.deletingId === combo.id}
              >
                <PencilIcon />
              </Button>
              <DeleteButton
                label="Dar de baja"
                icon={<TrashIcon />}
                title="Dar de baja combo"
                onConfirm={() => {
                  void remove(combo.id)
                }}
              >
                ¿Querés dar de baja <strong>{combo.nombre}</strong>? Dejará de ofrecerse en la
                carta.
              </DeleteButton>
            </div>
          )}
        />
      )}
    </>
  )
}
