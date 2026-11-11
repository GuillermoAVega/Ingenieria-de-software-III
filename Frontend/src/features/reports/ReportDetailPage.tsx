/**
 * EQUIPO: Administración
 * FUNCIONALIDAD: Detalle de un reporte
 * COMPLETAR:
 * 1. Implementar los filtros Desde/Hasta de los reportes restantes.
 * 2. Construir la visualización de cada slug restante.
 */
import { useState } from 'react'
import { Breadcrumb, Button, Card, EmptyState, DateInput, Field, PageHeader } from '../../ui/ui'
import { DEMO_REPORTS } from './demo'
import { ProductSalesReport } from './ProductSalesReport'
import { SalesComparisonReport } from './SalesComparisonReport'
import { SalesCountReport } from './SalesCountReport'
import { WaiterOrderReport } from './WaiterOrderReport'

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

  const isSales = report.slug === 'ventas'
  const canExport =
    isSales ||
    report.slug === 'comparativa-mensual' ||
    report.slug === 'comandas-mozo' ||
    report.slug === 'productos'

  return (
    <>
      <PageHeader
        breadcrumb={<Breadcrumb items={[{ label: 'Reportes', href: '#/reportes' }, { label: report.title }]} />}
        title={report.title}
        subtitle={report.description}
        actions={
          canExport ? (
            <Button variant="primary" onClick={() => window.print()}>
              Exportar PDF
            </Button>
          ) : undefined
        }
      />

      {report.slug === 'comparativa-mensual' ? (
        <SalesComparisonReport />
      ) : isSales ? (
        <SalesCountReport />
      ) : report.slug === 'comandas-mozo' ? (
        <WaiterOrderReport />
      ) : report.slug === 'productos' ? (
        <ProductSalesReport />
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

            <Card>
              <EmptyState title="Reporte en preparación">
                La visualización de este reporte todavía no está implementada.
                {/* TODO(equipo-administracion): construir la visualización de este reporte. */}
              </EmptyState>
            </Card>
        </>
      )}
    </>
  )
}
