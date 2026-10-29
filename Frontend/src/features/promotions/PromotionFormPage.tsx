/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Alta y edición de promociones
 * COMPLETAR:
 * 1. Reemplazar DEMO_PROMOTIONS por la carga desde la API.
 * 2. Validar el rango de vigencia y el valor del descuento.
 * 3. Guardar la promoción contra la API.
 */
import { Button, Card, Field, Input, PageHeader, Select, Switch } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_PROMOTIONS } from './demo'

export function PromotionFormPage({ id }: { id?: string }) {
  const promotion = id ? DEMO_PROMOTIONS.find((candidate) => candidate.id === id) : undefined
  const isEditing = Boolean(id)

  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar promoción' : 'Nueva promoción'}
        subtitle="Configurá el alcance, el descuento y la vigencia de la promoción."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          // TODO(equipo-carta): guardar la promoción en la API.
        }}
      >
        <Card
          footer={
            <>
              <Button onClick={() => navigate('/promociones')}>Cancelar</Button>
              <Button variant="primary" type="submit">
                Guardar promoción
              </Button>
            </>
          }
        >
          <div className="form-grid">
            <Field label="Nombre" required>
              <Input defaultValue={promotion?.name ?? ''} placeholder="Nombre de la promoción" />
            </Field>

            <Field label="Aplica a" required>
              <Select defaultValue={promotion?.appliesTo ?? ''}>
                <option value="">Seleccioná un alcance</option>
                <option value="Toda la carta">Toda la carta</option>
                <option value="Platos">Platos</option>
                <option value="Bebidas">Bebidas</option>
                <option value="Postres">Postres</option>
                <option value="Menú ejecutivo">Menú ejecutivo</option>
                <option value="Combos">Combos</option>
              </Select>
            </Field>

            <Field label="Tipo de descuento" required>
              <Select defaultValue={promotion?.discountType ?? 'Porcentaje'}>
                <option value="Porcentaje">Porcentaje</option>
                <option value="Monto fijo">Monto fijo</option>
              </Select>
            </Field>

            <Field label="Valor" required>
              <Input type="number" min={0} defaultValue={promotion?.discountValue ?? ''} placeholder="0" />
            </Field>

            <Field label="Desde" required>
              <Input type="date" defaultValue={promotion?.from ?? '2026-10-16'} />
            </Field>

            <Field label="Hasta" required>
              <Input type="date" defaultValue={promotion?.to ?? '2026-11-30'} />
            </Field>

            <Field label="Activa" className="span-full">
              <Switch defaultChecked={promotion?.active ?? true}>La promoción está activa</Switch>
            </Field>
          </div>
        </Card>
      </form>
    </>
  )
}
