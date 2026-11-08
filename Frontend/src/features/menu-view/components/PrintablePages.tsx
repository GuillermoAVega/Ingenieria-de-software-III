import type { PrintablePage } from '../pagination'
import { PrintablePageView } from './PrintablePageView'

export function PrintablePages({ pages }: { pages: PrintablePage[] }) {
  return (
    <>
      {pages.map((page) => (
        <PrintablePageView page={page} key={page.key} />
      ))}
    </>
  )
}
