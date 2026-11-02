# Código legacy y archivos sin uso

Este documento lista el código que quedó en desuso o que está pendiente de migración.
**No se eliminó ningún archivo**: la idea es dejar registrado qué podría borrarse en una limpieza futura.

Ningún archivo del código actual (`src/App.tsx`, `src/main.tsx`, `src/app/`, `src/features/`, `src/layout/`, `src/ui/ui.tsx` ni `src/utils/`) importa los módulos de esta lista.

## Cliente HTTP legacy

- `Frontend/src/api.ts`
  - Cliente HTTP anterior (`api<T>`, `ApiError`) con su propio `fetch` y variable `VITE_API_URL`.
  - Fue reemplazado por `Frontend/src/api/client.ts` (`apiFetch`, `getErrorMessage`, `getFieldErrors`) y la variable `VITE_API_BASE_URL`.
  - Solamente lo importan archivos dentro de `Frontend/src/pages/`.

## Pantallas legacy: `Frontend/src/pages/`

Ninguna de estas pantallas está ruteada por `Frontend/src/App.tsx` ni por `Frontend/src/app/routes.tsx`.
Las pantallas reales viven en `Frontend/src/features/`.

- `Comandas.tsx`
  - Reemplazada por `Frontend/src/features/orders/OrdersListPage.tsx` y `OrderFormPage.tsx`.
- `ComandaDetalle.tsx`
  - Reemplazada por `Frontend/src/features/orders/OrderDetailPage.tsx` y sus hooks.
- `Inicio.tsx`
  - Reemplazada por `Frontend/src/features/dashboard/DashboardPage.tsx`.
- `Facturas.tsx` y `FacturaDetalle.tsx`
  - No están ruteadas. La facturación todavía vive en el esqueleto demo de `features/billing`.
- `MediosPago.tsx`
  - Reemplazada por `Frontend/src/features/payment-methods/`.
- `NoEncontrada.tsx`
  - Reemplazada por `Frontend/src/features/NotFoundPage.tsx`.

## UI legacy

- `Frontend/src/ui.tsx`
  - Sistema de UI anterior. Ya no lo importa ningún archivo del código actual.
  - `ToastProvider` fue movido a `Frontend/src/ui/ToastProvider.tsx`.
  - El contexto y el hook de avisos fueron movidos a `Frontend/src/ui/toastContext.ts`.
  - Los componentes y helpers restantes de este archivo quedaron sin uso.
- `Frontend/src/index.css`
  - No se importa desde `main.tsx`.
  - Los estilos de avisos flotantes que se seguían usando fueron movidos a `Frontend/src/ui/ui.css`.

## Datos de demostración

- `Frontend/src/features/orders/demo.ts`
  - Ya no lo usa la feature de comandas ni el dashboard.
  - El dashboard tiene su propia copia en `Frontend/src/features/dashboard/ordersDemo.ts`.

## Dependencias relacionadas

- `react-router-dom` quedó usado únicamente por las pantallas legacy de `src/pages/`.
  La aplicación actual no usa `BrowserRouter`; navega por hash mediante `src/app/navigation.ts`.
  No quitar la dependencia mientras existan esos archivos legacy.
