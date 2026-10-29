/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Alta y edición de clientes
 * Alta y edición conectadas a la API de clientes.
 */
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Alert, Button, Card, Field, Input, PageHeader } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { createCustomer, getCustomer, updateCustomer } from './api'

export function CustomerFormPage({ id }: { id?: string }) {
  const isEditing = Boolean(id)
  const [dni, setDni] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(isEditing)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return

    let cancelled = false
    getCustomer(id)
      .then((customer) => {
        if (cancelled) return
        setDni(customer.dni)
        setFirstName(customer.nombre)
        setLastName(customer.apellido)
        setPhone(customer.telefono)
      })
      .catch((cause: unknown) => {
        if (!cancelled) setError(cause instanceof Error ? cause.message : 'No se pudo cargar el cliente.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [id])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSaving(true)

    const customer = {
      dni: dni.trim(),
      nombre: firstName.normalize('NFC').trim(),
      apellido: lastName.normalize('NFC').trim(),
      telefono: phone.trim(),
    }

    try {
      if (id) {
        await updateCustomer(id, customer)
      } else {
        await createCustomer(customer)
      }
      navigate('/clientes')
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo guardar el cliente.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar cliente' : 'Nuevo cliente'}
        subtitle="Completá los datos del cliente para futuras reservas y comandas."
      />

      <form onSubmit={handleSubmit}>
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/clientes')}>Cancelar</Button>
              <Button variant="primary" type="submit" disabled={loading || saving}>
                {saving ? 'Guardando...' : 'Guardar cliente'}
              </Button>
            </>
          }
        >
          {error && <Alert tone="danger">{error}</Alert>}
          {loading ? (
            <p className="muted">Cargando cliente...</p>
          ) : (
          <div className="form-grid">
            <Field label="DNI" required>
              <Input value={dni} onChange={(event) => setDni(event.target.value)} required />
            </Field>

            <Field label="Nombre" required>
              <Input value={firstName} onChange={(event) => setFirstName(event.target.value)} placeholder="Nombre" required />
            </Field>

            <Field label="Apellido" required>
              <Input value={lastName} onChange={(event) => setLastName(event.target.value)} placeholder="Apellido" required />
            </Field>

            <Field label="Teléfono" required>
              <Input
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                placeholder="2804550000"
                pattern="[0-9-]+"
                title="Ingresá solo números y guiones."
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
