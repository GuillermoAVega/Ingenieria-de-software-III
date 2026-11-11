import { Breadcrumb, Button, Card, EmptyState, PageHeader } from '../../ui/ui'
import { DEMO_REPORTS } from './demo'
import { PaymentMethodReport } from './PaymentMethodReport'
import { ProductSalesReport } from './ProductSalesReport'
import { SalesComparisonReport } from './SalesComparisonReport'
import { SalesCountReport } from './SalesCountReport'
import { WaiterOrderReport } from './WaiterOrderReport'
import { AbsentClientsReport } from './AbsentClientsReport'
import { OccupancyBySectorReport } from './OccupancyBySectorReport'

export function ReportDetailPage({ slug }: { slug: string }) {
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
  return (
    <>
      <PageHeader
        breadcrumb={<Breadcrumb items={[{ label: 'Reportes', href: '#/reportes' }, { label: report.title }]} />}
        title={report.title}
        subtitle={report.description}
        actions={
          <Button variant="primary" onClick={() => window.print()}>
            Exportar PDF
          </Button>
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
      ) : report.slug === 'reservas' ? (
        <AbsentClientsReport />
      ) : report.slug === 'ocupacion' ? (
        <OccupancyBySectorReport />
      ) : (
        <PaymentMethodReport />
      )}
    </>
  )
}
