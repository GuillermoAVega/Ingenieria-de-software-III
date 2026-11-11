import { formatCurrency } from '../../../utils/format'
import type { MenuViewItem } from '../types'

export function MenuItemRow({ item }: { item: MenuViewItem }) {
  return (
    <li className="menu-view-item" data-print-item={item.key}>
      <div className="menu-view-item-info">
        <span className="menu-view-item-name">{item.nombre}</span>
        {item.descripcion && <small className="menu-view-description">{item.descripcion}</small>}
        {item.platoNombre && (
          <small className="menu-view-description">Plato: {item.platoNombre}</small>
        )}
        {item.postreNombre && (
          <small className="menu-view-description">Postre: {item.postreNombre}</small>
        )}
        {item.promociones.length > 0 && (
          <span className="menu-view-promotions">
            {item.promociones.map((promotion) => (
              <small className="menu-view-promotion" key={promotion}>{promotion}</small>
            ))}
          </span>
        )}
      </div>
      <span className="menu-view-prices">
        {item.precioOriginal && (
          <span className="menu-view-price-original">{formatCurrency(item.precioOriginal)}</span>
        )}
        <span className="menu-view-price">{formatCurrency(item.precio)}</span>
      </span>
    </li>
  )
}
