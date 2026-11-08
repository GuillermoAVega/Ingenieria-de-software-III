/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de combos
 * La lógica vive en `useComboForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, DateInput, Field, Input, PageHeader, Select, Textarea } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { ProductPicker } from '../promotions/ProductPicker'
import { useComboForm } from './useComboForm'

const formatCurrency = (value: number) => `$ ${value.toLocaleString('es-AR')}`

export function ComboFormPage({ id }: { id?: string }) {
  return <ComboForm key={id ?? 'nuevo'} id={id} />
}

function ComboForm({ id }: { id?: string }) {
  const {
    state,
    isEditing,
    selectedKeys,
    componentsTotal,
    savings,
    updateField,
    updateSearch,
    toggleComponent,
    updateQuantity,
    quantityError,
    submit,
  } = useComboForm(id)

  const componentsError =
    state.fieldErrors.componentes ??
    state.fieldErrors.platos ??
    state.fieldErrors.bebidas ??
    state.fieldErrors.postres

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar combo' : 'Nuevo combo'}
        subtitle="Configurá el precio, la vigencia y los componentes del combo."
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo completar la operación">
          {state.error}
        </Alert>
      )}

      {state.loading ? (
        <Card>
          <p className="muted">Cargando...</p>
        </Card>
      ) : (
        <form onSubmit={submit} noValidate>
          <Card
            footer={
              <>
                <Button onClick={() => navigate('/productos/combos')} disabled={state.saving}>
                  Cancelar
                </Button>
                <Button variant="primary" type="submit" disabled={state.saving}>
                  {state.saving ? 'Guardando...' : 'Guardar combo'}
                </Button>
              </>
            }
          >
            <div className="form-grid">
              <Field label="Nombre" required error={state.fieldErrors.nombre}>
                <Input
                  value={state.nombre}
                  invalid={Boolean(state.fieldErrors.nombre)}
                  placeholder="Nombre del combo"
                  onChange={(event) => updateField('nombre', event.target.value)}
                />
              </Field>

              <Field label="Precio" required error={state.fieldErrors.precio}>
                <Input
                  type="number"
                  min={0}
                  step="0.01"
                  value={state.precio}
                  invalid={Boolean(state.fieldErrors.precio)}
                  placeholder="0"
                  onChange={(event) => updateField('precio', event.target.value)}
                />
              </Field>

              <Field label="Desde" required error={state.fieldErrors.fecha_desde}>
                <DateInput
                  value={state.fecha_desde}
                  invalid={Boolean(state.fieldErrors.fecha_desde)}
                  onChange={(value) => updateField('fecha_desde', value)}
                />
              </Field>

              <Field label="Hasta" required error={state.fieldErrors.fecha_hasta}>
                <DateInput
                  value={state.fecha_hasta}
                  invalid={Boolean(state.fieldErrors.fecha_hasta)}
                  onChange={(value) => updateField('fecha_hasta', value)}
                />
              </Field>

              <Field label="Sección" error={state.fieldErrors.seccion_id}>
                <Select
                  value={state.seccionId}
                  onChange={(event) => updateField('seccionId', event.target.value)}
                >
                  <option value="">Sin sección</option>
                  {state.sections.map((section) => (
                    <option key={section.id} value={section.id}>
                      {section.nombre}
                    </option>
                  ))}
                </Select>
              </Field>

              <Field label="Descripción" className="span-full" error={state.fieldErrors.descripcion}>
                <Textarea
                  value={state.descripcion}
                  onChange={(event) => updateField('descripcion', event.target.value)}
                  placeholder="Detalle del combo"
                />
              </Field>

              <Field label="Componentes" required className="span-full" error={componentsError}>
                <ProductPicker
                  options={state.options}
                  selectedKeys={selectedKeys}
                  search={state.search}
                  onSearchChange={updateSearch}
                  onToggle={toggleComponent}
                  quantityOf={(key) => state.quantities[key] ?? '1'}
                  onQuantityChange={updateQuantity}
                  quantityError={quantityError}
                  ariaLabel="Componentes"
                  emptyText="No hay platos, bebidas ni postres disponibles."
                  unitLabel={{
                    singular: 'componente seleccionado',
                    plural: 'componentes seleccionados',
                  }}
                />
                <p className="combo-summary" aria-live="polite">
                  Precio de los componentes: {formatCurrency(componentsTotal)}
                  {savings !== null && savings > 0 && ` — ahorro ${formatCurrency(savings)}`}
                  {savings !== null && savings <= 0 && ' — sin ahorro'}
                </p>
              </Field>
            </div>
          </Card>
        </form>
      )}
    </>
  )
}
