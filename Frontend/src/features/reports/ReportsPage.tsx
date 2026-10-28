/**
 * EQUIPO: Administración
 * FUNCIONALIDAD: Índice de reportes
 * COMPLETAR:
 * 1. Reemplazar DEMO_REPORTS por la definición que exponga la API.
 * 2. Definir permisos y filtros disponibles para cada reporte.
 */
import { Button, Card, PageHeader } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { DEMO_REPORTS } from './demo'

export function ReportsPage() {
  return (
    <>
      <PageHeader
        title="Reportes"
        subtitle="Indicadores de operación, carta y salón para el cierre de la jornada."
      />

      <div className="grid-auto">
        {DEMO_REPORTS.map((report) => (
          <Card
            key={report.slug}
            title={report.title}
            footer={
              <Button onClick={() => navigate(`/reportes/${report.slug}`)}>Ver reporte</Button>
            }
          >
            <p className="muted">{report.description}</p>
          </Card>
        ))}
      </div>
    </>
  )
}
