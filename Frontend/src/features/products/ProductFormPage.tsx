/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de platos, bebidas y postres
 * La lógica del formulario vive en `useProductForm`; la pantalla solo renderiza.
 */
import {
  Alert,
  Button,
  Card,
  Field,
  Input,
  InputGroup,
  PageHeader,
  Select,
  Switch,
  Textarea,
} from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useProductForm } from './useProductForm'
import type { ProductType } from './useProductForm'

const TITLES: Record<ProductType, { new: string; edit: string; save: string; loading: string }> = {
  platos: {
    new: 'Nuevo plato',
    edit: 'Editar plato',
    save: 'Guardar plato',
    loading: 'Cargando plato...',
  },
  bebidas: {
    new: 'Nueva bebida',
    edit: 'Editar bebida',
    save: 'Guardar bebida',
    loading: 'Cargando bebida...',
  },
  postres: {
    new: 'Nuevo postre',
    edit: 'Editar postre',
    save: 'Guardar postre',
    loading: 'Cargando postre...',
  },
}

function normalizeType(tipo?: string): ProductType {
  return tipo === 'bebidas' || tipo === 'postres' ? tipo : 'platos'
}

export function ProductFormPage({ tipo, id }: { tipo?: string; id?: string }) {
  const productType = normalizeType(tipo)
  return <ProductForm key={`${productType}-${id ?? 'nuevo'}`} tipo={productType} id={id} />
}

function ProductForm({ tipo, id }: { tipo: ProductType; id?: string }) {
  const { state, isEditing, updateField, submit } = useProductForm(tipo, id)
  const titles = TITLES[tipo]

  return (
    <>
      <PageHeader
        title={isEditing ? titles.edit : titles.new}
        subtitle="Completá los datos que se van a mostrar en la carta."
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo guardar el producto">
          {state.error}
        </Alert>
      )}

      {state.loading ? (
        <Card>
          <p className="muted">{titles.loading}</p>
        </Card>
      ) : (
        <form onSubmit={submit}>
          <Card
            footer={
              <>
                <Button onClick={() => navigate('/productos')} disabled={state.saving}>
                  Cancelar
                </Button>
                <Button variant="primary" type="submit" disabled={state.saving}>
                  {state.saving ? 'Guardando...' : titles.save}
                </Button>
              </>
            }
          >
            <div className="form-grid">
              <Field label="Nombre" required error={state.fieldErrors.nombre}>
                <Input
                  value={state.nombre}
                  onChange={(event) => updateField('nombre', event.target.value)}
                  placeholder="Nombre del producto"
                  required
                />
              </Field>

              <Field
                label="Sección"
                hint="Opcional. Elegí la sección donde se muestra el producto."
                error={state.fieldErrors.seccion_id ?? state.sectionsError ?? undefined}
              >
                <Select
                  value={state.seccionId}
                  onChange={(event) => updateField('seccionId', event.target.value)}
                  disabled={state.sectionsLoading}
                >
                  <option value="">
                    {state.sectionsLoading ? 'Cargando secciones...' : 'Sin sección'}
                  </option>
                  {state.sections.map((section) => (
                    <option key={section.id} value={section.id}>
                      {section.nombre}
                    </option>
                  ))}
                </Select>
              </Field>

              <Field label="Precio" required error={state.fieldErrors.precio}>
                <InputGroup prefix="$">
                  <Input
                    type="number"
                    min={0.01}
                    step="0.01"
                    value={state.precio}
                    onChange={(event) => updateField('precio', event.target.value)}
                    placeholder="0"
                    required
                  />
                </InputGroup>
              </Field>

              {tipo === 'platos' && (
                <Field
                  label="Cantidad de personas"
                  required
                  hint="Entero mayor o igual a 1."
                  error={state.fieldErrors.cant_personas}
                >
                  <Input
                    type="number"
                    min={1}
                    step={1}
                    value={state.cantPersonas}
                    onChange={(event) => updateField('cantPersonas', event.target.value)}
                    required
                  />
                </Field>
              )}

              {tipo === 'bebidas' && (
                <Field label="Bebida alcohólica" error={state.fieldErrors.es_alcoholica}>
                  <Switch
                    checked={state.esAlcoholica}
                    onChange={(event) => updateField('esAlcoholica', event.target.checked)}
                  >
                    Contiene alcohol
                  </Switch>
                </Field>
              )}

              <Field label="Descripción" className="span-full" error={state.fieldErrors.descripcion}>
                <Textarea
                  value={state.descripcion}
                  onChange={(event) => updateField('descripcion', event.target.value)}
                  placeholder="Descripción breve del producto"
                />
              </Field>
            </div>
          </Card>
        </form>
      )}
    </>
  )
}
