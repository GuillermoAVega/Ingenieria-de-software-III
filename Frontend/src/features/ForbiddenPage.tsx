import { Button, Card, EmptyState } from '../ui/ui'
import { navigate } from '../app/navigation'

export function ForbiddenPage() {
  return (
    <Card>
      <EmptyState title="Acceso restringido">
        Tu usuario no tiene permisos para ingresar a esta sección.
        <div className="mt-4">
          <Button variant="primary" onClick={() => navigate('/')}>
            Volver al inicio
          </Button>
        </div>
      </EmptyState>
    </Card>
  )
}
