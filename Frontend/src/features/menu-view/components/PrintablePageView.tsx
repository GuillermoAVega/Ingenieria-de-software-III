import type { PrintablePage } from '../pagination'
import { MenuSectionFrame } from './MenuSectionFrame'

export function PrintablePageView({ page }: { page: PrintablePage }) {
  return (
    <div className="menu-view-page">
      {page.blocks.map((block) => (
        <div className="print-block" key={block.key} data-print-section-block>
          <MenuSectionFrame
            partKey={block.measureKey}
            title={block.name}
            subtitle={block.subtitle}
            items={block.items}
            showTitle={block.showTitle}
            breakable={block.breakable}
          />
        </div>
      ))}
    </div>
  )
}
