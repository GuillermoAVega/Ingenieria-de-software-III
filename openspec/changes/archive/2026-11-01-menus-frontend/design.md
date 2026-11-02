# Diseño: Menús en el frontend

## Decisiones

1. **Detalle enriquecido sólo para GET**: `ProductoMenuDetalleRespuesta` agrega `producto_nombre`, `producto_tipo` y `producto_dado_de_baja` mediante `validation_alias=AliasPath("producto", ...)`. `ProductoMenuRespuesta` (alta y modificación) no cambia, preservando PMD-03.
2. **Listado de menús del día**: todas las fechas, orden `fecha DESC`, sin filtros; el frontend filtra en memoria por producto, tipo o fecha. Incluye menús de productos dados de baja.
3. **Listado de menús ejecutivos**: reutiliza `services.listar`, por lo que hereda el filtro de activos y el orden por `id`; no requiere esquema nuevo.
4. **Nombres de componentes**: el frontend resuelve `plato_id`/`postre_id` con los listados activos de platos y postres. Un menú activo siempre tiene componentes activos (el backend lo garantiza), por lo que no quedan ids sin resolver.
5. **Navegación**: `/menus` es la entrada del grupo CARTA; las altas y ediciones viven en rutas propias. `/menu-del-dia/nuevo` se conserva como alias de `/menus/dia/nuevo`.
6. **Edición sin cambio de producto**: en la edición del menú del día el producto se muestra de sólo lectura; sólo se envía `{fecha}` al PUT.
7. **Menús ejecutivos**: la baja de la UI usa el DELETE existente (baja lógica). El formulario reutiliza los listados de platos, postres y secciones.

## Backend

- `schemas.py`: `ProductoMenuDetalleRespuesta` con seis campos.
- `services.py`: `listar_productos_menu` con `selectinload` y `fecha.desc()`.
- `productos_menu/router.py`: `GET ""` y `GET "/{id:int}"`.
- `menus_ejecutivos/router.py`: `GET ""` con `list[MenuRespuesta]`.

## Frontend

- `features/menus/MenusPage.tsx`: pestañas y composición.
- `features/daily-menu/`: `api.ts` completo, `useDailyMenusList`, `DailyMenusTab`, `useDailyMenuForm` con edición y `DailyMenuFormPage` con `id`.
- `features/executive-menus/`: `api.ts`, `useExecutiveMenusList`, `ExecutiveMenusTab`, `useExecutiveMenuForm`, `ExecutiveMenuFormPage`.
- `features/menus/format.ts`: etiquetas de tipo y formatos de fecha y moneda sin corrimiento UTC.

## Pruebas

- `Backend/tests/productos_menu/test_router_listado.py`: PMD-41 a PMD-47.
- `Backend/tests/productos/menus_ejecutivos/test_router_listado.py`: CAT-S-29 a CAT-S-32.
- Verificación del frontend: `npm run build` y `npm run lint`.
