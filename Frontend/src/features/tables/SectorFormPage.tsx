/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Alta y edición de sectores
 */
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Alert, Button, Card, Field, Input, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { createSector, getSector, updateSector } from './api'
import type { SectorPayload, SectorRecord } from './types'

export function SectorFormPage({ id }: { id?: string }) {
  const isEditing = Boolean(id)
  const sectorId = Number(id)
  const invalidId = isEditing && (!Number.isSafeInteger(sectorId) || sectorId <= 0)
  const [form, setForm] = useState<{
    id?: string
    nombre: string
    piso: string
    aptoFumadores: boolean
  }>({ nombre: '', piso: '', aptoFumadores: false })
  const [sector, setSector] = useState<SectorRecord | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<{ id?: string; message: string } | null>(null)
  const currentForm =
    form.id === id ? form : { id, nombre: '', piso: '', aptoFumadores: false }
  const currentSector = isEditing && sector?.id === sectorId ? sector : null
  const visibleError = invalidId
    ? 'El identificador del sector no es válido.'
    : error && error.id === id
      ? error.message
      : null
  const loading = isEditing && !invalidId && !currentSector && !visibleError

  useEffect(() => {
    if (!id || invalidId) return

    let cancelled = false
    getSector(sectorId)
      .then((result) => {
        if (cancelled) return
        setSector(result)
        setForm({
          id,
          nombre: result.nombre,
          piso: result.piso,
          aptoFumadores: result.apto_fumadores,
        })
      })
      .catch((cause: unknown) => {
        if (!cancelled) {
          setError({
            id,
            message: cause instanceof Error ? cause.message : 'No se pudo cargar el sector.',
          })
        }
      })

    return () => {
      cancelled = true
    }
  }, [id, invalidId, sectorId])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const payload: SectorPayload = {
      nombre: currentForm.nombre.normalize('NFC').trim(),
      piso: currentForm.piso.normalize('NFC').trim(),
      apto_fumadores: currentForm.aptoFumadores,
    }

    if (!payload.nombre) {
      setError({ id, message: 'El nombre no puede estar vacío.' })
      return
    }
    if (payload.nombre.length > 50) {
      setError({ id, message: 'El nombre no debe superar los 50 caracteres.' })
      return
    }
    if (payload.piso.length > 30) {
      setError({ id, message: 'El piso no debe superar los 30 caracteres.' })
      return
    }
    if (isEditing && !currentSector) return

    setSaving(true)
    try {
      if (currentSector) {
        await updateSector(currentSector.id, payload)
      } else {
        await createSector(payload)
      }
      navigate('/mesas')
    } catch (cause) {
      setError({
        id,
        message: cause instanceof Error ? cause.message : 'No se pudo guardar el sector.',
      })
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar sector' : 'Nuevo sector'}
        subtitle="Definí el nombre, el piso y la condición del sector."
      />

      <form onSubmit={handleSubmit}>
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/mesas')}>Cancelar</Button>
              <Button
                variant="primary"
                type="submit"
                disabled={loading || saving || (isEditing && !currentSector)}
              >
                {saving ? 'Guardando...' : 'Guardar sector'}
              </Button>
            </>
          }
        >
          {visibleError && <Alert tone="danger">{visibleError}</Alert>}
          {loading ? (
            <p className="muted">Cargando sector...</p>
          ) : isEditing && !currentSector ? (
            <p className="muted">No se pudo cargar el sector para editarlo.</p>
          ) : (
            <div className="form-grid">
              <Field label="Nombre" required>
                <Input
                  value={currentForm.nombre}
                  onChange={(event) => setForm({ ...currentForm, nombre: event.target.value })}
                  placeholder="Nombre del sector"
                  maxLength={50}
                  required
                />
              </Field>

              <Field label="Piso" required>
                <Input
                  value={currentForm.piso}
                  onChange={(event) => setForm({ ...currentForm, piso: event.target.value })}
                  placeholder="Ej.: Planta baja"
                  maxLength={30}
                  required
                />
              </Field>

              <Field label="Condición">
                <Select
                  value={currentForm.aptoFumadores ? 'true' : 'false'}
                  onChange={(event) =>
                    setForm({ ...currentForm, aptoFumadores: event.target.value === 'true' })
                  }
                >
                  <option value="false">No fumadores</option>
                  <option value="true">Apto fumadores</option>
                </Select>
              </Field>
            </div>
          )}
        </Card>
      </form>
    </>
  )
}
