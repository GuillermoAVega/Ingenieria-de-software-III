# Propuesta: Menús en el frontend (menú del día y menú ejecutivo)

## Intención

El frontend sólo permite crear un menú del día y no permite ver, modificar ni eliminar menús. Tampoco permite crear menús ejecutivos, que son productos compuestos por un plato y un postre. Se agrega la pestaña "Menús" en el grupo CARTA con la gestión de ambas entidades, y los endpoints de listado que faltan.

## Alcance

### Dentro del alcance
- `GET /productos-menu` (listado, fecha descendente) y `GET /productos-menu/{id}` con detalle enriquecido: `producto_nombre`, `producto_tipo`, `producto_dado_de_baja`.
- `GET /productos/menus-ejecutivos` (sólo activos, orden por id ascendente) reutilizando `MenuRespuesta`.
- Frontend:
  - Pestaña "Menús" en CARTA con sub-pestañas "Menú del día" y "Menú ejecutivo".
  - Listado, alta, edición de fecha y borrado de menús del día.
  - Listado, alta, edición y baja lógica de menús ejecutivos (plato + postre, sin fecha).
- Pruebas de backend para los endpoints nuevos.

### Fuera del alcance
- Cambio de `producto_id` de un menú del día.
- Filtros o paginación en los listados.
- Listado de combos y parámetro `?incluir_bajas`.
- Historial de menús ejecutivos dados de baja (el listado sólo devuelve activos).

## Capacidades

### Capacidades modificadas
- `daily-menu-management`: agrega listado y consulta por id.
- `product-catalog`: agrega el listado de menús ejecutivos activos.

## Enfoque

Los `GET` de menú del día usan un esquema de detalle exclusivo (`ProductoMenuDetalleRespuesta`) con `AliasPath` sobre la relación `producto`, y el servicio lista con `selectinload` y orden descendente. El listado de menús ejecutivos reutiliza `services.listar`, igual que platos, bebidas y postres. En el frontend, cada feature mantiene un único objeto de estado y su hook; la página de Menús sólo compone pestañas.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `Backend/src/productos_menu/` | Modificado | Esquema de detalle, servicio y rutas GET |
| `Backend/src/productos/menus_ejecutivos/router.py` | Modificado | Ruta GET de listado |
| `Backend/tests/productos_menu/`, `Backend/tests/productos/menus_ejecutivos/` | Nuevo | Pruebas de listado |
| `Frontend/src/features/daily-menu/` | Modificado | Listado, edición y baja |
| `Frontend/src/features/executive-menus/` | Nuevo | Feature de menús ejecutivos |
| `Frontend/src/features/menus/` | Nuevo | Página con pestañas y formatos |
| `Frontend/src/app/routes.tsx` | Modificado | Rutas y navegación |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Romper el contrato de alta/modificación (PMD-03) | Baja | Esquema de detalle separado, exclusivo de los GET |
| N+1 al serializar el producto del menú | Media | `selectinload` en el servicio de listado |

## Criterios de éxito

- [x] `GET /productos-menu` y `GET /productos-menu/{id}` responden con el detalle acordado.
- [x] `GET /productos/menus-ejecutivos` lista sólo activos, ordenados por id.
- [x] La pestaña Menús permite gestionar ambas entidades.
- [x] Suite de pytest y `npm run build` / `npm run lint` en verde.
