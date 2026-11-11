import { canAccessRoute, matchRoute } from './app/routes'
import { useHashRoute } from './app/useHashRoute'
import { AppLayout } from './layout/AppLayout'
import { NotFoundPage } from './features/NotFoundPage'
import { ForbiddenPage } from './features/ForbiddenPage'
import { LoginPage } from './features/auth/LoginPage'
import { useAuth } from './auth/useAuth'

export default function App() {
  const path = useHashRoute()
  const auth = useAuth()

  if (auth.loading) {
    return <main className="auth-page"><p className="muted">Cargando sesión...</p></main>
  }
  if (!auth.user) {
    return <LoginPage />
  }

  const match = matchRoute(path)
  const content = !match
    ? <NotFoundPage />
    : canAccessRoute(match.route, auth.user.rol)
      ? match.route.render(match.params)
      : <ForbiddenPage />

  return (
    <AppLayout activePath={path} user={auth.user} onLogout={auth.logout}>
      {content}
    </AppLayout>
  )
}
