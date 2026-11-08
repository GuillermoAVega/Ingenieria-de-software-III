# Tareas: Menú del Día como subtipo de Producto

Cambio: `menu-del-dia-producto`. Entradas: `proposal.md`, `design.md`, `specs/daily-menu-management/spec.md`, `specs/product-catalog/spec.md`, `specs/product-logical-delete/spec.md` (MDD-01 a MDD-62, 62 escenarios). Comando de pruebas: `cd Backend && python -m pytest`. Los escenarios se numeran en el Anexo A.

## Pronóstico de carga de revisión

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | PR 1 ≈ 330; PR 2 ≈ 430; PR 3 ≈ 175; total ≈ 935 (backend ≈ 760, frontend ≈ 175; aprox. 65 % pruebas en backend) |
| Riesgo frente al presupuesto de 400 líneas | Medium (el PR 2 queda en el límite o lo supera; los PR 1 y 3 caben) |
| PR encadenados recomendados | Yes |
| División sugerida | PR 1 (Fase 1) → PR 2 (Fases 2-3) → PR 3 (Fase 4); el PR 2 puede dividirse en 2a (Fase 2) y 2b (Fase 3) si supera 400 líneas |
| Estrategia de entrega | ask-on-risk |
| Estrategia de cadena | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: Medium

Decisión pendiente: elegir la estrategia de cadena (rama de la funcionalidad con PR apilados, o PR encadenados sobre `main`) y si el PR 2 se divide en 2a/2b. El PR 2 deja el frontend roto hasta el PR 3 (cambia el contrato de `/productos-menu`), por lo que los PR 2 y 3 deben integrarse sobre una rama de la funcionalidad y no directamente en `main` por separado.

### Unidades de trabajo sugeridas

| Unidad | Objetivo | PR probable | Comando de prueba focalizado | Arnés de ejecución | Límite de reversión |
|--------|----------|-------------|------------------------------|--------------------|---------------------|
| 1 | Subtipo `MenuDelDia` y su CRUD en `/productos/menus-del-dia` | PR 1 | `cd Backend && python -m pytest tests/productos` | `POST/GET/PUT/DELETE /productos/menus-del-dia` | `Backend/src/productos/menus_del_dia/`, `constants.py`, `registro.py`, `router.py` de `productos`; `Backend/tests/productos/menus_del_dia/` |
| 2 | FK `menu_del_dia_id` en `ProductoMenu`, rechazo de otros subtipos, regla de baja, reescritura de `tests/productos_menu` | PR 2 (2a: Fase 2; 2b: Fase 3) | `cd Backend && python -m pytest` | `rm Backend/app.db`, `POST /productos-menu`, `DELETE /productos/menus-del-dia/{id}` | `Backend/src/productos_menu/**`, `Backend/src/productos/{models,services,exceptions,router}.py`, `Backend/tests/productos_menu/**` |
| 3 | Frontend: tipo `menus-del-dia`, selector, listado, mensaje de baja bloqueada | PR 3 | `cd Frontend && npm run build && npm run lint` | Lista de verificación manual (Fase 4) | `Frontend/src/features/{products,daily-menu,menus}/**` |

## Convenciones

- **TDD estricto**: cada tarea de comportamiento sigue RED (pruebas que fallan por el motivo correcto) → GREEN (código mínimo) → REFACTOR opcional con la suite en verde. Las pruebas de **caracterización** (comportamiento existente que el cambio no debe romper) nacen en verde y se rotulan **[CARACTERIZACIÓN: nace en verde]**.
- Nombres de prueba: `test_mdd_NN_<descripcion>`.
- Niveles: **E** = esquema/unidad, **S** = servicio, **H** = HTTP con `TestClient`, **BD** = integración con SQLite. Cada escenario con comportamiento HTTP tiene al menos una prueba H o BD.
- `[COMMIT]` = unidad confirmable con la suite en verde; commits convencionales, sin atribución de IA.
- Un solo escritor: varias tareas modifican `Backend/tests/conftest.py`, `Backend/src/productos/services.py` y `Backend/src/productos_menu/services.py`.
- El frontend no tiene ejecutor de pruebas: la verificación es `npm run build` (`tsc -b`) y `npm run lint` en `Frontend/`, más la lista manual de la Fase 4. Reglas de `AGENTS.md`: un único objeto de estado por hook, lógica en hooks de la feature, sin `fetch` directo, mensajes en español e identificadores en inglés.
- Cada PR deja la suite de backend completa en verde.
- Hasta la tarea 2.1 `ProductoMenu` conserva `producto_id` y `Producto.menus_del_dia`: el PR 1 no los toca.

---

## Fase 1 (PR 1): Subtipo `MenuDelDia` y su CRUD

- [x] **1.1 Constante de tipo, modelo y registro** — Archivos: `Backend/src/productos/menus_del_dia/{__init__,constants,models}.py`, `Backend/src/productos/constants.py`, `Backend/src/productos/registro.py`, `Backend/tests/productos/menus_del_dia/{__init__,test_modelos}.py`, `Backend/tests/productos/{test_registro,test_constantes}.py`.
  - RED: `test_mdd_30_modelos_por_tipo_contiene_seis_tipos` (incluye `menu_del_dia` y `configure_mappers()` sin error); `TIPO_MENU_DEL_DIA == "menu_del_dia"`; identidad polimórfica (`tipo`, tabla `menu_del_dia`); `MenuDelDia` y `MenuEjecutivo` son clases y tablas distintas (MDD-31, nivel modelo); las pruebas que contaban cinco tipos pasan a seis. Falla por importación inexistente.
  - GREEN: `MenuDelDia(Producto)` sin campos propios (patrón de `postres/`), constante, entrada en `MODELOS_POR_TIPO` y en `registro.py`. `RESTRICT_POR_TIPO` no cambia.
  - Escenarios: MDD-30, MDD-31 (parcial).

- [x] **1.2 Esquemas y servicios genéricos del subtipo** — Archivos: `Backend/src/productos/menus_del_dia/{exceptions,schemas,services}.py`, `Backend/tests/conftest.py` (fábrica `crear_menu_del_dia`), `Backend/tests/productos/menus_del_dia/{test_schemas,test_servicios}.py`. Depende de 1.1.
  - RED:
    - (E) Entrada con solo campos comunes (`nombre`, `precio`, `descripcion`, `imagen`, `seccion_id`) y `dado_de_baja` en el PUT; la respuesta expone los comunes y `tipo = "menu_del_dia"` y no expone `fechas` ni `menus_del_dia` (MDD-20, nivel esquema); validación de `nombre` vacío, `precio = 0` y `descripcion` de 501 caracteres (MDD-34).
    - (S) Crear, `seccion_id` inexistente (MDD-34), nombre activo duplicado entre subtipos (MDD-35), listar solo activos por `id` ascendente (MDD-36), obtener un dado de baja (MDD-38), PUT como reemplazo completo (MDD-40), `seccion_id` en el PUT (MDD-43).
  - GREEN: copia del patrón de `postres/` sobre los servicios genéricos; fábrica `crear_menu_del_dia(...)` en `conftest.py`.
  - Escenarios (E/S): MDD-20 (parcial), MDD-32..36, MDD-38, MDD-40, MDD-43.

- [x] **1.3 Router `/productos/menus-del-dia` y subrouter** — Archivos: `Backend/src/productos/menus_del_dia/router.py`, `Backend/src/productos/router.py`, `Backend/tests/productos/menus_del_dia/test_router.py`, `Backend/tests/productos/test_manejadores.py`. Depende de 1.2.
  - RED (H): 201 con `tipo = "menu_del_dia"` (MDD-32); con `seccion_id` (MDD-33); 422 sin registro (MDD-34); 409 por nombre duplicado (MDD-35); listado de activos (MDD-36); listado vacío con platos y menús ejecutivos presentes (MDD-37); GET de uno dado de baja → 200 con `dado_de_baja` (MDD-38); id de un Plato o inexistente → 404 (MDD-39); PUT de reemplazo completo deja `descripcion`, `imagen` y `seccion_id` en `null` (MDD-40); 422 sobre 404 (MDD-41); 404 en PUT (MDD-42); PUT con y sin sección válida (MDD-43); cada ruta responde solo en la suya, la ruta del otro subtipo devuelve 404 (MDD-31); la respuesta no contiene `fechas` ni `menus_del_dia` (MDD-20).
  - GREEN: `APIRouter` del subtipo registrado en el router de `productos`.
  - Escenarios (H): MDD-20, MDD-31..43.

- [x] **1.4 Suite completa intacta** — **[CARACTERIZACIÓN: nace en verde]** — Archivos: ninguno. Depende de 1.3.
  - Verificar `cd Backend && python -m pytest` en verde, y que `tests/productos_menu` y la baja de Plato, Bebida y Postre no cambiaron.
  - `[COMMIT]` (Fase 1 completa; PR 1 cerrable aquí).

---

## Fase 2 (PR 2 / 2a): FK `menu_del_dia_id` y reescritura de `productos_menu`

- [x] **2.1 Modelo, relación y fábrica** — Archivos: `Backend/src/productos_menu/models.py`, `Backend/src/productos/menus_del_dia/models.py`, `Backend/src/productos/models.py`, `Backend/tests/conftest.py`, `Backend/tests/productos_menu/{test_modelos,test_fabrica}.py`.
  - RED:
    - `test_mdd_01_relacion_bidireccional` (`ProductoMenu.menu_del_dia` y `MenuDelDia.fechas`, ordenadas por `fecha`).
    - `test_mdd_03_menu_sin_fechas_tiene_coleccion_vacia`.
    - Columna `menu_del_dia_id` NOT NULL con índice (`IntegrityError` al omitirla), FK a `menu_del_dia.id` sin `ON DELETE`; `ProductoMenu` no tiene `producto_id`; `Producto.menus_del_dia` no existe; `configure_mappers()` sin error.
    - `test_mdd_24_menu_con_varias_fechas` (BD) y el índice UNIQUE de `fecha` se conserva.
    - Fábrica `crear_producto_menu(menu_del_dia, fecha=None)` con fechas desde `date(2100, 1, 1)` y contador por prueba.
  - GREEN: reemplazar `producto_id` y la relación `producto` por `menu_del_dia_id` (`ForeignKey("menu_del_dia.id")`, NOT NULL, `index=True`) y `menu_del_dia = relationship("MenuDelDia", back_populates="fechas")`; `MenuDelDia.fechas = relationship("ProductoMenu", back_populates="menu_del_dia", order_by="ProductoMenu.fecha")`; eliminar `Producto.menus_del_dia`. Relaciones por cadena (sin importaciones cíclicas).
  - Escenarios (BD): MDD-01, MDD-03, MDD-24 (parcial).

- [x] **2.2 Excepciones y esquemas renombrados** — Archivos: `Backend/src/productos_menu/{exceptions,schemas}.py`, `Backend/tests/productos_menu/{test_excepciones,test_schemas}.py`. Depende de 2.1.
  - RED: `ProductoInexistente` → `MenuDelDiaInexistente(menu_del_dia_id)` y `ProductoDadoDeBaja` → `MenuDelDiaDadoDeBaja`; `FechaMenuOcupada` y `ProductoMenuNoEncontrado` sin cambios; jerarquía disjunta de `ErrorDominio`. (E) `ProductoMenuCrear{menu_del_dia_id, fecha}` con `menu_del_dia_id` ausente, incluido un cuerpo que solo envía `producto_id` (MDD-06), y no entero (MDD-07); `ProductoMenuRespuesta{id, menu_del_dia_id, fecha}` (MDD-02); `ProductoMenuDetalleRespuesta` con `menu_del_dia_nombre` y `menu_del_dia_dado_de_baja` (vía `AliasPath("menu_del_dia", …)`), sin `producto_tipo`; `ProductoMenuActualizar` con `{fecha, menu_del_dia_id}` solo expone `fecha` (MDD-16, nivel esquema); sin `model_config`, con el comentario actualizado.
  - GREEN: renombrar y ajustar los modelos Pydantic.
  - Escenarios (E): MDD-02, MDD-06, MDD-07, MDD-16 (parcial), MDD-21 (parcial).

- [x] **2.3 Servicios de `productos_menu`** — Archivos: `Backend/src/productos_menu/services.py`, `Backend/tests/productos_menu/test_servicios.py`. Depende de 2.2.
  - RED (S):
    - Alta con `sesion.get(MenuDelDia, id)`: alta válida, fecha pasada, de hoy y futura, mismo menú en dos fechas (MDD-04, MDD-24).
    - El id de un Plato, Bebida, Postre, MenuEjecutivo o ComboPromocion lanza `MenuDelDiaInexistente` (MDD-05); id inexistente (MDD-08); menú dado de baja (MDD-09); fecha ocupada (MDD-10).
    - Prioridad: inexistente sobre fecha ocupada (MDD-12); baja sobre fecha ocupada (MDD-13).
    - Cada error deja `sesion.in_transaction()` en falso y el conjunto persistido idéntico (MDD-14); el `IntegrityError` de `producto_menu.fecha` se traduce a `FechaMenuOcupada` y uno ajeno se propaga.
    - `actualizar_fecha`: ignora `menu_del_dia_id` (MDD-16); menú dado de baja → `MenuDelDiaDadoDeBaja` sin cambios (MDD-15); baja sobre fecha ocupada (MDD-17); conservar la fecha propia, mover a fecha libre, fecha de otro registro, 404 antes que 409.
    - `eliminar` no mira el estado del menú (MDD-18); la fecha liberada se reutiliza.
    - Listado ordenado por `fecha` descendente con los menús dados de baja incluidos (MDD-21, MDD-22); consulta por id coincide con el listado (MDD-23).
  - GREEN: `crear` con `get(MenuDelDia)` → dado de baja → fecha libre; `actualizar_fecha` con 404 → baja → fecha libre excluyendo el propio id; `_confirmar` sin cambios.
  - Escenarios (S): MDD-04, MDD-05, MDD-08..10, MDD-12..18, MDD-21..24.

- [x] **2.4 Router y manejadores de `productos_menu`** — Archivos: `Backend/src/productos_menu/router.py`, `Backend/tests/productos_menu/{test_manejadores,test_router_alta,test_router_modificacion,test_router_borrado,test_router_listado}.py`. Depende de 2.3.
  - RED (H):
    - Manejadores: `MenuDelDiaInexistente` → 422 con `loc: ["body","menu_del_dia_id"]` y `type: "menu_del_dia_inexistente"`; `MenuDelDiaDadoDeBaja` → 409 con mensaje que identifica el menú dado de baja; `FechaMenuOcupada` → 409 con mensaje distinto; `ProductoMenuNoEncontrado` → 404.
    - POST: 201 con exactamente `id`, `menu_del_dia_id` y `fecha`, sin `producto_id` (MDD-02, MDD-04); 422 para id de otro subtipo (MDD-05), ausente (MDD-06), no entero (MDD-07), inexistente (MDD-08); 409 baja (MDD-09), fecha ocupada con el existente intacto (MDD-10); esquema sobre inexistente (MDD-11); inexistente sobre fecha ocupada (MDD-12); baja sobre fecha ocupada con mensaje distinto (MDD-13); rechazos no modifican filas (MDD-14); dos altas del mismo menú en fechas distintas → 201 y `MenuDelDia.fechas` con ambas (MDD-24); alta concurrente simulada con `_verificar_fecha_libre` anulado → 409 y no 500.
    - PUT: 409 con menú dado de baja (MDD-15); `menu_del_dia_id` ajeno en el cuerpo → 200 y el registro conserva el original (MDD-16); baja sobre fecha ocupada (MDD-17).
    - DELETE: 204 con menú dado de baja (MDD-18).
    - GET listado y detalle: claves exactas `id`, `menu_del_dia_id`, `fecha`, `menu_del_dia_nombre`, `menu_del_dia_dado_de_baja`; historial con menús dados de baja; detalle igual al ítem del listado; 404 si no existe (MDD-21..23).
  - GREEN: ajustar rutas, `_error_de_campo` y mensajes a `menu_del_dia`.
  - Escenarios (H): MDD-02, MDD-04..18, MDD-21..24.

- [x] **2.5 Suite completa en verde con la regla de baja aún ausente** — **[CARACTERIZACIÓN: nace en verde]** — Archivos: ninguno. Depende de 2.4.
  - `rg "producto_id|Producto\b|crear_plato" Backend/tests/productos_menu` no devuelve restos del contrato anterior; `rg "from src.productos" Backend/src/productos_menu/models.py` sin resultados. `cd Backend && python -m pytest` en verde.
  - `[COMMIT]` (Fase 2 completa; PR 2a cerrable aquí).

---

## Fase 3 (PR 2 / 2b): Regla de baja de `MenuDelDia`

- [x] **3.1 Excepción y manejador con `fechas`** — Archivos: `Backend/src/productos/exceptions.py`, `Backend/src/productos/router.py`, `Backend/tests/productos/test_manejadores.py`.
  - RED (H, aplicación mínima): `MenuDelDiaConFechasVigentes(ErrorConflicto)` con `fechas: list[date]` produce 409 con `detail` en español y `fechas` en ISO ascendente; `BajaRestringida` sigue emitiendo `bloqueantes` (caracterización); un `ErrorConflicto` genérico sigue emitiendo solo `detail`.
  - GREEN: nueva clase y rama `elif isinstance(error, MenuDelDiaConFechasVigentes)` en `manejar_conflicto`.
  - Escenarios: soporte de MDD-49, MDD-54.

- [x] **3.2 `buscar_fechas_vigentes` y llamada en `aplicar_cambio_estado`** — Archivos: `Backend/src/productos/services.py`, `Backend/tests/productos/menus_del_dia/test_baja.py`. Depende de 3.1, 2.1.
  - RED (S, con `obtener_hoy` fijado):
    - Fecha futura bloquea (MDD-49); fecha de hoy bloquea (MDD-50); PUT con `dado_de_baja = true` bloquea sin cambiar otros campos (MDD-51).
    - Solo fechas pasadas permite la baja y el historial permanece (MDD-52, MDD-19); sin fechas permite por DELETE y por PUT (MDD-53).
    - Múltiples bloqueantes en orden ascendente, sin la pasada (MDD-54); el límite depende de `obtener_hoy` (F+1 permite, F bloquea) (MDD-55); borrar la fecha vigente desbloquea (MDD-56); baja repetida idempotente (MDD-57).
    - Tras el rechazo el menú sigue activo y los `ProductoMenu` intactos (MDD-58); `sesion.in_transaction()` falso tras el 409 de `dar_de_baja`.
    - Plato, Postre y Bebida con registros `ProductoMenu` vigentes sobre un `MenuDelDia` se dan de baja sin bloqueo (MDD-62).
  - GREEN: `buscar_fechas_vigentes(sesion, producto, hoy) -> list[date]` (consulta `select` sobre `ProductoMenu.fecha >= hoy`, solo si `producto.tipo == TIPO_MENU_DEL_DIA`), llamada en `aplicar_cambio_estado` antes de `buscar_bloqueantes`; `dar_de_baja` pasa a capturar `ErrorDominio` antes del rollback. `RESTRICT_POR_TIPO` no cambia.
  - Escenarios (S): MDD-19, MDD-49..58, MDD-62.

- [x] **3.3 Rutas de baja de `MenuDelDia` por HTTP** — Archivos: `Backend/tests/productos/menus_del_dia/test_router_baja.py`. Depende de 3.2.
  - RED (H): DELETE bloqueado → 409 con clave `fechas` en ISO ascendente (MDD-49, MDD-54); fecha de hoy (MDD-50); PUT bloqueado (MDD-51); DELETE con fechas pasadas → 204 y registros intactos (MDD-52); sin fechas (MDD-53); borrar la fecha por `DELETE /productos-menu/{id}` y luego la baja → 204 (MDD-56); DELETE repetido → 204 sin cuerpo (MDD-57); invariante tras 409 (MDD-58); `POST /productos-menu` con menú dado de baja → 409 (MDD-59); reactivar por PUT y luego `POST` → 200 y 201 (MDD-60); reactivar con nombre duplicado → 409 y sigue dado de baja (MDD-61); baja de Plato, Postre y Bebida con registros vigentes → éxito (MDD-62).
  - GREEN: sin código adicional si 3.2 está completa; si falla, corregir el origen de la falla.
  - Escenarios (H): MDD-49..62.

- [x] **3.4 Suite completa y trazabilidad backend** — **[CARACTERIZACIÓN: nace en verde]** — Archivos: ninguno. Depende de 3.3.
  - `cd Backend && python -m pytest` en verde; `configure_mappers()` sin error; para cada escenario MDD-01..43 y MDD-49..62 existe una prueba `test_mdd_NN` (listado de huecos vacío o registrado como riesgo). `rg "productos_menu" Backend/src/productos` solo en `registro.py` y cadenas de relaciones.
  - `[COMMIT]` (Fase 3 completa; PR 2 cerrable aquí).

---

## Fase 4 (PR 3): Frontend

Verificación de cada tarea: `cd Frontend && npm run build && npm run lint` sin errores. Sin ejecutor de pruebas, la conducta se comprueba con la lista manual de 4.6.

- [x] **4.1 Tipo `menus-del-dia` en la feature de productos** — Archivos: `Frontend/src/features/products/api.ts`, `Frontend/src/features/menus/format.ts`.
  - Agregar el tipo `menus-del-dia`, las funciones de API (`getMenusDelDia`, alta, edición, baja, obtención) vía `apiFetch`, y la etiqueta en español para `menu_del_dia` distinta de la de `menu_ejecutivo` (MDD-48).
  - Escenarios: MDD-44..46, MDD-48 (soporte).

- [x] **4.2 Hooks y pantallas de productos con el cuarto tipo** — Archivos: `Frontend/src/features/products/{useProductForm,useProductsList,ProductFormPage,ProductsListPage}.ts(x)`. Depende de 4.1.
  - Pestaña y formulario con los campos comunes (mismo formulario que postres); listado solo de activos; edición con `PUT` de cuerpo completo. Estado único por hook, sin `fetch` directo.
  - Escenarios: MDD-44, MDD-45, MDD-46.

- [x] **4.3 Baja bloqueada informada** — Archivos: `Frontend/src/features/products/errors.ts` (nuevo), `Frontend/src/features/products/{useProductsList,ProductsListPage}.ts(x)`. Depende de 4.2.
  - `getDeleteErrorMessage(e)`: si es `ApiError` 409 con `body.fechas` arreglo no vacío, devuelve "No se puede dar de baja el menú del día porque tiene fechas asignadas: " con las fechas formateadas con `formatDate`; si no, `getErrorMessage(e)`. `useProductsList` agrega `actionError` al mismo objeto de estado, lo asigna en `remove` sin incrementar `reloadToken`; `ProductsListPage` lo muestra en un `Alert` "No se pudo dar de baja el producto".
  - Escenarios: MDD-47.

- [x] **4.4 Contrato `menu_del_dia_id` en `daily-menu`** — Archivos: `Frontend/src/features/daily-menu/{api,useDailyMenuForm}.ts(x)`. Depende de 4.1.
  - `ProductoMenuDetalle` pasa a `{id, menu_del_dia_id, fecha, menu_del_dia_nombre, menu_del_dia_dado_de_baja}`; `useDailyMenuForm` carga `getMenusDelDia()` (activos) y reemplaza `productoId`/`producto`/`platos`/`platosLoading` por `menuDelDiaId`/`registro`/`menusDelDia`/`menusDelDiaLoading` en el único objeto de estado; `fieldErrors.menu_del_dia_id` por validación local y 422 vía `getFieldErrors`; el `catch` de `submit` conserva `fecha` y `menuDelDiaId` (MDD-27); en edición `updateProductoMenuFecha(id, fecha)` envía solo `{ fecha }` (MDD-28).
  - Escenarios: MDD-25, MDD-26, MDD-27, MDD-28.

- [x] **4.5 Pantalla y listado del menú del día** — Archivos: `Frontend/src/features/daily-menu/{DailyMenuFormPage,DailyMenusTab,useDailyMenusList}.ts(x)`. Depende de 4.4.
  - `DailyMenuFormPage`: selector de menús activos en el alta; en edición, `Input` deshabilitado con `state.registro?.menu_del_dia_nombre` (campo "Menú del día") y alerta si `menu_del_dia_dado_de_baja`. `DailyMenusTab`: columnas Fecha y "Menú del día" (nombre y `Badge` "Dado de baja"), sin columna Tipo. `useDailyMenusList` filtra por nombre y fecha, sin `tipoLabel`.
  - Escenarios: MDD-26, MDD-28, MDD-29.

- [x] **4.6 Verificación final del frontend** — Archivos: ninguno. Depende de 4.3, 4.5.
  - `npm run build` y `npm run lint` en verde. Lista manual (con backend del PR 2 y base recreada):
    - [ ] (manual, pendiente de ejecutar en navegador) MDD-44/45/46: alta, listado de activos y edición de un menú del día desde Productos.
    - [ ] (manual, pendiente de ejecutar en navegador) MDD-48: la etiqueta del tipo es distinta de la del menú ejecutivo.
    - [ ] (manual, pendiente de ejecutar en navegador) MDD-25/26: el alta del menú del día envía `menu_del_dia_id` y `fecha` (sin `producto_id`) y el selector excluye menús dados de baja.
    - [ ] (manual, pendiente de ejecutar en navegador) MDD-27: un 409 (fecha ocupada o menú dado de baja) muestra el mensaje del backend y conserva los valores del formulario.
    - [ ] (manual, pendiente de ejecutar en navegador) MDD-28: la edición muestra el menú deshabilitado y la pestaña de red muestra `PUT` con cuerpo `{ fecha }`.
    - [ ] (manual, pendiente de ejecutar en navegador) MDD-29: el listado muestra nombre y fecha, con la insignia "Dado de baja" en la fila correspondiente.
    - [ ] (manual, pendiente de ejecutar en navegador) MDD-47: la baja de un menú con fecha vigente muestra las fechas en el `Alert` y el menú permanece en el listado.
  - Nota de apply: `tsc` sin errores en `src/features/**`; `npm run build` falla solo por `react-router-dom` ausente en `src/pages/*` y `npm run lint` solo por `src/ui.tsx` (ambos preexistentes, sin tocar). Checklist manual no ejecutable sin navegador.
  - `[COMMIT]` (Fase 4 completa; PR 3 cerrable aquí).

---

## Fase 5: Paso manual de base local

- [x] **5.1 Reinicio de la base SQLite local (paso manual documentado, no es código)** — `create_all` crea `menu_del_dia` pero no altera `producto_menu` existente (cambia `producto_id` por `menu_del_dia_id`). Antes de probar contra una base local: eliminar la tabla `producto_menu` o borrar y recrear `Backend/app.db` (y `Backend/restaurante.db` si se usa) y reiniciar la aplicación; los datos previos se descartan por decisión del alcance. Las pruebas automáticas usan SQLite en memoria y no requieren este paso. Registrar el paso en la descripción del PR 2.

---

## Resumen

| Fase | PR | Tareas | Commits sugeridos |
|------|----|--------|-------------------|
| 1 Subtipo `MenuDelDia` y CRUD | PR 1 | 1.1-1.4 | tras 1.4 |
| 2 FK y reescritura de `productos_menu` | PR 2 (2a) | 2.1-2.5 | tras 2.5 |
| 3 Regla de baja | PR 2 (2b) | 3.1-3.4 | tras 3.4 |
| 4 Frontend | PR 3 | 4.1-4.6 | tras 4.6 |
| 5 Reinicio de la base local | manual | 5.1 | n/a |

Total: 5 fases, 24 tareas.

Paralelismo: dentro de la Fase 2, 2.2 `||` 2.1 no es seguro (2.2 depende de la fábrica y del modelo); dentro de la Fase 4, 4.2/4.3 `||` 4.4/4.5 (archivos disjuntos en `products/` y `daily-menu/`, ambas ramas dependen de 4.1). El resto es secuencial porque comparte `Backend/tests/conftest.py`, `Backend/src/productos/services.py` y `Backend/src/productos_menu/services.py`. Las Fases 1, 2 y 3 se aplican en orden; la Fase 3 requiere la FK de la Fase 2.

---

## Anexo A: Trazabilidad de escenarios

### daily-menu-management (MDD-01..29)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| MDD-01 | La relación es bidireccional | 2.1 |
| MDD-02 | La respuesta expone solo id, menu_del_dia_id y fecha | 2.2, 2.4 |
| MDD-03 | Un MenuDelDia sin fechas es válido | 2.1 |
| MDD-04 | Alta válida | 2.3, 2.4 |
| MDD-05 | Un id de producto de otro subtipo se rechaza | 2.3, 2.4 |
| MDD-06 | menu_del_dia_id ausente | 2.2, 2.4 |
| MDD-07 | menu_del_dia_id no entero | 2.2, 2.4 |
| MDD-08 | MenuDelDia inexistente | 2.3, 2.4 |
| MDD-09 | MenuDelDia dado de baja | 2.3, 2.4 |
| MDD-10 | Fecha ocupada | 2.3, 2.4 |
| MDD-11 | Esquema inválido prevalece sobre inexistente | 2.4 |
| MDD-12 | Inexistente prevalece sobre fecha ocupada | 2.3, 2.4 |
| MDD-13 | Dado de baja prevalece sobre fecha ocupada | 2.3, 2.4 |
| MDD-14 | Una solicitud rechazada no cambia nada | 2.3, 2.4 |
| MDD-15 | Menú del día dado de baja en el PUT | 2.3, 2.4 |
| MDD-16 | menu_del_dia_id en el cuerpo se ignora | 2.2, 2.3, 2.4 |
| MDD-17 | Dado de baja prevalece sobre fecha ocupada en el PUT | 2.3, 2.4 |
| MDD-18 | El borrado no verifica el estado del MenuDelDia | 2.3, 2.4 |
| MDD-19 | Los registros pasados permanecen tras la baja | 3.2, 3.3 |
| MDD-20 | La respuesta de MenuDelDia no incluye fechas | 1.2, 1.3 |
| MDD-21 | El listado incluye los datos del menú del día | 2.2, 2.3, 2.4 |
| MDD-22 | El listado incluye menús dados de baja | 2.3, 2.4 |
| MDD-23 | La consulta por id coincide con el listado | 2.3, 2.4 |
| MDD-24 | Un MenuDelDia con varias fechas | 2.1, 2.3, 2.4 |
| MDD-25 | Alta eligiendo un MenuDelDia | 4.4, 4.6 |
| MDD-26 | El selector excluye menús dados de baja | 4.4, 4.5, 4.6 |
| MDD-27 | Fecha ocupada o menú dado de baja se informan | 4.4, 4.6 |
| MDD-28 | Edición solo de la fecha | 4.4, 4.5, 4.6 |
| MDD-29 | El listado muestra el nombre del menú del día | 4.5, 4.6 |

### product-catalog (MDD-30..48)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| MDD-30 | El registro de tipos contiene seis subtipos | 1.1 |
| MDD-31 | MenuDelDia y MenuEjecutivo son tipos distintos | 1.1, 1.3 |
| MDD-32 | Crear un MenuDelDia | 1.2, 1.3 |
| MDD-33 | Crear con seccion_id | 1.2, 1.3 |
| MDD-34 | Validación de campos comunes | 1.2, 1.3 |
| MDD-35 | Nombre activo duplicado | 1.2, 1.3 |
| MDD-36 | Listar solo activos | 1.2, 1.3 |
| MDD-37 | Listado vacío y sin mezcla de subtipos | 1.3 |
| MDD-38 | Obtener por id un MenuDelDia dado de baja | 1.2, 1.3 |
| MDD-39 | Id de otro subtipo o inexistente | 1.3 |
| MDD-40 | PUT como reemplazo completo | 1.2, 1.3 |
| MDD-41 | Prioridad 422 sobre 404 en el PUT | 1.3 |
| MDD-42 | PUT sobre un id inexistente | 1.3 |
| MDD-43 | El MenuDelDia acepta y rechaza seccion_id en el PUT | 1.2, 1.3 |
| MDD-44 | Alta desde la interfaz de productos | 4.1, 4.2, 4.6 |
| MDD-45 | Listado de menús del día | 4.1, 4.2, 4.6 |
| MDD-46 | Edición de un MenuDelDia | 4.1, 4.2, 4.6 |
| MDD-47 | Baja bloqueada informada | 4.3, 4.6 |
| MDD-48 | Etiqueta del tipo menu_del_dia | 4.1, 4.6 |

### product-logical-delete (MDD-49..62)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| MDD-49 | Baja bloqueada con fecha futura (DELETE) | 3.1, 3.2, 3.3 |
| MDD-50 | Baja bloqueada con fecha de hoy | 3.2, 3.3 |
| MDD-51 | Baja bloqueada vía PUT | 3.2, 3.3 |
| MDD-52 | Baja permitida con solo fechas pasadas | 3.2, 3.3 |
| MDD-53 | Baja permitida sin fechas | 3.2, 3.3 |
| MDD-54 | Múltiples bloqueantes | 3.1, 3.2, 3.3 |
| MDD-55 | El límite depende de la fecha fijada para hoy | 3.2 |
| MDD-56 | Liberar la fecha desbloquea la baja | 3.2, 3.3 |
| MDD-57 | Baja repetida idempotente | 3.2, 3.3 |
| MDD-58 | Invariante tras una baja bloqueada | 3.2, 3.3 |
| MDD-59 | Asignar fecha a un menú dado de baja | 2.3, 2.4, 3.3 |
| MDD-60 | Reactivar permite asignar fechas de nuevo | 3.3 |
| MDD-61 | Conflicto de nombre en la reactivación | 3.3 |
| MDD-62 | Los registros ProductoMenu no afectan la baja de otros subtipos | 3.2, 3.3 |

El Anexo A es la numeración normativa; los nombres de prueba usan el id (`test_mdd_NN_...`).

## Escenarios sin tarea asignada

Ninguno: los 62 escenarios MDD están mapeados. Las tareas 3.4 y 4.6 verifican la cobertura backend y frontend respectivamente.
