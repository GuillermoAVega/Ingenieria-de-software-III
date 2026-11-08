/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de promociones
 * La lógica vive en `usePromotionForm`; la pantalla solo renderiza.
 */
import { Alert, Button, Card, DateInput, Field, Input, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { usePromotionForm } from './usePromotionForm'
import { ProductPicker } from './ProductPicker'
import type { PromotionType } from './types'

export function PromotionFormPage({ id }: { id?: string }) {
  return <PromotionForm key={id ?? 'nueva'} id={id} />
}

function PromotionForm({ id }: { id?: string }) {
  const {
    state,
    options,
    isEditing,
    updateField,
    updateSearch,
    toggleProduct,
    submit,
  } = usePromotionForm(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar promoción' : 'Nueva promoción'}
        subtitle="Configurá el descuento, la vigencia y los productos de la promoción."
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
      ) : state.inUse ? (
        <Alert tone="warning" title="Esta promoción no se puede editar">
          <p>
            Ya fue aplicada en facturas, por lo que no puede modificarse. Podés dejarla sin efecto
            dándola de baja desde el listado y crear una nueva.
          </p>
          <a href="#/promociones">Volver al listado de promociones</a>
        </Alert>
      ) : (
        <form onSubmit={submit} noValidate>
          <Card
            footer={
              <>
                <Button onClick={() => navigate('/promociones')} disabled={state.saving}>
                  Cancelar
                </Button>
                <Button variant="primary" type="submit" disabled={state.saving}>
                  {state.saving ? 'Guardando...' : 'Guardar promoción'}
                </Button>
              </>
            }
          >
            <div className="form-grid">
              <Field label="Nombre" required error={state.fieldErrors.nombre}>
                <Input
                  value={state.nombre}
                  invalid={Boolean(state.fieldErrors.nombre)}
                  placeholder="Nombre de la promoción"
                  onChange={(event) => updateField('nombre', event.target.value)}
                />
              </Field>

              <Field label="Tipo de promoción" required>
                <Select
                  value={state.tipo}
                  onChange={(event) => updateField('tipo', event.target.value as PromotionType)}
                >
                  <option value="porcentaje">Porcentaje</option>
                  <option value="lleva_paga">Por cantidad (2x1, 3x2…)</option>
                </Select>
              </Field>

              {state.tipo === 'porcentaje' ? (
                <Field label="Descuento (%)" required error={state.fieldErrors.descuento}>
                  <Input
                    type="number"
                    min={0}
                    max={100}
                    step="0.01"
                    value={state.descuento}
                    invalid={Boolean(state.fieldErrors.descuento)}
                    placeholder="0"
                    onChange={(event) => updateField('descuento', event.target.value)}
                  />
                </Field>
              ) : (
                <>
                  <Field label="Lleva (unidades)" required error={state.fieldErrors.lleva}>
                    <Input
                      type="number"
                      min={2}
                      step={1}
                      value={state.lleva}
                      invalid={Boolean(state.fieldErrors.lleva)}
                      placeholder="3"
                      onChange={(event) => updateField('lleva', event.target.value)}
                    />
                  </Field>
                  <Field label="Paga (unidades)" required error={state.fieldErrors.paga}>
                    <Input
                      type="number"
                      min={1}
                      step={1}
                      value={state.paga}
                      invalid={Boolean(state.fieldErrors.paga)}
                      placeholder="2"
                      onChange={(event) => updateField('paga', event.target.value)}
                    />
                  </Field>
                </>
              )}

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

              <Field
                label="Productos"
                required
                className="span-full"
                error={state.fieldErrors.productos_ids}
              >
                <ProductPicker
                  options={options}
                  selectedKeys={state.productosIds.map(String)}
                  search={state.search}
                  onSearchChange={updateSearch}
                  onToggle={toggleProduct}
                />
              </Field>
            </div>
          </Card>
        </form>
      )}
    </>
  )
}
