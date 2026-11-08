# Exploración: menu-del-dia-producto

## Resumen ejecutivo

Reemplazar `ProductoMenu(producto_id → producto)` por un subtipo `MenuDelDia(Producto)` sin campos propios y una tabla de fechas `ProductoMenu(menu_del_dia_id → menu_del_dia, fecha UNIQUE)`. El cambio de backend es acotado y mecánico. El frontend consume `/productos-menu` y deja de funcionar si cambia el contrato. La base `app.db` existente requiere reinicio o migración manual.

## Decisiones de producto confirmadas

1. Se elimina la implementación actual de menú del día y se reformula.
2. `MenuDelDia` es un nuevo subtipo de `Producto` (herencia por tablas unidas), distinto de `MenuEjecutivo` y coexistente con él.
3. Objetivo: no duplicar un mismo producto (por ejemplo, "Milanesa") por cada fecha.
4. `ProductoMenu` registra cuándo un `MenuDelDia` fue menú del día: `id`, `menu_del_dia_id` (FK NOT NULL → `menu_del_dia`), `fecha`. Un `MenuDelDia` tiene 0..N `ProductoMenu`; cada `ProductoMenu` pertenece exactamente a un `MenuDelDia`.
5. `fecha` se mantiene única (un menú del día por fecha).

## Estado actual (`Backend/src/productos_menu/`)

- `models.py`: `ProductoMenu` (tabla `producto_menu`): `id`, `producto_id` FK → `producto.id` NOT NULL indexada, `fecha` Date; índice único `ux_producto_menu_fecha`; `relationship("Producto", back_populates="menus_del_dia")`.
- `schemas.py`: `ProductoMenuCrear{producto_id, fecha}`, `ProductoMenuActualizar{fecha}`, `ProductoMenuRespuesta{id, producto_id, fecha}`, `ProductoMenuDetalleRespuesta` (agrega `producto_nombre`, `producto_tipo`, `producto_dado_de_baja` vía `AliasPath`).
- `services.py`: `obtener`, `listar` (fecha descendente, `selectinload`), `crear`, `actualizar_fecha`, `eliminar` (borrado físico); `_verificar_producto_activo`, `_verificar_fecha_libre`, `_confirmar` (traduce `IntegrityError` a 409). Prioridad en el alta: inexistente (422) → dado de baja (409) → fecha ocupada (409).
- `exceptions.py`: `ErrorProductoMenu`, `ProductoInexistente`, `ProductoDadoDeBaja`, `FechaMenuOcupada`, `ProductoMenuNoEncontrado`.
- `router.py`: `PREFIJO="/productos-menu"`; GET lista, GET `/{id}`, POST 201, PUT (solo fecha), DELETE 204; `MANEJADORES_EXCEPCIONES`.
- Cableado: `Backend/src/main.py` (router y manejadores), `Backend/src/productos/registro.py` (importa `ProductoMenu`), `Backend/src/productos/models.py` (`Producto.menus_del_dia`).

## Subtipos de producto

- Cada subtipo vive en `Backend/src/productos/<paquete>/` con `models`, `schemas`, `services`, `router`, `constants` y `exceptions`. Ejemplo mínimo: `postres/`.
- Modelo: `class Postre(Producto)` con `__tablename__`, `id = mapped_column(ForeignKey("producto.id"), primary_key=True)` y `polymorphic_identity`.
- `registro.py` define `MODELOS_POR_TIPO` (5 tipos) y `RESTRICT_POR_TIPO` (plato, postre y bebida como componentes que bloquean la baja). Un `MenuDelDia` no necesita entrada en `RESTRICT_POR_TIPO`.
- Los routers de subtipo se incluyen en `productos/router.py` y usan los servicios genéricos (`crear_producto`, `listar`, `obtener`, `dar_de_baja`, `actualizar_producto`).

## Qué requiere `MenuDelDia`

- Sin campos propios obligatorios; tabla `menu_del_dia` solo con `id` FK.
- Paquete nuevo `Backend/src/productos/menus_del_dia/` (`PREFIJO="/menus-del-dia"`).
- Cambios en `productos/constants.py` (`TIPO_MENU_DEL_DIA="menu_del_dia"`), `registro.py`, `productos/router.py` y la relación `Producto.menus_del_dia`, que pasa a `MenuDelDia.fechas`.
- `ProductoMenu.menu_del_dia_id` FK → `menu_del_dia.id` NOT NULL indexada; `fecha` UNIQUE.
- Recomendación: mantener `src/productos_menu/` como módulo del registro de fechas para minimizar el diff.

## Impacto en tests

- `Backend/tests/productos_menu/` (12 archivos) se reescribe casi por completo, incluida `test_integracion_productos.py` (PMD-37..40).
- `Backend/tests/conftest.py`: la fixture `crear_producto_menu` pasa a usar `menu_del_dia=`; se agrega `crear_menu_del_dia`. `crear_menu` pertenece a `MenuEjecutivo` y no se modifica.
- `Backend/tests/productos/test_registro.py`: el conteo de tipos pasa de 5 a 6.
- `tests/productos/test_schemas.py:170` (PMD-39) debe seguir siendo válido.

## Migración SQLite

`create_all` no altera tablas existentes; `Backend/app.db` y `Backend/restaurante.db` quedarían desfasadas. Opciones: (a) descartar `producto_menu` en desarrollo; (b) migración manual al estilo de `migrar_detalle_reserva_legacy`. Recomendado: (a), documentado.

## Frontend

Consume `/productos-menu`: `Frontend/src/features/daily-menu/api.ts`, `useDailyMenusList.ts`, `useDailyMenuForm.ts` (selector de platos), `DailyMenusTab.tsx`, `DailyMenuFormPage.tsx`, rutas en `app/routes.tsx` y la pestaña "Menú del día" en `features/menus/MenusPage.tsx`. `features/menus/format.ts` necesitaría la etiqueta `menu_del_dia`.

## Preguntas abiertas y valores recomendados

1. Campos propios de `MenuDelDia`: ninguno (solo los comunes de `Producto`).
2. Endpoints: CRUD del subtipo en `/productos/menus-del-dia`; se mantiene `/productos-menu` con `menu_del_dia_id` en lugar de `producto_id`.
3. Baja lógica de un `MenuDelDia` con fechas: se permite y se conserva el historial; asignar una fecha nueva a un menú dado de baja responde 409.
4. Fechas pasadas y futuras: se permiten.
5. Datos existentes: se descartan en desarrollo, sin migración.
6. Frontend: pendiente de decisión.

## Riesgos

- El frontend deja de funcionar si cambia el contrato.
- La base local queda desfasada.
- Colisión de nombres con la fixture `crear_menu`.
- `openspec/specs/daily-menu-management/spec.md` queda obsoleta y requiere una spec delta.
