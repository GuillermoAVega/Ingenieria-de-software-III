/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Consulta de la carta del restaurante
 */
import { Alert, Button, Card, EmptyState, PageHeader } from '../../ui/ui'
import { formatDate } from '../../utils/format'
import { MenuCover } from './components/MenuCover'
import { MenuSectionFrame } from './components/MenuSectionFrame'
import { PrintablePages } from './components/PrintablePages'
import { sectionKey } from './pagination'
import { useMenuView } from './useMenuView'
import { useMenuViewPrint } from './useMenuViewPrint'

export function MenuViewPage() {
  const { state, sections } = useMenuView()
  const { state: printState, print, measureRef, measurePages } = useMenuViewPrint(sections)

  const isPrinting = printState.phase === 'printing'
  const isPreparing = printState.phase !== 'idle'

  return (
    <>
      <PageHeader
        title="Ver carta"
        subtitle={`Carta vigente al ${formatDate(state.date)}.`}
        actions={
          <Button variant="primary" onClick={print} disabled={isPreparing || state.loading}>
            {isPreparing ? 'Preparando PDF…' : 'Descargar PDF'}
          </Button>
        }
      />

      {state.error && (
        <Alert tone="danger" title="No se pudo cargar la carta">
          {state.error}
        </Alert>
      )}

      {printState.error && (
        <Alert tone="danger" title="No se pudo preparar el PDF">
          {printState.error}
        </Alert>
      )}

      {state.loading ? (
        <p className="muted">Cargando carta...</p>
      ) : (
        <div className={`menu-view${isPrinting ? ' menu-view--print' : ''}`}>
          <MenuCover />

          {isPrinting && printState.pages ? (
            <PrintablePages pages={printState.pages} />
          ) : sections.length > 0 ? (
            sections.map((section) => (
              <div className="menu-view-category" key={section.id}>
                <MenuSectionFrame
                  partKey={sectionKey(section.id)}
                  title={section.nombre}
                  subtitle={section.subtitulo}
                  items={section.items}
                  showTitle
                />
              </div>
            ))
          ) : (
            <Card flush>
              <EmptyState title="Sin elementos en la carta">
                Todavía no hay productos o menús con sección cargados.
              </EmptyState>
            </Card>
          )}
        </div>
      )}

      {measurePages && (
        <div
          ref={measureRef}
          className="menu-view menu-view--print menu-view--measure"
          aria-hidden="true"
        >
          <PrintablePages pages={measurePages} />
        </div>
      )}
    </>
  )
}
