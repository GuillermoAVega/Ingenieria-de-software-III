# Frontend

Base visual del sistema de gestión del restaurante. Cada funcionalidad vive en una carpeta dentro de `src/features/`. Las pantallas ya tienen estructura, datos de ejemplo y comentarios `TODO` que indican qué falta implementar.

## Levantar el proyecto

```bash
cd Frontend
npm install
npm run dev
```

Antes de abrir un PR:

```bash
npm run build
npm run lint
```

## Qué archivos toca cada equipo

| Funcionalidad | Ruta principal | Carpeta | Archivos que toca el equipo |
|---|---|---|---|
| Inicio / Dashboard | `#/` | `src/features/dashboard/` | `DashboardPage.tsx` |
| Comandas | `#/comandas` | `src/features/orders/` | `OrdersListPage.tsx`, `OrderDetailPage.tsx`, `OrderFormPage.tsx`, `demo.ts`, `types.ts` |
| Reservas | `#/reservas` | `src/features/reservations/` | `ReservationsListPage.tsx`, `ReservationFormPage.tsx`, `demo.ts`, `types.ts` |
| Facturación | `#/facturacion` | `src/features/billing/` | `BillingListPage.tsx`, `demo.ts`, `types.ts` |
| Productos | `#/productos` | `src/features/products/` | `ProductsListPage.tsx`, `ProductFormPage.tsx`, `demo.ts`, `types.ts` |
| Secciones | `#/secciones` | `src/features/sections/` | `SectionsListPage.tsx`, `SectionFormPage.tsx`, `demo.ts`, `types.ts` |
| Promociones | `#/promociones` | `src/features/promotions/` | `PromotionsListPage.tsx`, `PromotionFormPage.tsx`, `demo.ts`, `types.ts` |
| Mesas y sectores | `#/mesas` | `src/features/tables/` | `TablesAndSectorsPage.tsx`, `SectorFormPage.tsx`, `TableFormPage.tsx`, `demo.ts`, `types.ts` |
| Mozos | `#/mozos` | `src/features/waiters/` | `WaitersListPage.tsx`, `WaiterFormPage.tsx`, `WaiterAttentionsPage.tsx`, `api.ts`, `types.ts` |
| Clientes | `#/clientes` | `src/features/customers/` | `CustomersListPage.tsx`, `CustomerFormPage.tsx`, `demo.ts`, `types.ts` |
| Medios de pago | `#/medios-de-pago` | `src/features/payment-methods/` | `PaymentMethodsListPage.tsx`, `PaymentMethodFormPage.tsx`, `demo.ts`, `types.ts` |
| Reportes | `#/reportes` | `src/features/reports/` | `ReportsPage.tsx`, `ReportDetailPage.tsx`, `demo.ts`, `types.ts` |

## Cómo saber qué tocar

1. Buscá tu pantalla en la tabla de arriba.
2. Abrí esa carpeta en `src/features/`.
3. Los archivos `*Page.tsx` son las pantallas. `demo.ts` tiene datos falsos y `types.ts` los tipos.
4. Cada página empieza con un comentario que indica el equipo y los `TODO` pendientes.
5. Las rutas y el menú lateral están en `src/app/routes.tsx`; el `import` de cada ruta te dice qué archivo se muestra.

## Reglas rápidas

- Usá solo `src/ui/ui.tsx` y las clases de `src/ui/ui.css`.
- No crees CSS nuevo ni colores, radios o sombras sueltas.
- Reemplazá los datos `DEMO_*` por la API cuando esté disponible.
- Completá los `TODO(equipo-...)` de tu carpeta.
- Para eliminaciones usá `DeleteButton`.
- No modifiques la carpeta de otra feature sin acordarlo.
- Los cambios en `ui.tsx`, `ui.css` o `routes.tsx` los revisa el equipo base.
- Copy y comentarios en español; nombres de código en inglés.

## Archivos compartidos

No tocar sin coordinar:

- `src/ui/ui.tsx` y `src/ui/ui.css`: componentes y estilos base.
- `src/app/routes.tsx`: rutas y navegación.
- `src/layout/AppLayout.tsx`: estructura general.
- `src/App.tsx` y `src/main.tsx`: entrada de la aplicación.

## Rutas

Todas las rutas están declaradas en `src/app/routes.tsx`. Si tu equipo necesita una ruta nueva:

1. Agregá la entrada en `routes.tsx`.
2. Si debe aparecer en el menú, completá `nav: { group: '...', label: '...' }`.
3. Agregá tu página dentro de la carpeta de la feature correspondiente.
