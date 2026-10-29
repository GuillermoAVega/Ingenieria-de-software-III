/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Alta y edición de mesas
 */
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Alert, Button, Card, Field, Input, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { createTable, getTable, listSectors, updateTable } from './api'
import type { SectorRecord, TablePayload, TableRecord } from './types'

export function TableFormPage({ id }: { id?: string }) {
  const isEditing = Boolean(id)
  const tableId = Number(id)
  const invalidId = isEditing && (!Number.isSafeInteger(tableId) || tableId <= 0)
  const [sectors, setSectors] = useState<SectorRecord[]>([])
  const [form, setForm] = useState<{
    id?: string
    sectorId: string
    capacity: string
    available: boolean
  }>({ sectorId: '', capacity: '2', available: true })
  const [table, setTable] = useState<TableRecord | null>(null)
  const [loadingData, setLoadingData] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<{ id?: string; message: string } | null>(null)
  const currentForm =
    form.id === id ? form : { id, sectorId: '', capacity: '2', available: true }
  const currentTable = isEditing && table?.id === tableId ? table : null
  const visibleError = invalidId
    ? 'El identificador de la mesa no es válido.'
    : error && error.id === id
      ? error.message
      : null
  const loading = !invalidId && loadingData

  useEffect(() => {
    if (invalidId) return

    let cancelled = false
    const requests: [Promise<SectorRecord[]>, Promise<TableRecord | null>] = [
      listSectors(),
      id ? getTable(tableId) : Promise.resolve(null),
    ]

    Promise.all(requests)
      .then(([sectorResults, tableResult]) => {
        if (cancelled) return
        const activeSectors = sectorResults.filter((sector) => sector.estado)
        setSectors(activeSectors)
        if (tableResult) {
          setTable(tableResult)
          setForm({
            id,
            sectorId: String(tableResult.sector_id),
            capacity: String(tableResult.capacidad),
            available: tableResult.disponible,
          })
        } else {
          setForm((current) => ({ ...current, id, sectorId: activeSectors[0] ? String(activeSectors[0].id) : '' }))
        }
      })
      .catch((cause: unknown) => {
        if (!cancelled) {
          setError({
            id,
            message: cause instanceof Error ? cause.message : 'No se pudieron cargar los datos de la mesa.',
          })
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingData(false)
      })

    return () => {
      cancelled = true
    }
  }, [id, invalidId, tableId])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const sectorId = Number(currentForm.sectorId)
    const capacity = Number(currentForm.capacity)
    if (!Number.isSafeInteger(sectorId) || sectorId <= 0) {
      setError({ id, message: 'Seleccioná un sector activo.' })
      return
    }
    if (!Number.isSafeInteger(capacity) || capacity <= 0) {
      setError({ id, message: 'La capacidad debe ser un entero positivo.' })
      return
    }
    if (isEditing && !currentTable) return

    const payload: TablePayload = {
      capacidad: capacity,
      disponible: currentForm.available,
      sector_id: sectorId,
    }

    setSaving(true)
    try {
      if (currentTable) {
        await updateTable(currentTable.id, payload)
      } else {
        await createTable(payload)
      }
      navigate('/mesas')
    } catch (cause) {
      setError({
        id,
        message: cause instanceof Error ? cause.message : 'No se pudo guardar la mesa.',
      })
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar mesa' : 'Nueva mesa'}
        subtitle="Asigná la mesa a un sector y definí su capacidad y disponibilidad."
      />

      <form onSubmit={handleSubmit}>
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/mesas')}>Cancelar</Button>
              <Button
                variant="primary"
                type="submit"
                disabled={
                  loading ||
                  saving ||
                  sectors.length === 0 ||
                  (isEditing && !currentTable)
                }
              >
                {saving ? 'Guardando...' : 'Guardar mesa'}
              </Button>
            </>
          }
        >
          {visibleError && <Alert tone="danger">{visibleError}</Alert>}
          {loading ? (
            <p className="muted">Cargando datos de la mesa...</p>
          ) : isEditing && !currentTable ? (
            <p className="muted">No se pudo cargar la mesa para editarla.</p>
          ) : sectors.length === 0 ? (
            <p className="muted">No hay sectores activos para asignar la mesa.</p>
          ) : (
            <div className="form-grid">
              <Field label="Sector" required>
                <Select
                  value={currentForm.sectorId}
                  onChange={(event) => setForm({ ...currentForm, sectorId: event.target.value })}
                  required
                >
                  <option value="">Seleccioná un sector</option>
                  {sectors.map((sector) => (
                    <option key={sector.id} value={sector.id}>
                      {sector.nombre}
                    </option>
                  ))}
                </Select>
              </Field>

              <Field label="Personas" required>
                <Input
                  type="number"
                  value={currentForm.capacity}
                  onChange={(event) => setForm({ ...currentForm, capacity: event.target.value })}
                  min={1}
                  step={1}
                  required
                />
              </Field>

              <Field label="Estado">
                <Select
                  value={currentForm.available ? 'disponible' : 'ocupada'}
                  onChange={(event) =>
                    setForm({ ...currentForm, available: event.target.value === 'disponible' })
                  }
                >
                  <option value="disponible">Disponible</option>
                  <option value="ocupada">Ocupada</option>
                </Select>
              </Field>
            </div>
          )}
        </Card>
      </form>
    </>
  )
}
