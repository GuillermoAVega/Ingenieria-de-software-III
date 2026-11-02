/**
 * EQUIPO: Carta
 * FUNCIONALIDAD: Menús del día y menús ejecutivos
 * Pestañas sobre listados; la lógica vive en cada hook de feature.
 */
import { useState } from 'react'
import { PageHeader, Tabs } from '../../ui/ui'
import { DailyMenusTab } from '../daily-menu/DailyMenusTab'
import { ExecutiveMenusTab } from '../executive-menus/ExecutiveMenusTab'

const TABS = [
  { id: 'dia', label: 'Menú del día' },
  { id: 'ejecutivos', label: 'Menú ejecutivo' },
] as const

type MenusTabId = (typeof TABS)[number]['id']

export function MenusPage() {
  const [activeTab, setActiveTab] = useState<MenusTabId>('dia')

  return (
    <>
      <PageHeader
        title="Menús"
        subtitle="Menús del día por fecha y menús ejecutivos compuestos por plato y postre."
      />

      <Tabs
        tabs={TABS.map((tab) => ({ ...tab }))}
        active={activeTab}
        onChange={(id) => setActiveTab(id as MenusTabId)}
      />

      {activeTab === 'dia' ? <DailyMenusTab /> : <ExecutiveMenusTab />}
    </>
  )
}
