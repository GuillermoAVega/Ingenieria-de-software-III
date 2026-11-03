import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Alert, Button, Card, Field, Input, PageHeader, Select, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import {
  addReservationDetail,
  createCustomer,
  createReservation,
  listReservationDetails,
  removeReservationDetail,
  updateReservation,
} from './api'
import type {
  CustomerRecord,
  ReservationDetailPayload,
  ReservationStatus,
  TableRecord,
} from './types'
import { useReservationTableAvailability } from './useReservationTableAvailability'
import { ReservationAvailabilitySummary } from './ReservationAvailabilitySummary'
import { useReservationFormData } from './useReservationFormData'

const newCustomerValue = 'nuevo'
const fakeProducts = [
  { id: 1, name: 'Empanadas surtidas', type: 'Plato' },
  { id: 2, name: 'Pizza muzzarella', type: 'Combo' },
  { id: 3, name: 'Ensalada de estación', type: 'Plato' },
  { id: 4, name: 'Flan casero', type: 'Postre' },
]

type DetailRow = {
  productId: number
  quantity: number
}

function seleccionarMesasDisponibles(tables: TableRecord[], guests: number): number[] {
  if (!Number.isInteger(guests) || guests < 1) return []
  let bestIds: number[] | null = null
  let bestCapacity = Number.POSITIVE_INFINITY

  function search(index: number, ids: number[], capacity: number) {
    if (capacity >= guests) {
      if (capacity < bestCapacity || (capacity === bestCapacity && ids.length > (bestIds?.length ?? 0))) {
        bestIds = ids
        bestCapacity = capacity
      }
      return
    }

    for (let position = index; position < tables.length; position += 1) {
      const table = tables[position]
      search(position + 1, [...ids, table.id], capacity + table.capacidad)
    }
  }

  search(0, [], 0)
  return bestIds ?? []
}

function getErrorMessage(cause: unknown, fallback: string): string {
  return cause instanceof Error ? cause.message : fallback
}

export function ReservationFormPage({ id }: { id?: string }) {
  const isEditing = Boolean(id)
  const formData = useReservationFormData(id)
  const [step, setStep] = useState<1 | 2>(isEditing ? 2 : 1)
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
  const [details, setDetails] = useState<DetailRow[]>([])
  const [productToAdd, setProductToAdd] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loading = formData.loading
  const loadFailed = formData.loadFailed

  useEffect(() => {
    if (!formData.reservation) {
      setCustomers(formData.customers)
      setTables(formData.tables)
      return
    }

    const reservation = formData.reservation
    setCustomers(formData.customers)
    setTables(formData.tables)
    setCustomerSelection(String(reservation.cliente_id))
    setDate(reservation.fecha)
    setTime(reservation.hora.slice(0, 5))
    setGuests(reservation.cant_comensales)
    setStatus(reservation.estado)
    setInitialStatus(reservation.estado)
    setNotes(reservation.observaciones ?? '')
    setSelectedTableIds(formData.reservationTables.map((table) => table.id))
    setDetails(formData.reservationDetails.map((detail) => ({
      productId: detail.producto_id,
      quantity: detail.cantidad_producto,
    })))
  }, [formData])

  const tableById = useMemo(() => new Map(tables.map((table) => [table.id, table])), [tables])
  const availabilityTableIds = useMemo(
    () => [...new Set([...tables.map((table) => table.id), ...selectedTableIds])],
    [selectedTableIds, tables],
  )
  const tableAvailability = useReservationTableAvailability(
    date,
    time,
    availabilityTableIds,
    id ? Number(id) : undefined,
  )
  const reservationTableIssues = useMemo(() => ({
    conflicts: tableAvailability.conflicts.filter(({ tableId }) => selectedTableIds.includes(tableId)),
    warnings: tableAvailability.warnings.filter(({ tableId }) => selectedTableIds.includes(tableId)),
  }), [selectedTableIds, tableAvailability.conflicts, tableAvailability.warnings])
  const scheduleTableAvailability = useMemo(() => {
    const conflicts = new Set(tableAvailability.conflicts.map(({ tableId }) => tableId))
    const warnings = new Set(tableAvailability.warnings.map(({ tableId }) => tableId))
    return {
      available: tables.filter((table) => table.estado && !selectedTableIds.includes(table.id) && !conflicts.has(table.id) && !warnings.has(table.id)),
      warning: tables.filter((table) => table.estado && !selectedTableIds.includes(table.id) && !conflicts.has(table.id) && warnings.has(table.id)),
      unavailable: tables.filter((table) => table.estado && !selectedTableIds.includes(table.id) && conflicts.has(table.id)),
    }
  }, [selectedTableIds, tableAvailability.conflicts, tableAvailability.warnings, tables])
  const formLoading = loading || tableAvailability.loading

  const assignedCapacity = selectedTableIds.reduce(
    (capacity, tableId) => capacity + (tableById.get(tableId)?.capacidad ?? 0),
    0,
  )
  const tableAssignmentError = selectedTableIds.length === 0
    ? 'Asigná al menos una mesa a la reserva.'
    : assignedCapacity < guests
      ? `La capacidad total de las mesas (${assignedCapacity}) no alcanza para ${guests} comensales.`
      : null
  const availableProducts = useMemo(() => {
    const products = [...fakeProducts]
    for (const detail of details) {
      if (!products.some((product) => product.id === detail.productId)) {
        products.push({ id: detail.productId, name: `Producto #${detail.productId}`, type: 'Producto' })
      }
    }
    return products
  }, [details])
  const canEdit = !isEditing || initialStatus === 'pendiente'

  function addDetail() {
    const productId = Number(productToAdd)
    if (!productId || details.some((detail) => detail.productId === productId)) return
    setDetails((current) => [...current, { productId, quantity: 1 }])
    setProductToAdd('')
  }

  function continueReservation() {
    if (!customerSelection || !date || !time || guests < 1) {
      setError('Completá cliente, fecha, hora y cantidad de comensales para continuar.')
      return
    }
    if (
      customerSelection === newCustomerValue &&
      (!customerDni.trim() || !customerFirstName.trim() || !customerLastName.trim() || !customerPhone.trim())
    ) {
      setError('Completá todos los datos del cliente nuevo para continuar.')
      return
    }
    setSelectedTableIds(seleccionarMesasDisponibles(scheduleTableAvailability.available, guests))
    setError(null)
    setStep(2)
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
      if (tableAssignmentError) throw new Error(tableAssignmentError)
      if (reservationTableIssues.conflicts.length) {
        const { tableId } = reservationTableIssues.conflicts[0]
        throw new Error(`La mesa ${tableId} ya está reservada para esa fecha y hora.`)
      }

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
        await updateReservation(reservationId, {
          ...payload,
          estado: status,
          mesa_ids: selectedTableIds,
        })
        await saveDetailChanges(reservationId, detailsPayload)
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
      {step === 1 && <div className="reservation-page-header">
        <PageHeader
          title={isEditing ? 'Editar reserva' : 'Nueva reserva'}
          subtitle={isEditing
            ? 'Actualizá el cliente, los datos, las mesas y el detalle de la reserva.'
            : 'Registrá una reserva y elegí un cliente, una o varias mesas y sus productos.'}
        />
      </div>}

      <form onSubmit={handleSubmit}>
        <div className="stack">
          {step === 1 && (
            <>
          <Card
            title="Datos de la reserva"
          >
            {(error || formData.error || tableAvailability.error) && (
              <Alert tone="danger">{error ?? formData.error ?? tableAvailability.error}</Alert>
            )}
            {formLoading ? (
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

          <div className="card-footer">
            <Button onClick={() => navigate('/reservas')}>Cancelar</Button>
            <Button variant="primary" onClick={continueReservation} disabled={formLoading || loadFailed || saving || !canEdit}>
              Continuar reserva
            </Button>
          </div>
            </>
          )}

          {step === 2 && !formLoading && canEdit && (
            <Card
              className="reservation-config-card"
              title="Configurar reserva"
              subtitle="Elegí las mesas y agregá productos anticipados de forma opcional."
            >
            <div className="reservation-step">
              <Card className="reservation-section" title="Mesas asignadas" subtitle="Se asignan automáticamente según la cantidad de comensales y la disponibilidad.">
                <ReservationAvailabilitySummary
                  date={date}
                  time={time}
                  available={scheduleTableAvailability.available}
                  warning={scheduleTableAvailability.warning}
                  unavailable={scheduleTableAvailability.unavailable}
                  onSelectTable={(tableId) => setSelectedTableIds((current) => current.includes(tableId) ? current : [...current, tableId])}
                />
                {selectedTableIds.length ? (
                  <div className="table-assignment-list reservation-table-list">
                    {selectedTableIds.map((tableId) => {
                      const table = tableById.get(tableId)
                      return (
                        <button
                          className="table-assignment-chip"
                          key={tableId}
                          type="button"
                          onClick={() => setSelectedTableIds((current) => current.filter((value) => value !== tableId))}
                          title="Quitar mesa asignada"
                        >
                          Mesa {tableId}<small>{table?.capacidad ?? '—'} personas · Quitar</small>
                        </button>
                      )
                    })}
                  </div>
                ) : (
                  <p className="muted">No hay una combinación de mesas disponible para esa cantidad de comensales.</p>
                )}
                {tableAssignmentError ? (
                  <p className="error-text" role="alert">{tableAssignmentError}</p>
                ) : (
                  <p className="muted" role="status">
                    Capacidad asignada: {assignedCapacity} para {guests} comensales.
                  </p>
                )}
                {reservationTableIssues.conflicts.map(({ tableId, time: occupiedTime }) => (
                  <Alert key={`${tableId}-${occupiedTime}`} tone="danger" title="Mesa ya reservada">
                    La mesa {tableId} ya está reservada para las {occupiedTime}. Elegí otra mesa u horario.
                  </Alert>
                ))}
                {reservationTableIssues.warnings.map(({ tableId, time: occupiedTime }) => (
                  <Alert key={`${tableId}-${occupiedTime}`} tone="warning" title="Atención con la ocupación de la mesa">
                    La mesa {tableId} estará ocupada desde las {occupiedTime} por otra reserva.
                  </Alert>
                ))}
              </Card>

              <Card className="reservation-section" title="Productos anticipados (opcional)" subtitle="Podés agregarlos ahora o directamente desde la comanda.">
                <div className="form-grid">
                  <Field label="Agregar producto">
                    <Select value={productToAdd} onChange={(event) => setProductToAdd(event.target.value)}>
                      <option value="">Seleccioná un producto</option>
                      {availableProducts
                        .filter((product) => !details.some((detail) => detail.productId === product.id))
                        .map((product) => (
                          <option key={product.id} value={product.id}>{product.name} · {product.type}</option>
                        ))}
                    </Select>
                  </Field>
                  <div className="field reservation-action">
                    <span className="label" aria-hidden="true">&nbsp;</span>
                    <Button type="button" onClick={addDetail} disabled={!productToAdd}>
                      Agregar producto
                    </Button>
                  </div>
                </div>
                {details.length ? (
                  <div className="stack reservation-product-list">
                    {details.map((detail) => (
                      <div className="row reservation-selection reservation-product-selection" key={detail.productId}>
                        <span>
                          {availableProducts.find((product) => product.id === detail.productId)?.name
                            ?? `Producto #${detail.productId}`}
                          <span className="reservation-product-type">
                            {availableProducts.find((product) => product.id === detail.productId)?.type ?? 'Producto'}
                          </span>
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
              <div className="card-footer reservation-actions">
                <Button onClick={() => navigate('/reservas')} disabled={saving}>Cancelar</Button>
                {!isEditing && <Button onClick={() => setStep(1)} disabled={saving}>Volver</Button>}
                <Button
                  variant="primary"
                  type="submit"
                  disabled={
                    formLoading ||
                    loadFailed ||
                    Boolean(tableAvailability.error) ||
                    saving ||
                    !canEdit ||
                    Boolean(tableAssignmentError) ||
                    reservationTableIssues.conflicts.length > 0
                  }
                >
                  {saving ? 'Guardando...' : 'Guardar reserva'}
                </Button>
              </div>
            </div>
            </Card>
          )}
        </div>
      </form>
    </>
  )
}
