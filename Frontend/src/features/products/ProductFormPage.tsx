/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de platos
 * COMPLETAR:
 * 1. Reemplazar DEMO_PRODUCTS por la carga desde la API.
 * 2. Implementar la subida de imagen y sus validaciones.
 * 3. Guardar el plato contra la API.
 */
import { Breadcrumb, Button, Card, Dropzone, Field, Input, InputGroup, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_PRODUCTS, DEMO_PRODUCT_SECTIONS } from './demo'

export function ProductFormPage({ id }: { id?: string }) {
  const product = id ? DEMO_PRODUCTS.find((candidate) => candidate.id === id) : undefined
  const isEditing = Boolean(id)

  return (
    <>
      <PageHeader
        breadcrumb={
          <Breadcrumb
            items={[
              { label: 'Productos', href: '#/productos' },
              { label: isEditing ? 'Editar plato' : 'Nuevo plato' },
            ]}
          />
        }
        title={isEditing ? 'Editar plato' : 'Nuevo plato'}
        subtitle="Completá los datos que se van a mostrar en la carta."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-carta): guardar el plato en la API.
        }}
      >
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/productos')}>Cancelar</Button>
              <Button variant="primary" type="submit">
                Guardar plato
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Nombre" required>
              <Input defaultValue={product?.name ?? ''} placeholder="Nombre del plato" />
            </Field>

            <Field label="Sección" required>
              <Select defaultValue={product?.section ?? ''}>
                <option value="">Seleccioná una sección</option>
                {DEMO_PRODUCT_SECTIONS.map((section) => (
                  <option key={section} value={section}>
                    {section}
                  </option>
                ))}
              </Select>
            </Field>

            <Field label="Precio" required>
              <InputGroup prefix="$">
                <Input type="number" min={0} defaultValue={product?.price ?? ''} placeholder="0" />
              </InputGroup>
            </Field>

            <Field label="Imagen" className="span-full">
              <Dropzone
                title="Arrastrá la imagen del plato o elegila desde tu equipo"
                hint="JPG o PNG hasta 2 MB"
                action={
                  <Button
                    variant="secondary"
                    onClick={() => {
                      // TODO(equipo-carta): abrir el selector de archivos y validar tamaño/formato.
                    }}
                  >
                    Elegir archivo
                  </Button>
                }
              />
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
