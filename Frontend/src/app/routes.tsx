import type { ReactNode } from 'react'
import { normalizePath } from './navigation'
import { DashboardPage } from '../features/dashboard/DashboardPage'
import { OrdersListPage } from '../features/orders/OrdersListPage'
import { OrderDetailPage } from '../features/orders/OrderDetailPage'
import { OrderFormPage } from '../features/orders/OrderFormPage'
import { ReservationsListPage } from '../features/reservations/ReservationsListPage'
import { ReservationFormPage } from '../features/reservations/ReservationFormPage'
import { ReservationDetailPage } from '../features/reservations/ReservationDetailPage'
import { BillingListPage } from '../features/billing/BillingListPage'
import { ProductsListPage } from '../features/products/ProductsListPage'
import { ProductFormPage } from '../features/products/ProductFormPage'
import { SectionsListPage } from '../features/sections/SectionsListPage'
import { SectionFormPage } from '../features/sections/SectionFormPage'
import { PromotionsListPage } from '../features/promotions/PromotionsListPage'
import { PromotionFormPage } from '../features/promotions/PromotionFormPage'
import { TablesAndSectorsPage } from '../features/tables/TablesAndSectorsPage'
import { SectorFormPage } from '../features/tables/SectorFormPage'
import { TableFormPage } from '../features/tables/TableFormPage'
import { WaitersListPage } from '../features/waiters/WaitersListPage'
import { WaiterFormPage } from '../features/waiters/WaiterFormPage'
import { WaiterAttentionsPage } from '../features/waiters/WaiterAttentionsPage'
import { CustomersListPage } from '../features/customers/CustomersListPage'
import { CustomerFormPage } from '../features/customers/CustomerFormPage'
import { PaymentMethodsListPage } from '../features/payment-methods/PaymentMethodsListPage'
import { PaymentMethodFormPage } from '../features/payment-methods/PaymentMethodFormPage'
import { ReportsPage } from '../features/reports/ReportsPage'
import { ReportDetailPage } from '../features/reports/ReportDetailPage'

export type RouteParams = Record<string, string>

export type NavMeta = {
  group: string
  label: string
}

export type RouteDefinition = {
  path: string
  nav?: NavMeta
  render: (params: RouteParams) => ReactNode
}

export type NavItem = {
  text: string
  href: string
  active: boolean
}

export type NavGroup = {
  label: string
  items: NavItem[]
}

export type MatchedRoute = {
  route: RouteDefinition
  params: RouteParams
}

export const routes: RouteDefinition[] = [
  {
    path: '/',
    nav: { group: 'OPERACIÓN', label: 'Inicio' },
    render: () => <DashboardPage />,
  },
  {
    path: '/comandas',
    nav: { group: 'OPERACIÓN', label: 'Comandas' },
    render: () => <OrdersListPage />,
  },
  {
    path: '/comandas/nueva',
    render: () => <OrderFormPage />,
  },
  {
    path: '/comandas/:id',
    render: (params) => <OrderDetailPage id={params.id} />,
  },
  {
    path: '/reservas',
    nav: { group: 'OPERACIÓN', label: 'Reservas' },
    render: () => <ReservationsListPage />,
  },
  {
    path: '/reservas/nueva',
    render: () => <ReservationFormPage />,
  },
  {
    path: '/reservas/:id',
    render: (params) => <ReservationDetailPage id={params.id} />,
  },
  {
    path: '/reservas/:id/editar',
    render: (params) => <ReservationFormPage id={params.id} />,
  },
  {
    path: '/facturacion',
    nav: { group: 'OPERACIÓN', label: 'Facturación' },
    render: () => <BillingListPage />,
  },
  {
    path: '/productos',
    nav: { group: 'CARTA', label: 'Productos' },
    render: () => <ProductsListPage />,
  },
  {
    path: '/productos/nuevo',
    render: () => <ProductFormPage />,
  },
  {
    path: '/productos/:id/editar',
    render: (params) => <ProductFormPage id={params.id} />,
  },
  {
    path: '/secciones',
    nav: { group: 'CARTA', label: 'Secciones' },
    render: () => <SectionsListPage />,
  },
  {
    path: '/secciones/nueva',
    render: () => <SectionFormPage />,
  },
  {
    path: '/secciones/:id/editar',
    render: (params) => <SectionFormPage id={params.id} />,
  },
  {
    path: '/promociones',
    nav: { group: 'CARTA', label: 'Promociones' },
    render: () => <PromotionsListPage />,
  },
  {
    path: '/promociones/nueva',
    render: () => <PromotionFormPage />,
  },
  {
    path: '/promociones/:id/editar',
    render: (params) => <PromotionFormPage id={params.id} />,
  },
  {
    path: '/mesas',
    nav: { group: 'SALÓN', label: 'Mesas y sectores' },
    render: () => <TablesAndSectorsPage />,
  },
  {
    path: '/mesas/sectores/nuevo',
    render: () => <SectorFormPage />,
  },
  {
    path: '/mesas/sectores/:id/editar',
    render: (params) => <SectorFormPage id={params.id} />,
  },
  {
    path: '/mesas/nueva',
    render: () => <TableFormPage />,
  },
  {
    path: '/mesas/:id/editar',
    render: (params) => <TableFormPage id={params.id} />,
  },
  {
    path: '/mozos',
    nav: { group: 'SALÓN', label: 'Mozos' },
    render: () => <WaitersListPage />,
  },
  {
    path: '/mozos/nuevo',
    render: () => <WaiterFormPage />,
  },
  {
    path: '/mozos/:id/atenciones',
    render: (params) => <WaiterAttentionsPage key={params.id} id={params.id} />,
  },
  {
    path: '/mozos/:id/editar',
    render: (params) => <WaiterFormPage id={params.id} />,
  },
  {
    path: '/clientes',
    nav: { group: 'SALÓN', label: 'Clientes' },
    render: () => <CustomersListPage />,
  },
  {
    path: '/clientes/nuevo',
    render: () => <CustomerFormPage />,
  },
  {
    path: '/clientes/:id/editar',
    render: (params) => <CustomerFormPage id={params.id} />,
  },
  {
    path: '/medios-de-pago',
    nav: { group: 'ADMINISTRACIÓN', label: 'Medios de pago' },
    render: () => <PaymentMethodsListPage />,
  },
  {
    path: '/medios-de-pago/nuevo',
    render: () => <PaymentMethodFormPage />,
  },
  {
    path: '/medios-de-pago/:id/editar',
    render: (params) => <PaymentMethodFormPage id={params.id} />,
  },
  {
    path: '/reportes',
    nav: { group: 'ADMINISTRACIÓN', label: 'Reportes' },
    render: () => <ReportsPage />,
  },
  {
    path: '/reportes/:slug',
    render: (params) => <ReportDetailPage slug={params.slug} />,
  },
]

function isActive(routePath: string, activePath: string): boolean {
  if (routePath === '/') return activePath === '/'
  return activePath === routePath || activePath.startsWith(`${routePath}/`)
}

export function buildNav(activePath: string): NavGroup[] {
  const groups: NavGroup[] = []
  const normalizedActivePath = normalizePath(activePath)

  for (const route of routes) {
    const nav = route.nav
    if (!nav) continue

    let group = groups.find((candidate) => candidate.label === nav.group)
    if (!group) {
      group = { label: nav.group, items: [] }
      groups.push(group)
    }

    group.items.push({
      text: nav.label,
      href: `#${route.path}`,
      active: isActive(route.path, normalizedActivePath),
    })
  }

  return groups
}

function matchPath(pattern: string, path: string): RouteParams | null {
  const patternParts = pattern.split('/').filter(Boolean)
  const pathParts = path.split('/').filter(Boolean)

  if (patternParts.length !== pathParts.length) return null

  const params: RouteParams = {}

  for (let index = 0; index < patternParts.length; index += 1) {
    const patternPart = patternParts[index]
    const pathPart = pathParts[index]

    if (patternPart.startsWith(':')) {
      params[patternPart.slice(1)] = decodeURIComponent(pathPart)
    } else if (patternPart !== pathPart) {
      return null
    }
  }

  return params
}

export function matchRoute(path: string): MatchedRoute | null {
  const normalizedPath = normalizePath(path)

  for (const route of routes) {
    const params = matchPath(route.path, normalizedPath)
    if (params) {
      return { route, params }
    }
  }

  return null
}
