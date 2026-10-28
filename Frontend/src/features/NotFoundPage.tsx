/**
 * EQUIPO: Transversal
 * FUNCIONALIDAD: Página no encontrada
 * COMPLETAR:
 * 1. Revisar el mapa de rutas si esta pantalla aparece desde un enlace válido.
 */
import { Button, Card, EmptyState, PageHeader } from '../ui/ui'
import { navigate } from '../app/navigation'

export function NotFoundPage() {
  return (
    <>
      <PageHeader title="404" subtitle="La página que buscás no existe." />
      <Card>
        <EmptyState
          title="No encontramos esta pantalla"
          action={
            <Button variant="primary" onClick={() => navigate('/')}>
              Volver al inicio
            </Button>
          }
        >
          Revisá la dirección o volvé al panel principal.
        </EmptyState>
      </Card>
    </>
  )
}
