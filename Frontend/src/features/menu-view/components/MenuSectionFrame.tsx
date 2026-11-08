import type { MenuViewItem } from '../types'
import { MenuItemRow } from './MenuItemRow'

export type MenuSectionFrameProps = {
  partKey: string
  title: string
  subtitle?: string | null
  items: MenuViewItem[]
  showTitle: boolean
  breakable?: boolean
}

export function MenuSectionFrame({
  partKey,
  title,
  subtitle,
  items,
  showTitle,
  breakable = false,
}: MenuSectionFrameProps) {
  return (
    <div
      className={[
        'menu-view-section',
        !showTitle && 'menu-view-section--continuation',
        breakable && 'menu-view-section--breakable',
      ]
        .filter(Boolean)
        .join(' ')}
      data-print-section-frame
    >
      {showTitle && (
        <h3 className="menu-view-section-title" data-print-section-title={partKey}>
          <span>{title}</span>
          {subtitle && <small className="menu-view-description">{subtitle}</small>}
        </h3>
      )}
      <ul className="menu-view-items">
        {items.map((item) => (
          <MenuItemRow item={item} key={item.key} />
        ))}
      </ul>
    </div>
  )
}
