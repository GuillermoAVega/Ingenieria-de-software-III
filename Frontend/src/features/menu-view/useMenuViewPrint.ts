import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { paginateMenu, toPrintableBlocks } from './pagination'
import type { PrintMeasurements, PrintablePage } from './pagination'
import type { MenuViewSectionGroup } from './types'

type PrintPhase = 'idle' | 'measuring' | 'printing'

type PrintState = {
  phase: PrintPhase
  pages: PrintablePage[] | null
  error: string | null
}

const PRINT_ERROR = 'No se pudo preparar la impresión. Intentá de nuevo.'

function parsePx(value: string) {
  const parsed = Number.parseFloat(value)
  return Number.isFinite(parsed) ? parsed : 0
}

/**
 * Lee las alturas reales del clon oculto con el mismo layout que la impresión.
 * Todos los bloques usan padding (sin márgenes), así el alto de la página es la
 * suma exacta de los bloques y no hay colapso de márgenes.
 */
function collectMeasurements(root: HTMLElement): PrintMeasurements {
  const itemHeights: Record<string, number> = {}
  root.querySelectorAll<HTMLElement>('[data-print-item]').forEach((element) => {
    const key = element.dataset.printItem
    if (!key) return
    itemHeights[key] = element.getBoundingClientRect().height
  })

  const sectionTitleHeights: Record<string, number> = {}
  root.querySelectorAll<HTMLElement>('[data-print-section-title]').forEach((element) => {
    const key = element.dataset.printSectionTitle
    if (!key) return
    sectionTitleHeights[key] = element.getBoundingClientRect().height
  })

  let sectionFrameExtra = 0
  const frame = root.querySelector<HTMLElement>('[data-print-section-frame]')
  const frameBlock = root.querySelector<HTMLElement>('[data-print-section-block]')
  if (frame && frameBlock) {
    const frameStyle = window.getComputedStyle(frame)
    const blockStyle = window.getComputedStyle(frameBlock)
    sectionFrameExtra =
      parsePx(frameStyle.paddingTop) +
      parsePx(frameStyle.paddingBottom) +
      parsePx(frameStyle.borderTopWidth) +
      parsePx(frameStyle.borderBottomWidth) +
      parsePx(blockStyle.paddingBottom)
  }

  return {
    itemHeights,
    sectionTitleHeights,
    sectionFrameExtra,
  }
}

export function useMenuViewPrint(sections: MenuViewSectionGroup[]) {
  const [state, setState] = useState<PrintState>({ phase: 'idle', pages: null, error: null })
  const measureRef = useRef<HTMLDivElement>(null)

  // Clon de medición: un único flujo de secciones sin partir.
  const measurePages = useMemo<PrintablePage[] | null>(
    () =>
      state.phase === 'measuring'
        ? [{ key: 'measure', blocks: toPrintableBlocks(sections) }]
        : null,
    [state.phase, sections],
  )

  const print = useCallback(() => {
    setState((previous) => {
      if (previous.phase !== 'idle') return previous
      if (sections.length === 0) {
        return { phase: 'idle', pages: null, error: 'La carta no tiene contenido para imprimir.' }
      }
      return { phase: 'measuring', pages: null, error: null }
    })
  }, [sections.length])

  useEffect(() => {
    if (state.phase !== 'measuring') return
    let cancelled = false

    async function prepare() {
      try {
        await document.fonts.ready
      } catch {
        // Si la API de fuentes falla, medimos igual con lo que haya.
      }
      if (cancelled) return

      const root = measureRef.current
      if (!root) {
        setState({ phase: 'idle', pages: null, error: PRINT_ERROR })
        return
      }

      try {
        const measurements = collectMeasurements(root)
        const pages = paginateMenu(sections, measurements)
        if (!cancelled) {
          setState({ phase: 'printing', pages, error: null })
        }
      } catch {
        if (!cancelled) setState({ phase: 'idle', pages: null, error: PRINT_ERROR })
      }
    }

    void prepare()
    return () => {
      cancelled = true
    }
  }, [state.phase, sections])

  useLayoutEffect(() => {
    if (state.phase !== 'printing') return
    let cancelled = false

    const frame = requestAnimationFrame(() => {
      if (cancelled) return
      window.print()
      if (!cancelled) setState({ phase: 'idle', pages: null, error: null })
    })

    // `afterprint` se dispara al cerrar el diálogo; el retorno de `print()` varía por navegador.
    const restore = () => setState({ phase: 'idle', pages: null, error: null })
    window.addEventListener('afterprint', restore)

    return () => {
      cancelled = true
      cancelAnimationFrame(frame)
      window.removeEventListener('afterprint', restore)
    }
  }, [state.phase])

  return { state, print, measureRef, measurePages }
}
