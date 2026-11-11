import type { ReactNode } from 'react'
import { buildNav } from '../app/routes'
import { AppShell } from '../ui/ui'
import type { AuthUser } from '../auth/types'

function getInitials(name: string): string {
  return name.split(/\s+/).slice(0, 2).map((part) => part[0]).join('').toUpperCase()
}

export function AppLayout({
  activePath,
  user,
  onLogout,
  children,
}: {
  activePath: string
  user: AuthUser
  onLogout: () => void
  children: ReactNode
}) {
  return (
    <AppShell
      nav={buildNav(activePath, user.rol)}
      user={{
        name: user.nombre,
        role: user.rol === 'administrador' ? 'Administrador' : 'Operario',
        initials: getInitials(user.nombre),
      }}
      onLogout={onLogout}
    >
      {children}
    </AppShell>
  )
}
