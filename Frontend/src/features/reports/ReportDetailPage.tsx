/**
 * EQUIPO: Administración
 * FUNCIONALIDAD: Detalle de un reporte
 * COMPLETAR:
 * 1. Reemplazar DEMO_PRODUCT_RANKING por la llamada a la API del reporte.
 * 2. Implementar los filtros Desde/Hasta y la exportación.
 * 3. Construir la visualización de cada slug restante.
 */
import { useState } from 'react'
import { BarRow, Breadcrumb, Button, Card, EmptyState, DateInput, Field, PageHeader } from '../../ui/ui'
import { DEMO_PRODUCT_RANKING, DEMO_REPORTS } from './demo'
import { SalesComparisonReport } from './SalesComparisonReport'

export function ReportDetailPage({ slug }: { slug: string }) {
  const [period, setPeriod] = useState({ from: '2026-10-01', to: '2026-10-16' })
  const report = DEMO_REPORTS.find((candidate) => candidate.slug === slug)

  if (!report) {
    return (
      <>
        <PageHeader
          breadcrumb={<Breadcrumb items={[{ label: 'Reportes', href: '#/reportes' }, { label: slug }]} />}
          title="Reporte no encontrado"
        />
        <Card>
          <EmptyState title="No encontramos este reporte">
            Revisá la dirección o volvé al índice de reportes.
          </EmptyState>
        </Card>
      </>
    )
  }

  const maxValue = Math.max(...DEMO_PRODUCT_RANKING.map((product) => product.value))

  return (
    <>
      <PageHeader
        breadcrumb={<Breadcrumb items={[{ label: 'Reportes', href: '#/reportes' }, { label: report.title }]} />}
        title={report.title}
        subtitle={report.description}
        actions={
          <Button
            variant="primary"
            onClick={() => {
              // TODO(equipo-administracion): exportar el reporte en el formato acordado.
            }}
          >
            Exportar
          </Button>
        }
      />

      {report.slug === 'comparativa-mensual' ? (
        <SalesComparisonReport />
      ) : (
        <>
          <Card title="Período">
            <div className="form-grid">
              <Field label="Desde">
                <DateInput value={period.from} onChange={(from) => setPeriod((previous) => ({ ...previous, from }))} />
              </Field>
              <Field label="Hasta">
                <DateInput value={period.to} onChange={(to) => setPeriod((previous) => ({ ...previous, to }))} />
              </Field>
            </div>
          </Card>

          {report.slug === 'productos' ? (
            <Card title="Productos más vendidos" subtitle="Unidades vendidas en el período seleccionado.">
              <div className="stack">
                {DEMO_PRODUCT_RANKING.map((product) => (
                  <BarRow key={product.id} label={product.name} value={product.value} max={maxValue} />
                ))}
              </div>
            </Card>
          ) : (
            <Card>
              <EmptyState title="Reporte en preparación">
                La visualización de este reporte todavía no está implementada.
                {/* TODO(equipo-administracion): construir la visualización de este reporte. */}
              </EmptyState>
            </Card>
          )}
        </>
      )}
    </>
  )
}
