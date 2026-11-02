# Tareas: Menús en el frontend

Cambio: `menus-frontend`. Comando de pruebas: `cd Backend && python -m pytest`.

## Fase 1: Backend

- [x] **1.1 Listado y consulta de menús del día** — `Backend/src/productos_menu/{schemas,services,router}.py`; pruebas en `Backend/tests/productos_menu/test_router_listado.py` (PMD-41 a PMD-47).
- [x] **1.2 Listado de menús ejecutivos** — `Backend/src/productos/menus_ejecutivos/router.py`; pruebas en `Backend/tests/productos/menus_ejecutivos/test_router_listado.py` (CAT-S-29 a CAT-S-32).

## Fase 2: Frontend

- [x] **2.1 Feature de menús del día** — `api.ts`, `useDailyMenusList`, `DailyMenusTab`, `useDailyMenuForm` con edición y `DailyMenuFormPage` con `id`.
- [x] **2.2 Feature de menús ejecutivos** — `api.ts`, `useExecutiveMenusList`, `ExecutiveMenusTab`, `useExecutiveMenuForm` y `ExecutiveMenuFormPage`.
- [x] **2.3 Página de Menús, rutas y navegación** — `features/menus/MenusPage.tsx`, `format.ts`, `routes.tsx` y botón de Productos.

## Fase 3: Verificación

- [x] **3.1 Suite de backend** — `cd Backend && python -m pytest` en verde.
- [x] **3.2 Calidad del frontend** — `npm run build` y `npm run lint` en verde.
- [x] **3.3 Fusión de specs y archivo** — requisitos incorporados a `openspec/specs/daily-menu-management` y `openspec/specs/product-catalog`.
