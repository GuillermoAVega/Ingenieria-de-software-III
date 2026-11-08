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
      </div>
      <span className="menu-view-price">{formatCurrency(item.precio)}</span>
    </li>
  )
}
