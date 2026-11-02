# Tareas: Ids de Productos en la Respuesta de Sección

Cambio: `secciones-productos-ids`. Entradas: `proposal.md`, `design.md`, `specs/section-management/spec.md` (delta: 17 escenarios IDS-01..17; SEC-02, SEC-22 y SEC-30 se actualizan). Comando de pruebas: `cd Backend && python -m pytest`. Los escenarios se numeran en el Anexo A.

**Nota operativa**: el cambio no altera el esquema de base de datos (la propiedad no es columna), por lo que `Backend/app.db` no se recrea. Las pruebas usan SQLite en memoria. No se modifica ningún archivo de `.atl/`, `.claude/` ni de `Backend/app.db`.

## Orden de las fases y suite en verde

Las fases siguen la dependencia real del código:

- La Fase 1 agrega la propiedad `Seccion.productos_ids` y sus pruebas unitarias. Es aditiva: ninguna respuesta HTTP cambia todavía.
- La Fase 2 agrega `productos_ids` a `SeccionRespuesta` y, en la misma unidad atómica, actualiza las pruebas existentes que comparan respuestas exactas (SEC-02, SEC-25, POS-01 y toda otra igualdad `== {...}` de una sección). Agregar el campo antes de actualizar esas pruebas dejaría la suite en rojo; por eso ambas cosas entran juntas, con el RED escrito primero.
- La Fase 3 agrega las pruebas HTTP de comportamiento. Con el código ya completo tras la Fase 2, casi todas nacen en verde (caracterización) y fijan el contrato.
- La Fase 4 verifica la suite completa y la trazabilidad.

## Pronóstico de carga de revisión

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | 450 a 650 (aprox. 5 % código, 95 % pruebas) |
| Riesgo frente al presupuesto de 400 líneas | Medio |
| PR encadenados recomendados | Opcional |
| División sugerida | PR 1 (Fases 1-2: código y pruebas existentes) → PR 2 (Fases 3-4: pruebas HTTP y verificación) |
| Estrategia de entrega | ask-on-risk |
| Estrategia de cadena | pending |

Decision needed before apply: No
Chained PRs recommended: No (opcional)
Chain strategy: pending
400-line budget risk: Medium

### Unidades de trabajo sugeridas

| Unidad | Objetivo | PR probable | Comando de prueba focalizado | Límite de reversión |
|--------|----------|-------------|------------------------------|---------------------|
| 1 | Propiedad del modelo, campo de respuesta y pruebas existentes actualizadas | PR 1 | `cd Backend && python -m pytest tests/secciones tests/productos` | `models.py`, `schemas.py` |
| 2 | Pruebas HTTP, conteo de sentencias, importaciones y trazabilidad | PR 2 | `cd Backend && python -m pytest` | Solo archivos de prueba |

## Convenciones

- **TDD estricto**: cada tarea tiene un paso RED (pruebas que fallan por el motivo correcto) y un paso GREEN (código mínimo), con REFACTOR opcional en verde. Las pruebas de **caracterización** (comportamiento que ya se cumple o que el cambio no debe romper) nacen en verde y se rotulan **(caracterización, nace verde)**; en ellas el RED consiste en registrar la línea base verde antes de editar y el GREEN en mantenerla. Cuando una prueba de caracterización protege una regla sensible (p. ej. el filtro de dados de baja), el escritor DEBE comprobar su sensibilidad invirtiendo temporalmente la condición en la propiedad y reponiéndola después; no se deja ningún cambio residual.
- Nombres de prueba: `test_ids_NN_<descripcion>` para los escenarios IDS; las pruebas de apoyo sin escenario usan `test_productos_ids_<descripcion>`. Los SEC-xx modificados conservan su prefijo `test_sec_NN`.
- Niveles: **U** = unidad (modelo o esquema), **H** = HTTP con `TestClient`, **BD** = integración con SQLite en memoria.
- Los productos de prueba se crean con las fábricas y fixtures existentes de `Backend/tests/` (localizar con `rg "def crear_" Backend/tests`); no se duplican helpers. Los cinco subtipos se crean con sus constructores reales.
- `[COMMIT]` = unidad confirmable con la suite en verde; commits convencionales, sin atribución de IA.
- Un solo escritor: varias tareas modifican `test_router.py`.

---

## Fase 1: Propiedad del modelo

- [x] **1.1 `Seccion.productos_ids`: vacío, filtro de baja y orden** — Archivos: `Backend/src/secciones/models.py`, `Backend/tests/secciones/test_modelos.py`.
  - RED (U/BD): `test_ids_02_seccion_sin_productos_devuelve_lista_vacia_en_el_modelo`; `test_ids_06_modelo_incluye_solo_productos_activos` (Plato activo, Bebida dada de baja y Postre activo → solo los activos; IDS-06 y IDS-07 a nivel modelo con una sección con solo productos dados de baja → `[]`); `test_ids_08_modelo_devuelve_ids_ascendentes` (productos insertados en orden 12, 10, 11 → `[10, 11, 12]`, sin repetidos); `test_ids_15_modelo_ignora_productos_de_otras_secciones_y_sin_seccion`. Fallan con `AttributeError` porque la propiedad no existe.
  - GREEN: propiedad de solo lectura en `Seccion` con el contrato del diseño: `sorted(p.id for p in self.productos if not p.dado_de_baja)`. Sin importar `src.productos`.
  - Escenarios (U): IDS-06, IDS-07, IDS-08, IDS-15 (nivel modelo); soporte de IDS-02.

- [x] **1.2 Subtipos y combo vencido en el modelo (caracterización, nace verde)** — Archivos: `Backend/tests/secciones/test_modelos.py`. Depende de 1.1.
  - RED (caracterización): línea base verde de `cd Backend && python -m pytest tests/secciones`.
  - GREEN: `test_ids_09_modelo_cuenta_los_cinco_subtipos` (Plato, Bebida, Postre, MenuEjecutivo y ComboPromocion activos → los cinco ids, ascendentes) y `test_ids_10_modelo_cuenta_combo_vencido_pero_activo` (`fecha_hasta` de ayer, `dado_de_baja = false` → figura). Pasan sin código nuevo: la propiedad no distingue subtipos ni vigencia. Comprobación de sensibilidad: filtrar por vigencia haría fallar IDS-10.
  - Escenarios (U): IDS-09, IDS-10.
  - `[COMMIT]` (Fase 1 completa; suite en verde, ninguna respuesta HTTP cambió).

---

## Fase 2: Esquema de respuesta y pruebas existentes

- [x] **2.1 `SeccionRespuesta.productos_ids` y actualización de las pruebas que comparan respuestas exactas** — Archivos: `Backend/src/secciones/schemas.py`, `Backend/tests/secciones/test_schemas.py`, `Backend/tests/secciones/test_router.py`, y todo otro archivo con igualdades exactas de una respuesta de sección (localizar con `rg "== \{" Backend/tests/secciones Backend/tests/productos` y `rg '"/secciones' Backend/tests`). Depende de 1.2. Unidad atómica: el campo y las pruebas existentes entran juntos para que la suite no quede en rojo entre commits.
  - RED (U/H): en `test_schemas.py`, el conjunto de `model_fields` incluye `productos_ids` después de `posicion` y `model_validate` de un `SimpleNamespace` con `productos_ids=[...]` lo copia (`test_productos_ids_esquema_expone_el_campo`); las igualdades exactas de SEC-22 (respuesta con `productos_ids: []`), SEC-25, POS-01 y toda otra comparación `== {...}` de una sección agregan `productos_ids: []`; SEC-02 se reescribe como `test_sec_02_la_respuesta_incluye_productos_ids_y_no_el_estado_de_baja` (sección con un Plato activo → `productos_ids == [id_del_plato]`, sin `dado_de_baja` ni objetos de producto). Fallan por diferencia de claves y por campo ausente.
  - GREEN: `productos_ids: list[int]` en `SeccionRespuesta`, después de `posicion` (se lee por `from_attributes`). Todas las pruebas actualizadas pasan y el resto de la suite sigue en verde.
  - Escenarios (U/H): SEC-02, SEC-22, SEC-25 (respuesta exacta), POS-01; soporte de IDS-01.

- [x] **2.2 Respuesta de POST y GET con `productos_ids` (caracterización, nace verde)** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de 2.1.
  - RED (caracterización): línea base verde de `cd Backend && python -m pytest tests/secciones tests/productos`.
  - GREEN: `test_ids_01_productos_ids_es_lista_de_enteros` (dos productos activos; cada elemento es `int` y la respuesta no contiene `precio`, `dado_de_baja` ni claves de producto); `test_ids_02_el_alta_devuelve_productos_ids_vacio` (POST → 201 y `productos_ids == []`); `test_ids_03_la_consulta_devuelve_los_ids_de_los_productos_activos` (sección con Plato activo → `[10]` según el id real); `test_sec_22_obtener_una_seccion_existente_incluye_productos_ids` (200 con `id`, `nombre`, `subtitulo`, `posicion` y `productos_ids`). Pasan sin código nuevo.
  - Escenarios (H): IDS-01, IDS-02, IDS-03, SEC-22.
  - `[COMMIT]` (Fase 2 completa; PR 1 cerrable aquí).

---

## Fase 3: Comportamiento HTTP

- [x] **3.1 Mezcla de activos e inactivos, orden y otras secciones (caracterización, nace verde)** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de 2.2.
  - RED (caracterización): línea base verde.
  - GREEN: `test_ids_06_get_incluye_solo_productos_activos` (Plato activo 10, Bebida dada de baja 11, Postre activo 12 → `[10, 12]`); `test_ids_07_seccion_con_solo_productos_dados_de_baja_devuelve_lista_vacia`; `test_ids_08_get_devuelve_ids_ascendentes` (asignados en el orden 12, 10, 11 → `[10, 11, 12]`); `test_ids_15_get_no_incluye_productos_de_otras_secciones_ni_sin_seccion` (A con Plato, B con Postre, Bebida sin sección → A devuelve solo el Plato). Comprobación de sensibilidad del filtro de baja y del orden según la convención.
  - Escenarios (H): IDS-06, IDS-07, IDS-08, IDS-15.

- [x] **3.2 Los cinco subtipos y el combo vencido por HTTP (caracterización, nace verde)** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de 3.1.
  - RED (caracterización): línea base verde.
  - GREEN: `test_ids_09_get_cuenta_los_cinco_subtipos` (los cinco productos activos asignados mediante los endpoints reales de cada subtipo → cinco ids ascendentes); `test_ids_10_get_incluye_combo_vencido_pero_activo` (`fecha_hasta` de ayer, activo → figura).
  - Escenarios (H): IDS-09, IDS-10.

- [x] **3.3 Baja, reactivación, movimiento y desasignación de productos (caracterización, nace verde)** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de 3.2.
  - RED (caracterización): línea base verde. Cada prueba consulta `GET /secciones/{id}` antes y después de la acción sobre el producto, para confirmar que no se necesita ninguna acción sobre la sección.
  - GREEN: `test_ids_11_dar_de_baja_un_producto_lo_quita` (DELETE del Plato → `[11]` y el Plato conserva su `seccion_id`); `test_ids_12_reactivar_un_producto_lo_reincorpora` (PUT del producto con `dado_de_baja: false` → `[10, 11]`); `test_ids_13_cambiar_la_seccion_de_un_producto_lo_mueve` (PUT con otro `seccion_id` → A `[]` y B `[10]`); `test_ids_14_desasignar_un_producto_lo_quita` (`seccion_id: null` → `[]`).
  - Escenarios (H): IDS-11, IDS-12, IDS-13, IDS-14.

- [x] **3.4 Borrado de sección y ausencia de listado por sección (caracterización, nace verde)** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de 3.3.
  - RED (caracterización): línea base verde.
  - GREEN: `test_ids_16_no_quedan_ids_obsoletos_tras_borrar_y_crear_una_seccion` (borrar la sección con un Plato activo, crear otra → `[]` y el Plato sigue existiendo con `seccion_id = null`); `test_ids_17_no_existe_listado_de_productos_por_seccion` (`GET /secciones/{id}/productos` → 404).
  - Escenarios (H): IDS-16, IDS-17.

- [x] **3.5 Frescura en POST y PUT, ignorar `productos_ids` del cuerpo y rechazos (caracterización, nace verde)** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de 3.4.
  - RED (caracterización): línea base verde. Estas pruebas fijan la decisión 5 del diseño (`expire_on_commit=True`); si alguna falla, la corrección consiste en `sesion.refresh` en el servicio (cambio mínimo) o en revisar el `expire_on_commit` de la sesión.
  - GREEN: `test_ids_02_el_alta_devuelve_lista_vacia_aunque_existan_otros_productos` (productos con `seccion_id = null` y asignados a otras secciones → POST devuelve `[]`); `test_ids_04_el_put_devuelve_el_estado_persistido` (Plato activo 10 y Postre dado de baja 11 asignados → PUT devuelve `[10]` y el GET siguiente es idéntico); `test_ids_05_enviar_productos_ids_en_el_put_no_cambia_la_asignacion` (cuerpo con `productos_ids = [11]` → 200, `[10]`, el Plato conserva su `seccion_id` y el Postre conserva `null`); prueba de apoyo `test_productos_ids_el_alta_ignora_productos_ids_del_cuerpo` (POST con `productos_ids = [11]` → 201, `[]`, el producto sigue sin sección); `test_sec_25_el_put_incluye_productos_ids_vigentes` (respuesta exacta del PUT con productos asignados); `test_sec_30_la_modificacion_no_altera_los_productos_asignados` (el Plato conserva su `seccion_id` y su id figura en `productos_ids` de la respuesta); `test_productos_ids_solicitudes_rechazadas_no_alteran_el_get` (POST y PUT rechazados con 409 y 422 dejan el `GET` con los mismos `productos_ids`).
  - Escenarios (H): IDS-02, IDS-04, IDS-05; SEC-25, SEC-30.

- [x] **3.6 Conteo de sentencias SQL (caracterización, nace verde)** — Archivos: `Backend/tests/secciones/test_modelos.py`. Depende de 3.5.
  - RED (caracterización): línea base verde.
  - GREEN: `test_productos_ids_emite_un_unico_select_sobre_producto` con un listener `before_cursor_execute` sobre el motor de prueba: con una sección que tenga productos de los cinco subtipos, leer `productos_ids` emite exactamente un `SELECT` y ninguna sentencia consulta las tablas de subtipos (`plato`, `bebida`, `postre`, `menu_ejecutivo`, `combo_promocion`; nombres reales según los modelos). Se retira el listener al terminar la prueba. Cubre las decisiones 2 y 3 del diseño (sin N+1, sin cargas por fila).
  - Escenarios: soporte de IDS-09.

- [x] **3.7 Verificación de importaciones (caracterización, nace verde)** — Archivos: `Backend/tests/secciones/test_excepciones.py`. Depende de 1.1.
  - RED (caracterización): línea base verde (hoy el archivo solo verifica `exceptions`).
  - GREEN: `test_productos_ids_secciones_no_importa_productos` recorre con `ast` el código fuente de `src.secciones.models`, `schemas`, `services` y `router` y comprueba que ninguno importa `src.productos` (ni `from src import productos`). Comprobación de sensibilidad: agregar temporalmente un import de `src.productos` en `models.py` debe hacerla fallar; se repone de inmediato.
  - Escenarios: restricción de dirección de importaciones (diseño, matriz de pruebas).
  - `[COMMIT]` (Fase 3 completa).

---

## Fase 4: Verificación final y trazabilidad

- [x] **4.1 Suite completa y grafo de importaciones** — Archivos: ninguno. Depende de Fase 3.
  - RED/GREEN: ejecutar `cd Backend && python -m pytest` en verde; `configure_mappers()` sin errores; `rg "from src.productos|import src.productos" Backend/src/secciones` sin resultados; `git status` no muestra cambios en `Backend/src` fuera de `secciones/models.py` y `secciones/schemas.py`, ni en `.atl/` ni `.claude/`.
  - Hecho cuando: suite en verde y el diff de código fuente se limita a los dos archivos previstos.

- [x] **4.2 Trazabilidad de escenarios** — Archivos: ninguno (solo se agregan pruebas en archivos existentes). Depende de 4.1.
  - RED/GREEN: revisar el Anexo A. Para cada uno de los 17 escenarios IDS debe existir una prueba cuyo nombre contenga `test_ids_NN` con nivel H (o BD); para SEC-02, SEC-22 y SEC-30 debe existir la prueba `test_sec_NN` correspondiente. Comprobar con `rg "def test_ids_" Backend/tests/secciones` y `rg "def test_sec_(02|22|30)" Backend/tests/secciones`. Listar los huecos y cerrarlos con RED → GREEN o registrarlos como riesgo.
  - Hecho cuando: el listado sin cobertura está vacío y `python -m pytest` pasa.
  - `[COMMIT]` final (verify queda para `sdd-verify`).

---

## Resumen

| Fase | Tareas | Commits sugeridos |
|------|--------|-------------------|
| 1 Propiedad del modelo | 1.1-1.2 | tras 1.2 |
| 2 Esquema de respuesta y pruebas existentes | 2.1-2.2 | tras 2.2 |
| 3 Comportamiento HTTP | 3.1-3.7 | tras 3.7 |
| 4 Verificación final y trazabilidad | 4.1-4.2 | tras 4.2 |

Total: 4 fases, 13 tareas.

Paralelismo: 3.7 solo depende de 1.1 y 3.6 solo del modelo, pero todo se mantiene secuencial para un único escritor porque 3.1-3.5 comparten `test_router.py` y 1.1, 1.2 y 3.6 comparten `test_modelos.py`. La Fase 2 no admite paralelismo (unidad atómica).

---

## Anexo A: Trazabilidad de escenarios

### section-management, delta de ids de productos (IDS, 17 escenarios)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| IDS-01 | productos_ids es una lista de enteros | 2.1, 2.2 |
| IDS-02 | El alta devuelve productos_ids vacío | 1.1, 2.2, 3.5 |
| IDS-03 | La consulta devuelve los ids de los productos activos | 2.2 |
| IDS-04 | La respuesta del PUT refleja el estado persistido | 3.5 |
| IDS-05 | Enviar productos_ids en el PUT no cambia la asignación | 3.5 |
| IDS-06 | Solo figuran los productos activos cuando hay activos y dados de baja | 1.1, 3.1 |
| IDS-07 | Una sección con solo productos dados de baja devuelve lista vacía | 1.1, 3.1 |
| IDS-08 | Los ids se devuelven en orden ascendente | 1.1, 3.1 |
| IDS-09 | Cuentan los cinco subtipos | 1.2, 3.2, 3.6 |
| IDS-10 | Un combo vencido pero activo figura | 1.2, 3.2 |
| IDS-11 | Dar de baja un producto lo hace desaparecer | 3.3 |
| IDS-12 | Reactivar un producto lo hace reaparecer | 3.3 |
| IDS-13 | Cambiar la sección de un producto lo mueve entre secciones | 3.3 |
| IDS-14 | Desasignar un producto lo quita de la sección | 3.3 |
| IDS-15 | No figuran productos de otras secciones ni sin sección | 1.1, 3.1 |
| IDS-16 | No quedan ids obsoletos tras borrar y crear una sección | 3.4 |
| IDS-17 | No existe un listado de productos por sección | 3.4 |

### Escenarios SEC modificados por el delta

| ID | Efecto | Tarea(s) |
|----|--------|----------|
| SEC-02 | La respuesta incluye `productos_ids` con el id del Plato y no incluye `dado_de_baja` | 2.1 |
| SEC-22 | La respuesta de la consulta incluye `productos_ids` | 2.1, 2.2 |
| SEC-30 | La modificación conserva el `seccion_id` del Plato y su id figura en `productos_ids` | 3.5 |

### Escenarios existentes con respuesta exacta afectada (resultado esperado sin cambios)

| ID | Efecto | Tarea(s) |
|----|--------|----------|
| POS-01 | La respuesta exacta incluye `productos_ids` | 2.1 |
| SEC-25 | La respuesta exacta del PUT incluye `productos_ids` | 2.1, 3.5 |

### Requisitos de diseño sin escenario propio

| Tema | Tarea(s) |
|------|----------|
| Conteo de sentencias SQL (decisiones 2 y 3) | 3.6 |
| Dirección de importaciones (`secciones` no importa `productos`) | 3.7, 4.1 |
| Frescura tras commit (decisión 5) | 3.5 |

El Anexo A es la numeración normativa; los nombres de prueba usan el id (`test_ids_NN_...`).

## Escenarios sin tarea asignada

Ninguno: los 17 escenarios IDS y los tres SEC modificados (SEC-02, SEC-22, SEC-30) están mapeados. La tarea 4.2 verifica que cada uno tenga su prueba.
