import type { MenuViewItem, MenuViewSectionGroup } from './types'

/**
 * Geometría de la hoja usada por la impresión.
 * Debe coincidir con `@page { size: A4; margin: 12mm }` de `ui.css`.
 */
const MM_PER_INCH = 25.4
const CSS_PX_PER_INCH = 96
const A4_WIDTH_MM = 210
const A4_HEIGHT_MM = 297
const PAGE_MARGIN_MM = 12

export const PRINT_CONTENT_WIDTH_MM = A4_WIDTH_MM - PAGE_MARGIN_MM * 2
export const PRINT_CONTENT_HEIGHT_PX =
  ((A4_HEIGHT_MM - PAGE_MARGIN_MM * 2) * CSS_PX_PER_INCH) / MM_PER_INCH

/** Margen de seguridad para absorber redondeos de subpíxeles. */
const PRINT_SAFETY_PX = 16

export type PrintBlock = {
  kind: 'section'
  key: string
  measureKey: string
  name: string
  subtitle: string | null
  /** La primera parte de una sección lleva título; las continuaciones no. */
  showTitle: boolean
  /** Ítem más alto que una hoja: se deja partir por el navegador. */
  breakable: boolean
  items: MenuViewItem[]
}

export type PrintablePage = {
  key: string
  blocks: PrintBlock[]
}

/** Alturas medidas en el clon de impresión, en píxeles CSS. */
export type PrintMeasurements = {
  itemHeights: Record<string, number>
  sectionTitleHeights: Record<string, number>
  /** Padding + bordes del recuadro + espacio inferior del bloque de sección. */
  sectionFrameExtra: number
}

export function sectionKey(sectionId: number) {
  return `g-${sectionId}`
}

function sectionBlock(
  section: MenuViewSectionGroup,
  offset: number,
  items: MenuViewItem[],
  showTitle: boolean,
): PrintBlock {
  return {
    kind: 'section',
    key: `${sectionKey(section.id)}-${offset}`,
    measureKey: sectionKey(section.id),
    name: section.nombre,
    subtitle: section.subtitulo,
    showTitle,
    breakable: false,
    items,
  }
}

/**
 * Estructura imprimible sin partir, en un único flujo de secciones.
 * Se usa para medir el clon oculto y como respaldo si no hay mediciones.
 */
export function toPrintableBlocks(sections: MenuViewSectionGroup[]): PrintBlock[] {
  return sections.map((section) => sectionBlock(section, 0, section.items, true))
}

function createPaginator(pageBudget: number) {
  const pages: PrintablePage[] = [{ key: 'page-0', blocks: [] }]

  return {
    pages,
    y: 0,
    pageBudget,
    add(block: PrintBlock, height: number) {
      pages[pages.length - 1].blocks.push(block)
      this.y += height
    },
    newPage() {
      pages.push({ key: `page-${pages.length}`, blocks: [] })
      this.y = 0
    },
  }
}

type Paginator = ReturnType<typeof createPaginator>

function placeSection(
  paginator: Paginator,
  section: MenuViewSectionGroup,
  measurements: PrintMeasurements,
): void {
  const key = sectionKey(section.id)
  const titleHeight = measurements.sectionTitleHeights[key] ?? 0
  const frame = measurements.sectionFrameExtra
  const items = section.items
  const heights = items.map((item) => measurements.itemHeights[item.key])
  const measured = heights.every((height) => typeof height === 'number')

  if (!measured) {
    // Sin mediciones confiables no se parte: que decida el navegador dentro de la hoja.
    paginator.add(sectionBlock(section, 0, items, true), titleHeight + frame)
    return
  }

  let index = 0
  let firstPart = true

  while (index < items.length) {
    const overhead = (firstPart ? titleHeight : 0) + frame
    const available = paginator.pageBudget - paginator.y
    const restHeight = heights.slice(index).reduce((sum, height) => sum + height, 0)

    if (overhead + restHeight <= available) {
      paginator.add(
        sectionBlock(section, index, items.slice(index), firstPart),
        overhead + restHeight,
      )
      break
    }

    let fit = 0
    let used = 0
    const room = available - overhead
    while (index + fit < items.length && used + heights[index + fit] <= room) {
      used += heights[index + fit]
      fit += 1
    }

    if (fit > 0) {
      paginator.add(
        sectionBlock(section, index, items.slice(index, index + fit), firstPart),
        overhead + used,
      )
      index += fit
      firstPart = false
      // La sección continúa en la hoja siguiente.
      if (index < items.length) paginator.newPage()
      continue
    }

    // No entra ni un ítem: probar desde el inicio de una hoja.
    if (paginator.y > 0) {
      paginator.newPage()
      continue
    }

    // En una hoja vacía tampoco entra: el ítem es más alto que la hoja.
    const block = sectionBlock(section, index, [items[index]], firstPart)
    block.breakable = true
    paginator.add(block, overhead + heights[index])
    index += 1
    firstPart = false
    if (index < items.length) paginator.newPage()
  }
}

/**
 * Pagina la carta completa en hojas explícitas. Cada hoja se imprime con un
 * salto forzado, así el resultado no depende del empaquetado del navegador.
 */
export function paginateMenu(
  sections: MenuViewSectionGroup[],
  measurements: PrintMeasurements,
): PrintablePage[] {
  const pageBudget = PRINT_CONTENT_HEIGHT_PX - PRINT_SAFETY_PX
  const paginator = createPaginator(pageBudget)

  for (const section of sections) {
    placeSection(paginator, section, measurements)
  }

  return paginator.pages.filter((page) => page.blocks.length > 0)
}
