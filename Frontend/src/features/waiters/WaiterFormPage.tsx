import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Alert, Button, Card, Field, Input, PageHeader } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { createWaiter, getWaiter, updateWaiter } from './api'
import type { Waiter } from './types'

export function WaiterFormPage({ id }: { id?: string }) {
  const isEditing = Boolean(id)
  const invalidId = isEditing && (!Number.isSafeInteger(Number(id)) || Number(id) <= 0)
  const [form, setForm] = useState<{ id?: string; name: string; employeeNumber: string }>({
    name: '',
    employeeNumber: '',
  })
  const [waiter, setWaiter] = useState<Waiter | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<{ id?: string; message: string } | null>(null)
  const currentForm = form.id === id ? form : { id, name: '', employeeNumber: '' }
  const currentWaiter = isEditing && waiter?.id === Number(id) ? waiter : null
  const visibleError = invalidId
    ? 'El identificador del mozo no es válido.'
    : error && error.id === id
      ? error.message
      : null
  const loading = isEditing && !invalidId && !currentWaiter && !visibleError

  useEffect(() => {
    if (!id || invalidId) return

    let cancelled = false
    const waiterId = Number(id)
    getWaiter(waiterId)
      .then((result) => {
        if (cancelled) return
        setWaiter(result)
        setForm({
          id,
          name: result.name,
          employeeNumber: String(result.nro_legajo),
        })
      })
      .catch((cause: unknown) => {
        if (!cancelled) {
          setError({
            id,
            message: cause instanceof Error ? cause.message : 'No se pudo cargar el mozo.',
          })
        }
      })

    return () => {
      cancelled = true
    }
  }, [id, invalidId])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const parsedEmployeeNumber = Number(currentForm.employeeNumber)
    const normalizedName = currentForm.name.normalize('NFC').trim()
    if (!normalizedName) {
      setError({ id, message: 'El nombre no puede estar vacío.' })
      return
    }
    if (!Number.isSafeInteger(parsedEmployeeNumber) || parsedEmployeeNumber <= 0) {
      setError({ id, message: 'El número de legajo debe ser un entero positivo.' })
      return
    }
    if (isEditing && !currentWaiter) return

    setSaving(true)
    try {
      const payload = { nombre: normalizedName, nro_legajo: parsedEmployeeNumber }
      if (currentWaiter) {
        await updateWaiter(currentWaiter.id, payload)
      } else {
        await createWaiter(payload)
      }
      navigate('/mozos')
    } catch (cause) {
      setError({
        id,
        message: cause instanceof Error ? cause.message : 'No se pudo guardar el mozo.',
      })
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar mozo' : 'Nuevo mozo'}
        subtitle="Completá el nombre y el número de legajo del mozo."
      />

      <form onSubmit={handleSubmit}>
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/mozos')}>Cancelar</Button>
              <Button
                variant="primary"
                type="submit"
                disabled={loading || saving || (isEditing && !currentWaiter)}
              >
                {saving ? 'Guardando...' : 'Guardar mozo'}
              </Button>
            </>
          }
        >
          {visibleError && <Alert tone="danger">{visibleError}</Alert>}
          {loading ? (
            <p className="muted">Cargando mozo...</p>
          ) : isEditing && !waiter ? (
            <p className="muted">No se pudo cargar el mozo para editarlo.</p>
          ) : (
            <div className="form-grid">
              <Field label="Nombre" required>
                <Input
                  value={currentForm.name}
                  onChange={(event) =>
                    setForm({ id, name: event.target.value, employeeNumber: currentForm.employeeNumber })
                  }
                  placeholder="Nombre y apellido"
                  maxLength={50}
                  required
                />
              </Field>

              <Field label="Número de legajo" required>
                <Input
                  type="number"
                  value={currentForm.employeeNumber}
                  onChange={(event) =>
                    setForm({ id, name: currentForm.name, employeeNumber: event.target.value })
                  }
                  placeholder="Ej.: 1001"
                  min={1}
                  step={1}
                  required
                />
              </Field>
            </div>
          )}
        </Card>
      </form>
    </>
  )
}
