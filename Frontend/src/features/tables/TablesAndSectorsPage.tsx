/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Mapa de mesas y sectores
 * COMPLETAR:
 * 1. Reemplazar DEMO_SECTORS y DEMO_TABLES por la llamada a la API.
 * 2. Implementar acciones rápidas sobre cada mesa (estado, comanda, reserva).
 * 3. Conectar la edición de sectores y mesas con la API.
 */
import { Badge, Button, Card, DeleteButton, PageHeader } from '../../ui/ui'
import type { BadgeTone } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_SECTORS, DEMO_TABLES } from './demo'
import type { RestaurantTable, TableStatus } from './types'

const statusLabel: Record<TableStatus, string> = {
  disponible: 'Disponible',
  ocupada: 'Ocupada',
  reservada: 'Reservada',
}

const statusTone: Record<TableStatus, BadgeTone> = {
  disponible: 'success',
  ocupada: 'info',
  reservada: 'warning',
}

const tableClassName = (table: RestaurantTable) =>
  ['mesa', table.status === 'ocupada' ? 'is-busy' : '', table.status === 'reservada' ? 'is-reserved' : '']
    .filter(Boolean)
    .join(' ')

export function TablesAndSectorsPage() {
  return (
    <>
      <PageHeader
        title="Mesas y sectores"
        subtitle="Estado del salón en tiempo real, agrupado por sector."
        actions={
          <>
            <Button onClick={() => navigate('/mesas/sectores/nuevo')}>Nuevo sector</Button>
            <Button variant="primary" onClick={() => navigate('/mesas/nueva')}>
              Nueva mesa
            </Button>
          </>
        }
      />

      <div className="row">
        <span className="muted text-sm">Referencias:</span>
        <Badge tone="success">Disponible</Badge>
        <Badge tone="info">Ocupada</Badge>
        <Badge tone="warning">Reservada</Badge>
      </div>

      {DEMO_SECTORS.map((sector) => {
        const tables = DEMO_TABLES.filter((table) => table.sectorId === sector.id)

        return (
          <Card
            key={sector.id}
            title={sector.name}
            subtitle={`${sector.floor} · ${sector.condition}`}
            actions={
              <div className="row">
                <Button size="sm" onClick={() => navigate(`/mesas/sectores/${sector.id}/editar`)}>
                  Editar sector
                </Button>
                <DeleteButton
                  label="Eliminar sector"
                  title="Eliminar sector"
                  onConfirm={() => {
                    // TODO(equipo-salon): eliminar el sector en la API.
                  }}
                >
                  ¿Querés eliminar <strong>{sector.name}</strong>?
                </DeleteButton>
              </div>
            }
          >
            <div className="mesa-grid">
              {tables.map((table) => (
                <button
                  key={table.id}
                  type="button"
                  className={tableClassName(table)}
                  onClick={() => navigate(`/mesas/${table.id}/editar`)}
                >
                  <span className="mesa-num">{table.number}</span>
                  <span className="mesa-meta">{table.seats} personas</span>
                  <Badge tone={statusTone[table.status]}>{statusLabel[table.status]}</Badge>
                </button>
              ))}
            </div>
          </Card>
        )
      })}
    </>
  )
}
