import { matchRoute } from './app/routes'
import { useHashRoute } from './app/useHashRoute'
import { AppLayout } from './layout/AppLayout'
import { NotFoundPage } from './features/NotFoundPage'

export default function App() {
  const path = useHashRoute()
  const match = matchRoute(path)

  return (
    <AppLayout activePath={path}>
      {match ? match.route.render(match.params) : <NotFoundPage />}
    </AppLayout>
  )
}
