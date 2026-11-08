/**
 * Selector de productos con búsqueda, compartido por promociones y combos.
 * Es presentacional: el estado vive en el hook de cada formulario.
 * Si recibe `quantityOf` y `onQuantityChange`, muestra una cantidad por seleccionado.
 */
import { Badge, Check, Input } from '../../ui/ui'
import { normalizeText } from './text'

export type PickerOption = {
  /** Clave única dentro del selector (los ids pueden repetirse entre tipos). */
  key: string
  nombre: string
  tipoLabel: string
  dado_de_baja: boolean
}

type ProductPickerProps = {
  options: PickerOption[]
  selectedKeys: string[]
  search: string
  onSearchChange: (search: string) => void
  onToggle: (key: string) => void
  /** Cantidad (como texto) del seleccionado; junto con `onQuantityChange` activa la variante de combos. */
  quantityOf?: (key: string) => string
  onQuantityChange?: (key: string, value: string) => void
  /** Error por seleccionado (por ejemplo, cantidad inválida). */
  quantityError?: (key: string) => string | undefined
  ariaLabel?: string
  emptyText?: string
  unitLabel?: { singular: string; plural: string }
}

export function ProductPicker({
  options,
  selectedKeys,
  search,
  onSearchChange,
  onToggle,
  quantityOf,
  onQuantityChange,
  quantityError,
  ariaLabel = 'Productos',
  emptyText = 'No hay productos disponibles en la carta.',
  unitLabel = { singular: 'producto seleccionado', plural: 'productos seleccionados' },
}: ProductPickerProps) {
  // Los dados de baja solo se muestran si ya están seleccionados
  const visible = options.filter(
    (option) => !option.dado_de_baja || selectedKeys.includes(option.key),
  )
  // Los seleccionados se muestran siempre; el filtro solo recorta los demás
  const selected = visible.filter((option) => selectedKeys.includes(option.key))
  const term = normalizeText(search)
  const available = visible.filter(
    (option) =>
      !selectedKeys.includes(option.key) &&
      (term === '' || normalizeText(option.nombre).includes(term)),
  )
  const withQuantity = quantityOf !== undefined && onQuantityChange !== undefined

  const label = (option: PickerOption) => (
    <>
      {option.nombre} <Badge>{option.tipoLabel}</Badge>
      {option.dado_de_baja ? ' - dado de baja' : ''}
    </>
  )

  return (
    <div className="product-picker">
      <Input
        type="search"
        aria-label={`Buscar ${ariaLabel.toLowerCase()} por nombre`}
        placeholder="Buscar..."
        value={search}
        onChange={(event) => onSearchChange(event.target.value)}
      />
      <p className="hint" aria-live="polite">
        {selectedKeys.length === 1
          ? `1 ${unitLabel.singular}`
          : `${selectedKeys.length} ${unitLabel.plural}`}
      </p>
      <div className="product-picker-list" role="group" aria-label={ariaLabel}>
        {visible.length === 0 && <p className="muted">{emptyText}</p>}
        {selected.length > 0 && (
          <>
            <p className="product-picker-title">Seleccionados</p>
            {selected.map((option) => (
              <div className="product-picker-row" key={option.key}>
                <Check checked onChange={() => onToggle(option.key)}>
                  {label(option)}
                </Check>
                {withQuantity && (
                  <label className="product-picker-qty">
                    <span className="muted">Cantidad</span>
                    <Input
                      type="number"
                      min={1}
                      step={1}
                      aria-label={`Cantidad de ${option.nombre}`}
                      value={quantityOf(option.key)}
                      invalid={Boolean(quantityError?.(option.key))}
                      onChange={(event) => onQuantityChange(option.key, event.target.value)}
                    />
                    {quantityError?.(option.key) && (
                      <span className="error-text">{quantityError(option.key)}</span>
                    )}
                  </label>
                )}
              </div>
            ))}
          </>
        )}
        {visible.length > 0 && <p className="product-picker-title">Disponibles</p>}
        {visible.length > 0 && available.length === 0 && (
          <p className="muted">Ningún elemento coincide con la búsqueda.</p>
        )}
        {available.map((option) => (
          <Check key={option.key} checked={false} onChange={() => onToggle(option.key)}>
            {label(option)}
          </Check>
        ))}
      </div>
    </div>
  )
}
