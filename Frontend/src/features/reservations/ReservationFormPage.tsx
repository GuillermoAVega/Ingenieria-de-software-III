import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Alert, Button, Card, Field, Input, PageHeader, Select, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import {
  addReservationDetail,
  addReservationTable,
  createCustomer,
  createReservation,
  getReservation,
  listCustomers,
  listReservationDetails,
  listReservationTables,
  listTables,
  removeReservationDetail,
  removeReservationTable,
  updateReservation,
} from './api'
import type {
  CustomerRecord,
  ReservationDetailPayload,
  ReservationStatus,
  TableRecord,
} from './types'

const newCustomerValue = 'nuevo'
const fakeProducts = [
  { id: 1, name: 'Empanadas surtidas' },
  { id: 2, name: 'Pizza muzzarella' },
  { id: 3, name: 'Ensalada de estación' },
  { id: 4, name: 'Flan casero' },
]

type DetailRow = {
  productId: number
  quantity: number
}

function getErrorMessage(cause: unknown, fallback: string): string {
  return cause instanceof Error ? cause.message : fallback
}

export function ReservationFormPage({ id }: { id?: string }) {
  const isEditing = Boolean(id)
  const [customers, setCustomers] = useState<CustomerRecord[]>([])
  const [tables, setTables] = useState<TableRecord[]>([])
  const [customerSelection, setCustomerSelection] = useState('')
  const [customerDni, setCustomerDni] = useState('')
  const [customerFirstName, setCustomerFirstName] = useState('')
  const [customerLastName, setCustomerLastName] = useState('')
  const [customerPhone, setCustomerPhone] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [guests, setGuests] = useState(2)
  const [status, setStatus] = useState<ReservationStatus>('pendiente')
  const [initialStatus, setInitialStatus] = useState<ReservationStatus | null>(null)
  const [notes, setNotes] = useState('')
  const [selectedTableIds, setSelectedTableIds] = useState<number[]>([])
  const [tableToAdd, setTableToAdd] = useState('')
  const [details, setDetails] = useState<DetailRow[]>([])
  const [productToAdd, setProductToAdd] = useState('')
  const [loading, setLoading] = useState(true)
  const [loadFailed, setLoadFailed] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadFormData() {
      try {
        const [customerRecords, tableRecords] = await Promise.all([listCustomers(), listTables()])
        if (cancelled) return
        setCustomers(customerRecords)
        setTables(tableRecords)

        if (!id) return
        const reservationId = Number(id)
        if (!Number.isInteger(reservationId) || reservationId < 1) {
          throw new Error('El identificador de la reserva no es válido.')
        }

        const [reservation, reservationTables, reservationDetails] = await Promise.all([
          getReservation(reservationId),
          listReservationTables(reservationId),
          listReservationDetails(reservationId),
        ])
        if (cancelled) return
        setCustomerSelection(String(reservation.cliente_id))
        setDate(reservation.fecha)
        setTime(reservation.hora.slice(0, 5))
        setGuests(reservation.cant_comensales)
        setStatus(reservation.estado)
        setInitialStatus(reservation.estado)
        setNotes(reservation.observaciones ?? '')
        const tableIds = reservationTables.map((table) => table.id)
        setSelectedTableIds(tableIds)
        setDetails(reservationDetails.map((detail) => ({
          productId: detail.producto_id,
          quantity: detail.cantidad_producto,
        })))
      } catch (cause) {
        if (!cancelled) {
          setLoadFailed(true)
          setError(getErrorMessage(cause, 'No se pudieron cargar los datos de la reserva.'))
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    void loadFormData()
    return () => {
      cancelled = true
    }
  }, [id])

  const tableById = useMemo(() => new Map(tables.map((table) => [table.id, table])), [tables])
  const availableProducts = useMemo(() => {
    const products = [...fakeProducts]
    for (const detail of details) {
      if (!products.some((product) => product.id === detail.productId)) {
        products.push({ id: detail.productId, name: `Producto #${detail.productId}` })
      }
    }
    return products
  }, [details])
  const canEdit = !isEditing || initialStatus === 'pendiente'

  function addTable() {
    const tableId = Number(tableToAdd)
    if (!tableId || selectedTableIds.includes(tableId)) return
    setSelectedTableIds((current) => [...current, tableId])
    setTableToAdd('')
  }

  function addDetail() {
    const productId = Number(productToAdd)
    if (!productId || details.some((detail) => detail.productId === productId)) return
    setDetails((current) => [...current, { productId, quantity: 1 }])
    setProductToAdd('')
  }

  async function saveTableChanges(reservationId: number) {
    const currentTables = await listReservationTables(reservationId)
    const selectedIds = new Set(selectedTableIds)
    const currentIds = new Set(currentTables.map((table) => table.id))
    for (const tableId of currentIds) {
      if (!selectedIds.has(tableId)) await removeReservationTable(reservationId, tableId)
    }
    for (const tableId of selectedIds) {
      if (!currentIds.has(tableId)) await addReservationTable(reservationId, tableId)
    }
  }

  async function saveDetailChanges(reservationId: number, nextDetails: ReservationDetailPayload[]) {
    const currentDetails = await listReservationDetails(reservationId)
    const originalByProduct = new Map(currentDetails.map((detail) => [detail.producto_id, detail.cantidad_producto]))
    const nextByProduct = new Map(nextDetails.map((detail) => [detail.producto_id, detail.cantidad_producto]))

    for (const detail of currentDetails) {
      const nextQuantity = nextByProduct.get(detail.producto_id)
      if (nextQuantity === undefined || nextQuantity !== detail.cantidad_producto) {
        await removeReservationDetail(reservationId, detail.producto_id)
      }
    }
    for (const detail of nextDetails) {
      const previousQuantity = originalByProduct.get(detail.producto_id)
      if (previousQuantity === undefined || previousQuantity !== detail.cantidad_producto) {
        await addReservationDetail(reservationId, detail)
      }
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!canEdit) return
    setError(null)
    setSaving(true)

    try {
      let customerId = Number(customerSelection)
      if (customerSelection === newCustomerValue) {
        const customer = await createCustomer({
          dni: customerDni.trim(),
          nombre: customerFirstName.normalize('NFC').trim(),
          apellido: customerLastName.normalize('NFC').trim(),
          telefono: customerPhone.trim(),
        })
        customerId = customer.id
        setCustomers((current) => [...current, customer])
        setCustomerSelection(String(customer.id))
      }

      const payload = {
        fecha: date,
        hora: time,
        cant_comensales: guests,
        observaciones: notes.trim() || null,
        cliente_id: customerId,
      }
      const detailsPayload = details.map(({ productId, quantity }) => ({
        producto_id: productId,
        cantidad_producto: quantity,
      }))

      if (id) {
        const reservationId = Number(id)
        await saveTableChanges(reservationId)
        await saveDetailChanges(reservationId, detailsPayload)
        await updateReservation(reservationId, { ...payload, estado: status })
      } else {
        await createReservation({
          ...payload,
          mesa_ids: selectedTableIds,
          detalles: detailsPayload,
        })
      }
      navigate('/reservas')
    } catch (cause) {
      setError(getErrorMessage(cause, 'No se pudo guardar la reserva.'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar reserva' : 'Nueva reserva'}
        subtitle={
          isEditing
            ? 'Actualizá el cliente, los datos, las mesas y el detalle de la reserva.'
            : 'Registrá una reserva y elegí un cliente, una o varias mesas y sus productos.'
        }
      />

      <form onSubmit={handleSubmit}>
        <div className="stack">
          <Card
            title="Datos de la reserva"
            footer={
              <>
                <Button onClick={() => navigate('/reservas')}>Cancelar</Button>
                <Button variant="primary" type="submit" disabled={loading || loadFailed || saving || !canEdit}>
                  {saving ? 'Guardando...' : 'Guardar reserva'}
                </Button>
              </>
            }
          >
            {error && <Alert tone="danger">{error}</Alert>}
            {loading ? (
              <p className="muted">Cargando datos de la reserva...</p>
            ) : (
              <>
                {!canEdit && (
                  <Alert tone="warning">
                    Solo se pueden modificar reservas pendientes. Esta reserva está {status.replace('_', ' ')}.
                  </Alert>
                )}
                {canEdit && <div className="form-grid">
                  <Field label="Cliente" required>
                    <Select
                      value={customerSelection}
                      onChange={(event) => setCustomerSelection(event.target.value)}
                      required
                    >
                      <option value="">Seleccioná un cliente</option>
                      {customers
                        .filter((customer) => customer.estado || String(customer.id) === customerSelection)
                        .map((customer) => (
                        <option key={customer.id} value={customer.id}>
                          {customer.nombre} {customer.apellido} · {customer.telefono}
                        </option>
                      ))}
                      <option value={newCustomerValue}>Crear un cliente nuevo...</option>
                    </Select>
                  </Field>

                  <Field label="Fecha" required>
                    <Input type="date" value={date} onChange={(event) => setDate(event.target.value)} required />
                  </Field>

                  <Field label="Hora" required>
                    <Input type="time" value={time} onChange={(event) => setTime(event.target.value)} required />
                  </Field>

                  <Field label="Comensales" required>
                    <Input
                      type="number"
                      min={1}
                      step={1}
                      value={guests}
                      onChange={(event) => setGuests(Number(event.target.value))}
                      required
                    />
                  </Field>

                  {isEditing && (
                    <Field label="Estado" required>
                      <Select
                        value={status}
                        onChange={(event) => setStatus(event.target.value as ReservationStatus)}
                      >
                        <option value="pendiente">Pendiente</option>
                        <option value="con_comanda">Con comanda</option>
                        <option value="ausente">Ausente</option>
                      </Select>
                    </Field>
                  )}

                  {customerSelection === newCustomerValue && (
                    <>
                      <Field label="DNI" required>
                        <Input value={customerDni} onChange={(event) => setCustomerDni(event.target.value)} required />
                      </Field>
                      <Field label="Nombre" required>
                        <Input
                          value={customerFirstName}
                          onChange={(event) => setCustomerFirstName(event.target.value)}
                          required
                        />
                      </Field>
                      <Field label="Apellido" required>
                        <Input
                          value={customerLastName}
                          onChange={(event) => setCustomerLastName(event.target.value)}
                          required
                        />
                      </Field>
                      <Field label="Teléfono" required>
                        <Input
                          value={customerPhone}
                          onChange={(event) => setCustomerPhone(event.target.value)}
                          pattern="[0-9-]+"
                          title="Ingresá solo números y guiones."
                          required
                        />
                      </Field>
                    </>
                  )}

                  <Field label="Notas" className="span-full">
                    <Textarea
                      value={notes}
                      onChange={(event) => setNotes(event.target.value)}
                      placeholder="Preferencias, ocasión especial u observaciones"
                    />
                  </Field>
                </div>}
              </>
            )}
          </Card>

          {!loading && canEdit && (
            <>
              <Card title="Mesas asignadas" subtitle="Podés asociar más de una mesa a la reserva.">
                <div className="form-grid">
                  <Field label="Agregar mesa">
                    <Select value={tableToAdd} onChange={(event) => setTableToAdd(event.target.value)}>
                      <option value="">Seleccioná una mesa</option>
                      {tables.filter((table) => table.estado && !selectedTableIds.includes(table.id)).map((table) => (
                        <option key={table.id} value={table.id}>
                          Mesa {table.id} · {table.capacidad} personas
                        </option>
                      ))}
                    </Select>
                  </Field>
                  <div className="field">
                    <span className="label" aria-hidden="true">&nbsp;</span>
                    <Button type="button" onClick={addTable} disabled={!tableToAdd}>
                      Agregar mesa
                    </Button>
                  </div>
                </div>
                {selectedTableIds.length ? (
                  <div className="stack">
                    {selectedTableIds.map((tableId) => {
                      const table = tableById.get(tableId)
                      return (
                        <div className="row" key={tableId}>
                          <span>
                            Mesa {tableId} · {table?.capacidad ?? '—'} personas
                          </span>
                          <Button
                            type="button"
                            size="sm"
                            variant="danger-ghost"
                            onClick={() => setSelectedTableIds((current) => current.filter((value) => value !== tableId))}
                          >
                            Quitar
                          </Button>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <p className="muted">No hay mesas asignadas.</p>
                )}
              </Card>

              <Card title="Detalle de comanda" subtitle="Productos ficticios por ahora.">
                <div className="form-grid">
                  <Field label="Agregar producto">
                    <Select value={productToAdd} onChange={(event) => setProductToAdd(event.target.value)}>
                      <option value="">Seleccioná un producto</option>
                      {availableProducts
                        .filter((product) => !details.some((detail) => detail.productId === product.id))
                        .map((product) => (
                          <option key={product.id} value={product.id}>{product.name}</option>
                        ))}
                    </Select>
                  </Field>
                  <div className="field">
                    <span className="label" aria-hidden="true">&nbsp;</span>
                    <Button type="button" onClick={addDetail} disabled={!productToAdd}>
                      Agregar producto
                    </Button>
                  </div>
                </div>
                {details.length ? (
                  <div className="stack">
                    {details.map((detail) => (
                      <div className="row" key={detail.productId}>
                        <span>
                          {availableProducts.find((product) => product.id === detail.productId)?.name
                            ?? `Producto #${detail.productId}`}
                        </span>
                        <Field label="Cantidad">
                          <Input
                            type="number"
                            min={1}
                            step={1}
                            value={detail.quantity}
                            onChange={(event) => {
                              const quantity = Number(event.target.value)
                              setDetails((current) => current.map((candidate) =>
                                candidate.productId === detail.productId ? { ...candidate, quantity } : candidate,
                              ))
                            }}
                            required
                          />
                        </Field>
                        <Button
                          type="button"
                          size="sm"
                          variant="danger-ghost"
                          onClick={() => setDetails((current) => current.filter((value) => value.productId !== detail.productId))}
                        >
                          Quitar
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="muted">No hay productos agregados al detalle.</p>
                )}
              </Card>
            </>
          )}
        </div>
      </form>
    </>
  )
}
