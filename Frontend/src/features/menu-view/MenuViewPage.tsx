/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Consulta de la carta del restaurante
 */
import { Alert, Button, PageHeader } from '../../ui/ui'
import { formatCurrency, formatDate } from '../../utils/format'
import { useMenuView } from './useMenuView'
import type { MenuViewCategory, MenuViewItem } from './types'

function MenuItemRow({ item }: { item: MenuViewItem }) {
  return (
    <li className="menu-view-item">
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

function MenuCategory({ category }: { category: MenuViewCategory }) {
  const hasSections = category.sectionGroups.length > 0

  return (
    <section className="menu-view-category" aria-labelledby={`menu-view-${category.id}`}>
      <h2 className="menu-view-category-title" id={`menu-view-${category.id}`}>
        {category.title}
      </h2>

      {hasSections &&
        category.sectionGroups.map((group) => (
          <div className="menu-view-section" key={group.id}>
            <h3 className="menu-view-section-title">
              <span>{group.nombre}</span>
              {group.subtitulo && (
                <small className="menu-view-description">{group.subtitulo}</small>
              )}
            </h3>
            <ul className="menu-view-items">
              {group.items.map((item) => (
                <MenuItemRow item={item} key={item.key} />
              ))}
            </ul>
          </div>
        ))}

      {category.unsectionedItems.length > 0 && (
        <div className={hasSections ? 'menu-view-section' : undefined}>
          {hasSections && <h3 className="menu-view-section-title">Sin sección</h3>}
          <ul className="menu-view-items">
            {category.unsectionedItems.map((item) => (
              <MenuItemRow item={item} key={item.key} />
            ))}
          </ul>
        </div>
      )}

      {!hasSections && category.unsectionedItems.length === 0 && (
        <p className="muted">No hay elementos disponibles.</p>
      )}
    </section>
  )
}

export function MenuViewPage() {
  const { state, categories } = useMenuView()

  const handleDownloadPdf = () => {
    window.print()
  }

  return (
    <>
      <PageHeader
        title="Ver carta"
        subtitle={`Carta vigente al ${formatDate(state.date)}.`}
        actions={
          <Button variant="primary" onClick={handleDownloadPdf}>
            Descargar PDF
          </Button>
        }
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo cargar la carta">
          {state.error}
        </Alert>
      )}

      {state.loading ? (
        <p className="muted">Cargando carta...</p>
      ) : (
        <div className="menu-view">
          <div className="menu-view-cover" aria-label="Carátula de la carta">
            <img className="menu-view-cover-logo" src="/logo.png" alt="Logo de Sabor de Mar" />
            <h1 className="menu-view-cover-title">Sabor de Mar</h1>
            <p className="menu-view-cover-subtitle">Carta del restaurante</p>
          </div>

          {categories
            .filter(
              (category) =>
                category.sectionGroups.length > 0 || category.unsectionedItems.length > 0,
            )
            .map((category) => (
              <MenuCategory category={category} key={category.id} />
            ))}
        </div>
      )}
    </>
  )
}
