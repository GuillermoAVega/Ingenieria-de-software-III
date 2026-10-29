import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import {
  Alert,
  Button,
  Card,
  DataTable,
  Field,
  Input,
  PageHeader,
  Select,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { listSectors } from '../tables/api'
import { createAttention, finishAttention, getWaiter, listAttentions } from './api'
import type { Attention, Waiter } from './types'
import type { SectorRecord } from '../tables/types'

type AttentionRow = Attention & { sector: string }

function localDate(): string {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function WaiterAttentionsPage({ id }: { id: string }) {
  const today = localDate()
  const invalidId = !Number.isSafeInteger(Number(id)) || Number(id) <= 0
  const waiterId = Number(id)
  const [waiter, setWaiter] = useState<Waiter | null>(null)
  const [attentions, setAttentions] = useState<Attention[]>([])
  const [sectors, setSectors] = useState<SectorRecord[]>([])
  const [sectorId, setSectorId] = useState('')
  const [startDate, setStartDate] = useState(localDate)
  const [finishDates, setFinishDates] = useState<Record<number, string>>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [finalizingId, setFinalizingId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (invalidId) return

    let cancelled = false
    Promise.all([getWaiter(waiterId), listAttentions(waiterId), listSectors()])
      .then(([waiterRecord, attentionRecords, sectorRecords]) => {
        if (cancelled) return
        setWaiter(waiterRecord)
        setAttentions(attentionRecords)
        setSectors(sectorRecords)
        setError(null)
      })
      .catch((cause: unknown) => {
        if (!cancelled) {
          setError(cause instanceof Error ? cause.message : 'No se pudieron cargar las atenciones.')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [invalidId, waiterId])

  const sectorsById = useMemo(() => new Map(sectors.map((sector) => [sector.id, sector.nombre])), [sectors])
  const activeSectors = useMemo(() => sectors.filter((sector) => sector.estado), [sectors])
  const activeAttentions = useMemo(
    () =>
      attentions
        .filter((attention) => attention.estado && attention.fecha_hasta === null)
        .map((attention) => ({
          ...attention,
          sector: sectorsById.get(attention.sector_id) ?? `Sector #${attention.sector_id}`,
        }))
        .sort((left, right) => left.fecha_desde.localeCompare(right.fecha_desde)),
    [attentions, sectorsById],
  )
  const assignedSectorIds = useMemo(
    () => new Set(activeAttentions.map((attention) => attention.sector_id)),
    [activeAttentions],
  )
  const availableSectors = useMemo(
    () => activeSectors.filter((sector) => !assignedSectorIds.has(sector.id)),
    [activeSectors, assignedSectorIds],
  )
  const historyAttentions = useMemo(
    () =>
      attentions
        .filter((attention) => attention.estado && attention.fecha_hasta !== null)
        .map((attention) => ({
          ...attention,
          sector: sectorsById.get(attention.sector_id) ?? `Sector #${attention.sector_id}`,
        }))
        .sort((left, right) => (right.fecha_hasta ?? '').localeCompare(left.fecha_hasta ?? '')),
    [attentions, sectorsById],
  )

  const visibleError = invalidId ? 'El identificador del mozo no es válido.' : error

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    if (!waiter || !sectorId) return
    if (startDate > today) {
      setError('La fecha desde no puede ser posterior a hoy.')
      return
    }

    setSaving(true)
    try {
      const created = await createAttention({
        fecha_desde: startDate,
        mozo_id: waiter.id,
        sector_id: Number(sectorId),
      })
      setAttentions((current) => [...current, created])
      setSectorId('')
      setStartDate(localDate())
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo crear la atención.')
    } finally {
      setSaving(false)
    }
  }

  async function handleFinish(attention: AttentionRow) {
    const fechaHasta = finishDates[attention.id] ?? localDate()
    setError(null)
    if (fechaHasta > today) {
      setError('La fecha hasta no puede ser posterior a hoy.')
      return
    }
    if (fechaHasta < attention.fecha_desde) {
      setError('La fecha hasta debe ser igual o posterior a la fecha desde.')
      return
    }
    setFinalizingId(attention.id)
    try {
      const finished = await finishAttention(attention.id, fechaHasta)
      setAttentions((current) =>
        current.map((candidate) => (candidate.id === finished.id ? finished : candidate)),
      )
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo finalizar la atención.')
    } finally {
      setFinalizingId(null)
    }
  }

  const currentColumns: DataTableColumn<AttentionRow>[] = [
    { key: 'sector', header: 'Sector' },
    { key: 'fecha_desde', header: 'Desde' },
  ]
  const historyColumns: DataTableColumn<AttentionRow>[] = [
    { key: 'sector', header: 'Sector' },
    { key: 'fecha_desde', header: 'Desde' },
    { key: 'fecha_hasta', header: 'Hasta' },
  ]

  return (
    <>
      <PageHeader
        title={waiter ? `Atenciones de ${waiter.name}` : 'Atenciones del mozo'}
        subtitle="Asigná sectores, finalizá atenciones abiertas y consultá el historial."
        actions={<Button onClick={() => navigate('/mozos')}>Volver a mozos</Button>}
      />

      {visibleError && <Alert tone="danger">{visibleError}</Alert>}

      {invalidId ? (
        <Card><p className="muted">No se puede cargar el mozo solicitado.</p></Card>
      ) : loading ? (
        <Card><p className="muted">Cargando atenciones...</p></Card>
      ) : waiter ? (
        <>
          <Card
            title="Nueva atención"
            subtitle="Elegí el sector y la fecha desde la que comienza. Un mozo puede tener varios sectores a cargo."
          >
            {!waiter.estado && (
              <Alert tone="warning">El mozo está inactivo y no puede recibir nuevas atenciones.</Alert>
            )}
            {waiter.estado && activeSectors.length === 0 && (
              <Alert tone="warning">No hay sectores activos para asignar.</Alert>
            )}
            {waiter.estado && activeSectors.length > 0 && availableSectors.length === 0 && (
              <Alert tone="warning">
                El mozo ya tiene una atención activa en todos los sectores disponibles.
              </Alert>
            )}
            <form onSubmit={handleCreate}>
              <div className="form-grid">
                <Field label="Sector" required>
                  <Select
                    value={sectorId}
                    onChange={(event) => setSectorId(event.target.value)}
                    required
                    disabled={!waiter.estado || availableSectors.length === 0}
                  >
                    <option value="">Seleccionar sector...</option>
                    {availableSectors.map((sector) => (
                      <option key={sector.id} value={sector.id}>{sector.nombre}</option>
                    ))}
                  </Select>
                </Field>
                <Field label="Fecha desde" required>
                  <Input
                    type="date"
                    value={startDate}
                    max={today}
                    onChange={(event) => setStartDate(event.target.value)}
                    required
                    disabled={!waiter.estado}
                  />
                </Field>
              </div>
              <div className="row">
                <Button
                  type="submit"
                  variant="primary"
                  disabled={!waiter.estado || availableSectors.length === 0 || !sectorId || saving}
                >
                  {saving ? 'Guardando...' : 'Agregar atención'}
                </Button>
              </div>
            </form>
          </Card>

          <Card title="Atenciones actuales" subtitle="Ingresá la fecha hasta para finalizar una atención.">
            <DataTable
              columns={currentColumns}
              rows={activeAttentions}
              rowKey="id"
              actions={(attention) => {
                const finishDate = finishDates[attention.id] ?? localDate()
                return (
                  <div className="row">
                    <Input
                      type="date"
                      aria-label={`Fecha hasta de ${attention.sector}`}
                      min={attention.fecha_desde}
                      max={today}
                      value={finishDate}
                      required
                      onChange={(event) =>
                        setFinishDates((current) => ({ ...current, [attention.id]: event.target.value }))
                      }
                    />
                    <Button
                      size="sm"
                      onClick={() => void handleFinish(attention)}
                      disabled={
                        finalizingId !== null ||
                        !finishDate ||
                        finishDate < attention.fecha_desde ||
                        finishDate > today
                      }
                    >
                      {finalizingId === attention.id ? 'Finalizando...' : 'Finalizar'}
                    </Button>
                  </div>
                )
              }}
              empty={
                <div className="empty">
                  <span className="empty-title">No hay atenciones abiertas</span>
                </div>
              }
            />
          </Card>

          <Card title="Historial de atenciones" subtitle="Las atenciones finalizadas se muestran solo para consulta.">
            <DataTable
              columns={historyColumns}
              rows={historyAttentions}
              rowKey="id"
              empty={
                <div className="empty">
                  <span className="empty-title">Todavía no hay atenciones finalizadas</span>
                </div>
              }
            />
          </Card>
        </>
      ) : (
        <Card><p className="muted">No se encontró el mozo solicitado.</p></Card>
      )}
    </>
  )
}
