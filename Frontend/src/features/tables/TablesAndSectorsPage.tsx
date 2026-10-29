/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Mapa de mesas y sectores
 */
import { useEffect, useState } from 'react'
import { Alert, Badge, Button, Card, DeleteButton, PageHeader } from '../../ui/ui'
import type { BadgeTone } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { listAttentions, listWaiters } from '../waiters/api'
import type { Attention, Waiter } from '../waiters/types'
import {
  deactivateSector,
  deactivateTable,
  listSectors,
  listTables,
  reactivateTable,
  reactivateSector,
} from './api'
import type { SectorRecord, TableRecord } from './types'

export function TablesAndSectorsPage() {
  const [sectors, setSectors] = useState<SectorRecord[]>([])
  const [tables, setTables] = useState<TableRecord[]>([])
  const [waiters, setWaiters] = useState<Waiter[]>([])
  const [attentions, setAttentions] = useState<Attention[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([listSectors(), listTables(true), listWaiters(), listAttentions()])
      .then(([sectorResults, tableResults, waiterResults, attentionResults]) => {
        if (cancelled) return
        setSectors(sectorResults)
        setTables(tableResults)
        setWaiters(waiterResults)
        setAttentions(attentionResults)
      })
      .catch((cause: unknown) => {
        if (!cancelled) {
          setError(
            cause instanceof Error
              ? cause.message
              : 'No se pudieron cargar los sectores y las mesas.',
          )
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const orderedSectors = [
    ...sectors.filter((sector) => sector.estado),
    ...sectors.filter((sector) => !sector.estado),
  ]
  const waiterNames = new Map(waiters.map((waiter) => [waiter.id, waiter.name]))

  async function handleDeactivateSector(sector: SectorRecord) {
    setError(null)
    try {
      await deactivateSector(sector.id)
      setSectors((current) =>
        current.map((candidate) =>
          candidate.id === sector.id ? { ...candidate, estado: false } : candidate,
        ),
      )
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo dar de baja el sector.')
    }
  }

  async function handleReactivateSector(sector: SectorRecord) {
    setError(null)
    try {
      await reactivateSector(sector.id)
      setSectors((current) =>
        current.map((candidate) =>
          candidate.id === sector.id ? { ...candidate, estado: true } : candidate,
        ),
      )
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo reactivar el sector.')
    }
  }

  async function handleDeactivateTable(table: TableRecord) {
    setError(null)
    try {
      await deactivateTable(table.id)
      setTables((current) =>
        current.map((candidate) =>
          candidate.id === table.id ? { ...candidate, estado: false } : candidate,
        ),
      )
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo dar de baja la mesa.')
    }
  }

  async function handleReactivateTable(table: TableRecord) {
    setError(null)
    try {
      await reactivateTable(table.id)
      setTables((current) =>
        current.map((candidate) =>
          candidate.id === table.id ? { ...candidate, estado: true } : candidate,
        ),
      )
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo dar de alta la mesa.')
    }
  }

  function renderSector(sector: SectorRecord) {
    const sectorTables = tables.filter((table) => table.sector_id === sector.id)
    const currentWaiterNames = [
      ...new Set(
        attentions
          .filter(
            (attention) =>
              attention.estado &&
              attention.fecha_hasta === null &&
              attention.sector_id === sector.id,
          )
          .map((attention) => waiterNames.get(attention.mozo_id))
          .filter((name): name is string => Boolean(name)),
      ),
    ]

    return (
      <Card
        key={sector.id}
        title={sector.nombre}
        subtitle={`${sector.piso} · ${sector.apto_fumadores ? 'Apto fumadores' : 'No fumadores'} · Mozos a cargo: ${currentWaiterNames.join(', ') || 'Sin mozos asignados'}`}
        actions={
          <div className="row">
            {sector.estado ? (
              <>
                <Button size="sm" onClick={() => navigate(`/mesas/sectores/${sector.id}/editar`)}>
                  Editar sector
                </Button>
                <DeleteButton
                  label="Dar de baja"
                  title="Dar de baja sector"
                  confirmLabel="Dar de baja"
                  onConfirm={() => void handleDeactivateSector(sector)}
                >
                  ¿Querés dar de baja <strong>{sector.nombre}</strong>?
                </DeleteButton>
              </>
            ) : (
              <>
                <Badge tone="neutral">Inactivo</Badge>
                <Button size="sm" onClick={() => void handleReactivateSector(sector)}>
                  Reactivar
                </Button>
              </>
            )}
          </div>
        }
      >
        {sectorTables.length > 0 ? (
          <div className="mesa-grid">
            {sectorTables.map((table) => {
              const status = table.disponible ? 'Disponible' : 'Ocupada'
              const tone: BadgeTone = table.disponible ? 'success' : 'info'

              return (
                <div key={table.id} className="stack">
                  {table.estado ? (
                    <button
                      type="button"
                      className={`mesa${table.disponible ? '' : ' is-busy'}`}
                      onClick={() => navigate(`/mesas/${table.id}/editar`)}
                    >
                      <span className="mesa-num">Mesa {table.id}</span>
                      <span className="mesa-meta">{table.capacidad} personas</span>
                      <Badge tone={tone}>{status}</Badge>
                    </button>
                  ) : (
                    <div className="mesa">
                      <span className="mesa-num">Mesa {table.id}</span>
                      <span className="mesa-meta">{table.capacidad} personas</span>
                      <Badge tone="neutral">Inactiva</Badge>
                    </div>
                  )}
                  {table.estado && (
                    <div className="row">
                      <DeleteButton
                        label="Dar de baja"
                        title="Dar de baja mesa"
                        confirmLabel="Dar de baja"
                        onConfirm={() => void handleDeactivateTable(table)}
                      >
                        ¿Querés dar de baja la <strong>Mesa {table.id}</strong>?
                      </DeleteButton>
                    </div>
                  )}
                  {!table.estado && (
                    <div className="row">
                      <Button size="sm" onClick={() => void handleReactivateTable(table)}>
                        Dar de alta
                      </Button>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        ) : (
          <p className="muted text-sm">
            {sector.estado ? 'No hay mesas activas en este sector.' : 'No hay mesas activas.'}
          </p>
        )}
      </Card>
    )
  }

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
      </div>

      {error && <Alert tone="danger">{error}</Alert>}
      {loading ? (
        <p className="muted">Cargando sectores y mesas...</p>
      ) : orderedSectors.length > 0 ? (
        orderedSectors.map(renderSector)
      ) : (
        <p className="muted">No hay sectores para mostrar.</p>
      )}
    </>
  )
}
