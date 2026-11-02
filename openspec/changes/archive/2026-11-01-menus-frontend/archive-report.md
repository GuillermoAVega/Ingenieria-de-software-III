# Reporte de archivo: menus-frontend

## Resultado

Cambio implementado y archivado el 2026-11-01.

- **Backend**: `GET /productos-menu` (fecha descendente, detalle con producto resuelto), `GET /productos-menu/{id}` y `GET /productos/menus-ejecutivos` (sólo activos, orden por id).
- **Frontend**: pestaña "Menús" en CARTA con "Menú del día" (listado, alta, edición de fecha y borrado) y "Menú ejecutivo" (listado, alta, edición y baja lógica).
- **Specs fusionadas**: `openspec/specs/daily-menu-management/spec.md` (PMD-41 a PMD-47) y `openspec/specs/product-catalog/spec.md` (CAT-S-29 a CAT-S-32).
- **Rutas nuevas**: `/menus`, `/menus/dia/nuevo`, `/menus/dia/:id/editar`, `/menus/ejecutivos/nuevo`, `/menus/ejecutivos/:id/editar`. `/menu-del-dia/nuevo` queda como alias.

## Verificación

- `cd Backend && python -m pytest`: 858 pruebas pasan y 1 falla por entorno (`test_main_carga_el_registro_de_modelos_por_si_solo` ejecuta un subproceso con `PATH` vacío y Windows devuelve `WinError 10106` al importar `asyncio`; no está relacionada con este cambio).
- `cd Frontend && npm run build`: correcto.
- `cd Frontend && npm run lint`: correcto.

## Pendientes conocidos

- Los listados no tienen paginación ni filtros de servidor (filtro en memoria en el frontend).
- El historial de menús ejecutivos dados de baja no se expone.
