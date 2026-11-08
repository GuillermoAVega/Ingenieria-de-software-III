# Diseño: Menú del Día como subtipo de Producto

## Enfoque técnico

Nuevo subtipo `MenuDelDia(Producto)` en `Backend/src/productos/menus_del_dia/`, copia del patrón mínimo de `postres/` (servicios genéricos, sin campos propios). `ProductoMenu` conserva su módulo y pasa a `menu_del_dia_id → menu_del_dia.id`. La regla de baja se agrega en el punto central donde ya vive la regla de vigencia de combos (`productos/services.py`, invocada por `aplicar_cambio_estado`), de modo que cubre DELETE y PUT con `dado_de_baja: true`. Implementa las deltas de `daily-menu-management`, `product-catalog` y `product-logical-delete`.

```
DELETE/PUT /productos/menus-del-dia/{id}
  → services.aplicar_cambio_estado ─→ buscar_fechas_vigentes(ProductoMenu.fecha >= hoy) ─→ 409
POST/PUT /productos-menu
  → productos_menu.services ─→ get(MenuDelDia) 422 → dado_de_baja 409 → fecha libre 409 → commit
```

## Decisiones de arquitectura

| # | Tema | Opciones | Compromiso | Decisión |
|---|------|----------|------------|----------|
| 1 | Regla de baja sin ciclo | (a) consulta en `productos/services.py` usando `ProductoMenu` importado desde `registro`; (b) gancho `verificar_baja` pasado por el router del subtipo; (c) consulta por nombre de tabla | (b) obliga a reescribir `dar_de_baja` para el subtipo y puede omitirse en un PUT; (c) pierde tipado | **(a)**. `productos/services.py` ya importa `registro` (donde está `combo_*` y la regla `fecha_hasta >= hoy`); `registro` ya importa `productos_menu.models`, que solo depende de `src.models`. No se crea ninguna arista nueva en el grafo |
| 2 | Ubicación de la regla | (a) dentro de `buscar_bloqueantes`; (b) función propia llamada desde `aplicar_cambio_estado` | (a) mezclaría ids de productos con fechas | **(b)**. `buscar_fechas_vigentes(sesion, producto, hoy) -> list[date]`, solo si `producto.tipo == TIPO_MENU_DEL_DIA`, antes de `buscar_bloqueantes`. `RESTRICT_POR_TIPO` no cambia |
| 3 | Error de la regla | (a) reutilizar `BajaRestringida`; (b) `MenuDelDiaConFechasVigentes(ErrorConflicto)` | (a) su campo `bloqueantes` son ids de compuestos | **(b)** en `productos/exceptions.py` (los servicios genéricos no importan subpaquetes), con atributo `fechas: list[date]` ya ordenado. `manejar_conflicto` (`productos/router.py`) agrega su propia rama `elif isinstance(error, MenuDelDiaConFechasVigentes): cuerpo["fechas"] = [f.isoformat() for f in error.fechas]`; sin esa rama el manejador genérico de `ErrorConflicto` emitiría solo `detail` |
| 3b | Rollback en `dar_de_baja` | (a) agregar `MenuDelDiaConFechasVigentes` a la tupla; (b) ampliar la cláusula a `ErrorDominio` | (a) vuelve a quedar frágil ante el próximo error de dominio | **(b)**. Hoy `dar_de_baja` solo captura `(ProductoNoEncontrado, BajaRestringida)` antes de `sesion.rollback()`: el nuevo error dejaría la transacción abierta. Se cambia a `except ErrorDominio`, igual que `actualizar_producto` y `crear_producto`. Prueba: tras el 409 de DELETE, `sesion.in_transaction()` es falso. `actualizar_producto` ya cubre el PUT `dado_de_baja: true` sin cambios |
| 4 | Relaciones | — | — | `MenuDelDia.fechas = relationship("ProductoMenu", back_populates="menu_del_dia", order_by="ProductoMenu.fecha")`; `ProductoMenu.menu_del_dia = relationship("MenuDelDia", back_populates="fechas")`. Se elimina `Producto.menus_del_dia`. FK por cadena `ForeignKey("menu_del_dia.id")`, NOT NULL, indexada, sin `ondelete`. La regla consulta con `select`, no por la relación (evita cargar el historial) |
| 5 | Carga en `/productos-menu` | (a) `sesion.get(MenuDelDia, id)`; (b) `get(Producto)` + chequeo de tipo | (b) duplica lo que hace el mapper | **(a)**. Un id de otro subtipo devuelve `None` → 422 (probarlo) |
| 6 | Excepciones de `productos_menu` | (a) conservar nombres; (b) renombrar | (a) induce a error | **(b)** `ProductoInexistente` → `MenuDelDiaInexistente` (422, `loc: ["body","menu_del_dia_id"]`, `type: "menu_del_dia_inexistente"`), `ProductoDadoDeBaja` → `MenuDelDiaDadoDeBaja` (409). `FechaMenuOcupada` y `ProductoMenuNoEncontrado` sin cambios. Jerarquía disjunta de `ErrorDominio` (decisión 7 del diseño archivado) |
| 7 | Prioridad | — | — | POST: inexistente 422 → dado de baja 409 → fecha ocupada 409. PUT: 404 → dado de baja 409 → fecha ocupada (excluyendo el propio id) 409. DELETE: 404 → borrado físico sin mirar el estado |
| 8 | Esquemas | — | — | `ProductoMenuCrear{menu_del_dia_id, fecha}`, `ProductoMenuRespuesta{id, menu_del_dia_id, fecha}`, `ProductoMenuDetalleRespuesta` + `menu_del_dia_nombre`, `menu_del_dia_dado_de_baja` (`AliasPath("menu_del_dia", …)`); se elimina `producto_tipo`. `MenuDelDiaRespuesta` no expone `fechas` |
| 8b | `PUT /productos-menu` (MDD-16) | (a) `extra="ignore"` por defecto de Pydantic; (b) `extra="forbid"` | (b) rompería clientes que reenvían el registro completo y contradice MDD-16 | **(a)**. `ProductoMenuActualizar` declara solo `fecha` y no define `model_config`, igual que hoy (comentario: "cualquier otro campo se ignora"); se actualiza el comentario para nombrar `menu_del_dia_id`. El servicio nunca asigna `menu_del_dia_id`. Pruebas: esquema con `{fecha, menu_del_dia_id}` no expone `menu_del_dia_id`; HTTP PUT con `menu_del_dia_id` de otro `MenuDelDia` activo → 200 y el registro conserva el original |
| 9 | Frontend CRUD | (a) nueva feature; (b) cuarto tipo en `features/products/` | (a) duplica formulario y listado | **(b)**. Tipo/pestaña `menus-del-dia` (coincide con la ruta de API), mismo formulario que postres |
| 10 | Selector en `daily-menu` | — | — | `useDailyMenuForm` carga `getMenusDelDia()` (activos) en lugar de `getPlatos()`; el único objeto de estado reemplaza `productoId`/`producto`/`platos`/`platosLoading` por `menuDelDiaId`/`registro`/`menusDelDia`/`menusDelDiaLoading`; `fieldErrors.menu_del_dia_id` (validación local y 422 vía `getFieldErrors`). La pantalla solo renderiza (AGENTS.md) |
| 11 | Errores del alta/edición (MDD-27) | — | — | Se conserva el patrón actual del hook: el `catch` de `submit` solo asigna `error: getErrorMessage(e)` y `fieldErrors: getFieldErrors(e)`, sin tocar `fecha` ni `menuDelDiaId`, por lo que el formulario conserva los valores. El mensaje es el `detail` en español del backend (fecha ocupada o menú dado de baja); no se traduce en el cliente |
| 12 | Edición solo de la fecha (MDD-28) | — | — | En edición `DailyMenuFormPage` no renderiza el selector: muestra un `Input` deshabilitado con `state.registro?.menu_del_dia_nombre` (campo "Menú del día") y la alerta de advertencia si `menu_del_dia_dado_de_baja`. `submit` en edición sigue llamando `updateProductoMenuFecha(id, fecha)`, cuyo cuerpo es solo `{ fecha }` |
| 13 | Listado de menús del día (MDD-29) | — | — | `ProductoMenuDetalle` pasa a `{id, menu_del_dia_id, fecha, menu_del_dia_nombre, menu_del_dia_dado_de_baja}`. `DailyMenusTab`: columnas Fecha y "Menú del día" (nombre + `Badge` "Dado de baja" si `menu_del_dia_dado_de_baja`); se elimina la columna Tipo. `useDailyMenusList` filtra por nombre y fecha (sin `tipoLabel`) |
| 14 | Baja bloqueada en productos (MDD-47) | (a) reutilizar `state.error`; (b) campo `actionError` en el mismo objeto de estado | (a) se muestra bajo el título "No se pudieron cargar los productos", que es engañoso | **(b)**. `useProductsList.remove` asigna `actionError: getDeleteErrorMessage(e)` y no incrementa `reloadToken`, por lo que el menú permanece en el listado. `getDeleteErrorMessage` (en `features/products/errors.ts`): si es `ApiError` 409 con `body.fechas` arreglo no vacío → "No se puede dar de baja el menú del día porque tiene fechas asignadas: " + fechas con `formatDate`; si no, `getErrorMessage(e)`. `ProductsListPage` lo muestra en un `Alert` "No se pudo dar de baja el producto". Llamadas solo vía funciones de `products/api.ts` (`apiFetch`) |

## Archivos y estimación

| Archivo | Acción | Líneas aprox. |
|---|---|---|
| `Backend/src/productos/menus_del_dia/{__init__,constants,exceptions,models,schemas,services,router}.py` | Crear | +90 |
| `Backend/src/productos/{constants,registro,router,models}.py` | Modificar (tipo, `MODELOS_POR_TIPO` a seis, subrouter, quitar `menus_del_dia`) | ±15 |
| `Backend/src/productos/services.py` | Modificar (`buscar_fechas_vigentes`, llamada en `aplicar_cambio_estado`, `dar_de_baja` captura `ErrorDominio`) | +20 |
| `Backend/src/productos/exceptions.py` | Modificar (`MenuDelDiaConFechasVigentes(ErrorConflicto)` con `fechas`) | +8 |
| `Backend/src/productos/router.py` | Modificar (`manejar_conflicto`: rama `isinstance` que emite `fechas`) | +3 |
| `Backend/src/productos_menu/{models,schemas,services,exceptions,router}.py` | Modificar | ±70 |
| `Backend/tests/conftest.py` | `crear_menu_del_dia`; `crear_producto_menu(menu_del_dia, fecha=None)` | ±15 |
| `Backend/tests/productos/menus_del_dia/**` | Crear (modelos, esquemas, servicios, router, regla de baja) | +220 |
| `Backend/tests/productos/{test_registro,test_constantes,test_manejadores}.py` | 5 → 6 tipos; cuerpo con `fechas` | ±20 |
| `Backend/tests/productos_menu/**` (12 archivos) | Reescribir a `menu_del_dia` | ±300 |
| `Frontend/src/features/products/{api,useProductForm,useProductsList,ProductFormPage,ProductsListPage}.ts(x)` | Tipo `menus-del-dia`; `actionError` en el estado del listado | +70 |
| `Frontend/src/features/products/errors.ts` | Crear (`getDeleteErrorMessage`, lee `fechas` del 409) | +15 |
| `Frontend/src/features/daily-menu/{api,useDailyMenuForm,useDailyMenusList,DailyMenuFormPage,DailyMenusTab}.ts(x)` | Contrato `menu_del_dia_id`; selector; sin columna Tipo | ±90 |
| `Frontend/src/features/menus/format.ts` | Etiqueta `menu_del_dia` | +1 |

Backend ≈ 760 líneas, frontend ≈ 175. Cortes sugeridos: (1) subtipo `MenuDelDia` y su CRUD (≈ 330); (2) FK de `ProductoMenu`, regla de baja y reescritura de pruebas (≈ 430, ajustado al límite); (3) frontend (≈ 175). (2) rompe el frontend hasta (3): entregar en cadena sobre una rama de la funcionalidad.

## Estrategia de pruebas

TDD estricto con pytest; `crear_menu` (de `MenuEjecutivo`) no se toca. `crear_producto_menu` usa fechas desde 2100-01-01, que son `>= HOY_FIJO`: las pruebas de baja permitida deben pasar fechas pasadas explícitas.

| Capa | Qué prueba |
|---|---|
| Unidad | `configure_mappers()`; identidad polimórfica; relación bidireccional; FK NOT NULL; esquemas (`menu_del_dia_id` requerido en el alta, `producto_id` ignorado; `ProductoMenuActualizar` ignora `menu_del_dia_id`); manejadores (422 y 409 con `fechas` ISO ascendentes; `BajaRestringida` sigue emitiendo `bloqueantes`) |
| Servicio | Baja con fecha `== hoy` → 409; con `hoy - 1` → permitida e historial intacto; PUT `dado_de_baja: true` → 409; reactivación; dobles condiciones de prioridad; id de un `Plato` → 422; `sesion.in_transaction()` falso tras cada error, incluido `MenuDelDiaConFechasVigentes` en `dar_de_baja` |
| HTTP | CRUD `/productos/menus-del-dia`; DELETE bloqueado → 409 con `fechas`; `/productos-menu` con el nuevo contrato; PUT con `menu_del_dia_id` ajeno → 200 sin cambiar la asociación (MDD-16); petición rechazada no modifica filas |

Frontend: sin herramientas de prueba en `package.json`; verificación con `npm run build` (`tsc -b`) y `npm run lint`, más prueba manual de MDD-27 (409 conserva valores), MDD-28 (edición con menú de solo lectura y PUT `{ fecha }` en la pestaña de red), MDD-29 (insignia "Dado de baja") y MDD-47 (mensaje con las fechas y el menú sigue en el listado).

## Matriz de amenazas

N/A — sin enrutamiento de shell, subprocesos, automatización VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

Sin migración de datos. `create_all` crea `menu_del_dia` pero no altera `producto_menu`: en desarrollo eliminar esa tabla o recrear `Backend/app.db` (y `Backend/restaurante.db`). Las pruebas usan SQLite en memoria.

## Preguntas abiertas

- [ ] Ninguna bloqueante.
