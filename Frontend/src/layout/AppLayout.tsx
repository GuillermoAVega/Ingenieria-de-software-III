import type { ReactNode } from 'react'
import { buildNav } from '../app/routes'
import { AppShell } from '../ui/ui'

const DEMO_USER = {
  name: 'Administrador',
  role: 'Encargado de salón',
  initials: 'AD',
}

export function AppLayout({ activePath, children }: { activePath: string; children: ReactNode }) {
  return (
    <AppShell nav={buildNav(activePath)} user={DEMO_USER}>
      {children}
    </AppShell>
  )
}
