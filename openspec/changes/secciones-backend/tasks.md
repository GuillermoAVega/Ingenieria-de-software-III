# Tareas: Secciones Backend

Cambio: `secciones-backend`. Entradas: `proposal.md`, `design.md`, `specs/section-management/spec.md` (SEC, 44 escenarios), `specs/product-catalog/spec.md` (CAT-S, 28 escenarios). Comando de pruebas: `cd Backend && python -m pytest`. Los escenarios se numeran en el Anexo A.

**Nota operativa (base local)**: `create_all` no agrega columnas a una tabla existente. Antes de iniciar la aplicación o de verificar manualmente, se debe borrar `Backend/app.db` (archivo local no versionado) para que se recree con la tabla `seccion` y la columna `producto.seccion_id`. Las pruebas usan SQLite en memoria y no se ven afectadas. La tarea 6.3 repite el recordatorio.

## Pronóstico de carga de revisión

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | 1.800 a 2.500 (aprox. 40 % código, 60 % pruebas) |
| Riesgo frente al presupuesto de 400 líneas | Alto |
| PR encadenados recomendados | Sí |
| División sugerida | PR 1 (Fases 1-3) → PR 2 (Fase 4) → PR 3 (Fases 5-6) |
| Estrategia de entrega | ask-on-risk |
| Estrategia de cadena | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Unidades de trabajo sugeridas

| Unidad | Objetivo | PR probable | Comando de prueba focalizado | Arnés de ejecución | Límite de reversión |
|--------|----------|-------------|------------------------------|--------------------|---------------------|
| 1 | Módulo `secciones` completo a nivel servicio (texto, modelo/FK, esquemas, servicios) | PR 1 | `cd Backend && python -m pytest tests/test_texto.py tests/secciones` | N/A: sin HTTP todavía | `Backend/src/texto.py`, `Backend/src/secciones/`, FK de `Backend/src/productos/models.py` |
| 2 | Integración en productos (validación compartida, orden de validación en menús y combos) | PR 2 | `cd Backend && python -m pytest tests/productos` | N/A: sin HTTP todavía | Cambios en `productos/services.py`, `menus_ejecutivos/services.py`, `combos/services.py` |
| 3 | Routers, manejadores, `main.py` y verificación final | PR 3 | `cd Backend && python -m pytest` | `rm Backend/app.db`, iniciar la app y `POST/GET/DELETE /secciones` | Routers y registro en `Backend/src/main.py` |

## Convenciones

- **TDD estricto**: cada tarea sigue RED (pruebas que fallan por el motivo correcto) → GREEN (código mínimo) → REFACTOR opcional con la suite en verde. Las pruebas de **caracterización** (comportamiento ya existente que el cambio no debe romper) pueden nacer en verde; se rotulan así en la tarea.
- Nombres de prueba: `test_sec_NN_<descripcion>` y `test_cat_s_NN_<descripcion>`; a nivel servicio o esquema se usa el mismo prefijo con el id del escenario.
- Niveles: **E** = esquema/unidad, **S** = servicio, **H** = HTTP con `TestClient`, **BD** = integración con SQLite. El Anexo A exige al menos una prueba H (o BD) por escenario cuando aplica.
- `[COMMIT]` = unidad confirmable con la suite en verde; commits convencionales, sin atribución de IA.
- Un solo escritor: varias tareas modifican `productos/services.py`, `productos/router.py` y `Backend/tests/conftest.py`.

---

## Fase 1: Texto compartido, modelo y clave foránea

- [x] **1.1 `normalizar_nombre` compartido** — Archivos: `Backend/src/texto.py`, `Backend/src/productos/services.py`, `Backend/tests/test_texto.py`.
  - RED: `test_texto_normalizar_nombre_recorta_y_casefold` (`"  Entrádas "` → `"entrádas"`), distingue tildes, y `from src.productos.services import normalizar_nombre` sigue disponible y es el mismo objeto que `src.texto.normalizar_nombre`.
  - GREEN: crear `texto.py`; `productos/services.py` la importa desde ahí y elimina su definición local. La suite de productos existente permanece en verde.
  - Escenarios: soporte de SEC-11..14.

- [x] **1.2 Constantes de secciones** — Archivos: `Backend/src/secciones/__init__.py`, `Backend/src/secciones/constants.py`, `Backend/tests/secciones/__init__.py`, `Backend/tests/secciones/test_constantes.py`. `||` con 1.1.
  - RED: `test_constantes_valores` (`NOMBRE_MAX == 100`, `SUBTITULO_MAX == 200`, `PREFIJO == "/secciones"`).
  - GREEN: crear paquete y `constants.py`.
  - Escenarios: soporte de SEC-07..10.

- [x] **1.3 Modelo `Seccion`, FK `producto.seccion_id` y relación bidireccional** — Archivos: `Backend/src/secciones/models.py`, `Backend/src/productos/models.py`, `Backend/src/productos/registro.py`, `Backend/tests/secciones/test_modelos.py`, `Backend/tests/productos/test_registro.py`. Depende de 1.1, 1.2.
  - RED: `test_sec_01_mappers_se_configuran_con_la_nueva_entidad` (`configure_mappers()` tras importar solo `src.productos.registro`, sin error); tabla `seccion` con columnas y `subtitulo` nulo; índice `ux_seccion_nombre_normalizado` rechaza con `IntegrityError` dos filas con igual `nombre_normalizado`; `producto.seccion_id` existe, es anulable y tiene FK a `seccion.id` con `ON DELETE SET NULL`; `Seccion.productos` y `Producto.seccion` son bidireccionales (asignar de un lado y leer del otro) con un Plato; `registro.py` expone `Seccion`.
  - GREEN: `Seccion(ModeloBase)` con `relationship("Producto", back_populates="seccion", passive_deletes=True)` sin importar `productos`; en `Producto`: `seccion_id` (FK, `nullable=True`, `index=True`) y `relationship("Seccion", back_populates="productos")`; `registro.py` agrega `from src.secciones.models import Seccion`.
  - Escenarios: SEC-01.
  - Hecho cuando: suite completa en verde; ningún módulo de `src/secciones` importa `src.productos`.

- [x] **1.4 Fixtures: `persistir` compartido y fábrica `crear_seccion`** — Archivos: `Backend/tests/conftest.py`, `Backend/tests/productos/conftest.py`, `Backend/tests/secciones/test_fabrica.py`. Depende de 1.3.
  - RED: `test_fabrica_crear_seccion_persiste_y_calcula_nombre_normalizado` (fábrica ausente → falla); la fábrica acepta `nombre` y `subtitulo` opcional.
  - GREEN: mover `persistir` a `Backend/tests/conftest.py` (REFACTOR sin cambiar aserciones) y agregar la fábrica `crear_seccion`.
  - `[COMMIT]` (Fase 1 completa: texto + modelo + FK).

---

## Fase 2: Esquemas

- [x] **2.1 Esquemas de sección** — Archivos: `Backend/src/secciones/schemas.py`, `Backend/tests/secciones/test_schemas.py`. Depende de 1.2.
  - RED (E): `nombre` `""` (SEC-03), `"   "` (SEC-04) y ausente (SEC-05) → error; `"  Entradas "` → `"Entradas"` (SEC-06); 100 caracteres válido (SEC-07); 101 → error (SEC-08); `subtitulo` de 200 válido (SEC-09); de 201 → error (SEC-10); `"  Para comenzar "` → `"Para comenzar"` (SEC-39); `""` → `None` (SEC-40); `"   "` → `None` (SEC-41); 200 caracteres rodeados de espacios → válido y de 200 (SEC-42); 201 rodeados de espacios → error (SEC-43); `subtitulo` omitido → `None`; `SeccionActualizar` equivale a `SeccionCrear`; `SeccionRespuesta` solo expone `id`, `nombre`, `subtitulo` (SEC-02, parcial) y valida desde atributos.
  - GREEN: `SeccionCrear` con `field_validator(..., mode="before")` que recorta `nombre` y `subtitulo` (este último devuelve `None` si queda vacío) y `Field(min_length=1, max_length=NOMBRE_MAX)` / `Field(max_length=SUBTITULO_MAX)`; `SeccionActualizar = SeccionCrear`; `SeccionRespuesta`.
  - Escenarios (E): SEC-02 (parcial), SEC-03..10, SEC-39..43.

- [x] **2.2 `seccion_id` en los esquemas comunes de producto** — Archivos: `Backend/src/productos/schemas.py`, `Backend/tests/productos/test_schemas.py`. Depende de 1.3. `||` con 2.1.
  - RED (E): `ProductoBase` sin `seccion_id` → `None` (CAT-S-02); con entero válido se conserva; `"abc"` → error de validación (CAT-S-13); `ProductoRespuestaBase` expone `seccion_id` (`None` o entero) y los cinco `*Crear`/`*Actualizar`/`*Respuesta` lo heredan (parametrizado por subtipo).
  - GREEN: `ProductoBase.seccion_id: int | None = None`; `ProductoRespuestaBase.seccion_id: int | None`.
  - Escenarios (E): CAT-S-02, CAT-S-13.
  - `[COMMIT]` (Fase 2 completa).

---

## Fase 3: Servicios de secciones

- [x] **3.1 Excepciones y `obtener_seccion`** — Archivos: `Backend/src/secciones/exceptions.py`, `Backend/src/secciones/services.py`, `Backend/tests/secciones/test_excepciones.py`, `Backend/tests/secciones/test_servicios.py`. Depende de 1.4.
  - RED: `ErrorSeccion` base de `SeccionNoEncontrada` y `NombreSeccionDuplicado`; jerarquía disjunta de `productos.ErrorDominio`; ningún módulo importa FastAPI ni `src.productos`; `test_sec_22_obtener_seccion_existente_devuelve_la_fila`; `test_sec_23_obtener_seccion_inexistente_lanza_no_encontrada`.
  - GREEN: excepciones y `obtener_seccion(sesion, id)`.
  - Escenarios (S): SEC-22, SEC-23.

- [x] **3.2 `crear_seccion` y `_confirmar`** — Archivos: `Backend/src/secciones/services.py`, `Backend/tests/secciones/test_servicios.py`. Depende de 3.1.
  - RED (S): crea con todos los campos y devuelve `id` (SEC-19); sin `subtitulo` queda `None` (SEC-20); persiste `nombre_normalizado`; duplicado exacto (SEC-11), por mayúsculas (SEC-12) y con espacios (SEC-13) → `NombreSeccionDuplicado` sin fila nueva y con rollback; tildes distintas → crea (SEC-14); un `IntegrityError` ajeno a `nombre_normalizado` se propaga sin traducir.
  - GREEN: `crear_seccion` y `_confirmar` (traduce el `IntegrityError` cuyo `orig` menciona `nombre_normalizado`; rollback en todo error).
  - Escenarios (S): SEC-11..14, SEC-19, SEC-20.

- [x] **3.3 `actualizar_seccion`** — Archivos: `Backend/src/secciones/services.py`, `Backend/tests/secciones/test_servicios.py`. Depende de 3.2.
  - RED (S): reemplazo (SEC-25); `subtitulo` omitido → `None` (SEC-26); id inexistente → `SeccionNoEncontrada` (SEC-27); 404 antes que 409 con nombre duplicado e id inexistente (SEC-29); duplicado en modificación → `NombreSeccionDuplicado` y la sección no cambia (SEC-15); conserva el propio nombre (SEC-16); cambio solo de mayúsculas (SEC-17) recalcula `nombre_normalizado`; `subtitulo` ya normalizado a `None` por el esquema se persiste como `null` (SEC-44, nivel servicio); un Plato asignado conserva `seccion_id` (SEC-30).
  - GREEN: `actualizar_seccion` (`obtener` → asignar → `_confirmar`).
  - Escenarios (S): SEC-15..17, SEC-25..27, SEC-29, SEC-30, SEC-44.

- [x] **3.4 `eliminar_seccion`** — Archivos: `Backend/src/secciones/services.py`, `Backend/tests/secciones/test_servicios.py`. Depende de 3.3.
  - RED (S): borra la fila (SEC-31, nivel servicio); id inexistente → `SeccionNoEncontrada` (SEC-32); repetir → `SeccionNoEncontrada` (SEC-33); reutilizar el nombre tras borrar (SEC-18); el borrado no carga `Seccion.productos` (captura de sentencias SQL: un solo `DELETE`, sin `SELECT` sobre `producto`).
  - GREEN: `eliminar_seccion` (`obtener` → `sesion.delete` → commit; rollback en error).
  - Escenarios (S): SEC-18, SEC-31..33.
  - `[COMMIT]` (Fase 3 completa; PR 1 cerrable aquí).

---

## Fase 4: Integración en productos

- [x] **4.1 `SeccionInexistente`** — Archivos: `Backend/src/productos/exceptions.py`, `Backend/tests/productos/test_excepciones.py`. Depende de 1.3.
  - RED: `SeccionInexistente(seccion_id)` hereda de `ErrorDominio`, guarda `seccion_id`, tiene mensaje y no importa FastAPI.
  - GREEN: agregar la clase.
  - Escenarios: soporte de CAT-S-03.

- [x] **4.2 `verificar_seccion`, campos comunes y orden en alta/modificación (Plato, Bebida, Postre)** — Archivos: `Backend/src/productos/services.py`, `Backend/tests/productos/test_seccion_producto.py`. Depende de 4.1, 2.2.
  - RED (S, vía `crear_plato`/`actualizar_plato`, `bebida`, `postre`): alta con sección existente guarda `seccion_id` (CAT-S-01); `seccion_id` inexistente → `SeccionInexistente` sin producto nuevo (CAT-S-03); `None` no consulta; cambiar sección (CAT-S-06); PUT sin `seccion_id` → `None` (CAT-S-07); PUT con inexistente → `SeccionInexistente` y el Plato conserva la sección (CAT-S-08); asignar a producto dado de baja (CAT-S-11); nombre duplicado en otra sección → `NombreDuplicado` (CAT-S-12, caracterización); PUT de id inexistente con sección inexistente → `ProductoNoEncontrado` (CAT-S-14, caracterización); `SeccionInexistente` antes que `NombreDuplicado` (CAT-S-18); rollback en `crear_producto` ante cualquier `ErrorDominio`.
  - GREEN: `verificar_seccion(sesion, seccion_id)`; `asignar_campos_comunes` copia `seccion_id`; `crear_producto`: sección → nombre; `actualizar_producto`: `obtener` → sección → nombre → estado; capturar `ErrorDominio` para el rollback.
  - Escenarios (S): CAT-S-01, 03, 06, 07, 08, 11, 12, 14, 18; soporte de CAT-S-04, 05, 09.

- [x] **4.3 Menú: separar existencia y actividad de componentes** — Archivos: `Backend/src/productos/menus_ejecutivos/services.py`, `Backend/tests/productos/menus_ejecutivos/test_servicios.py`. Depende de 4.2.
  - RED (S): alta y PUT con `seccion_id` válido (CAT-S-04, CAT-S-09 a nivel servicio); `seccion_id` inexistente → `SeccionInexistente` (CAT-S-05); `postre_id` dado de baja más `seccion_id` inexistente en menú activo → `SeccionInexistente` y no `ComponenteInactivo` (CAT-S-17); componente inexistente y sección inexistente → `ComponenteInvalido` primero; componente inactivo con nombre duplicado → `ComponenteInactivo` (CAT-S-19, caracterización); un menú que queda dado de baja no exige componentes activos (regresión CAT-43/CAT-44 del cambio previo).
  - GREEN: `resolver_componentes_menu(..., exigir_activos=False)` → `verificar_seccion` → `verificar_componentes_activos_menu(...)` si el menú queda activo (siempre en el alta); `crear_menu`/`actualizar_menu` capturan `ErrorDominio`.
  - Escenarios (S): CAT-S-04, 05, 09, 17, 19.

- [x] **4.4 Combo: separar validación, `seccion_id` en `_sin_otros_cambios`** — Archivos: `Backend/src/productos/combos/services.py`, `Backend/tests/productos/combos/test_servicios.py`, `Backend/tests/productos/combos/test_servicios_vencido.py`. Depende de 4.3.
  - RED (S): alta con sección (CAT-S-04) e inexistente → `SeccionInexistente` (CAT-S-05); vigente cambia de sección (CAT-S-28) y rechaza inexistente (CAT-S-09); vencido más sección inexistente → `ComboVencidoInmutable` (CAT-S-16); vencido con otra sección (CAT-S-22) o asignada a uno sin sección (CAT-S-23) → `ComboVencidoInmutable` sin cambios; baja con mismo `seccion_id` → OK (CAT-S-24); baja omitiendo `seccion_id` con combo con sección → `ComboVencidoInmutable` (CAT-S-25); baja de combo sin sección (CAT-S-26); `dar_de_baja` (DELETE) no altera `seccion_id` (CAT-S-27); id inexistente en `platos_ids` más Bebida inactiva → `ComponenteInvalido` (CAT-S-20).
  - GREEN: `resolver_componentes_combo(..., exigir_activos=False)` → `verificar_seccion` → `verificar_componentes_activos_combo(...)`; alta: `FechaHastaVencida` → existencia → sección → actividad → nombre; `_sin_otros_cambios` agrega `datos.seccion_id == combo.seccion_id`.
  - Escenarios (S): CAT-S-04, 05, 09, 16, 20, 22..28.
  - `[COMMIT]` (Fase 4 completa; PR 2 cerrable aquí).

---

## Fase 5: Routers y manejadores

- [x] **5.1 Router de secciones, manejadores y `main.py`** — Archivos: `Backend/src/secciones/router.py`, `Backend/src/main.py`, `Backend/tests/secciones/test_router.py`, `Backend/tests/secciones/test_manejadores.py`. Depende de Fase 3.
  - RED (H): `SeccionNoEncontrada` → 404 `{"detail"}` y `NombreSeccionDuplicado` → 409 `{"detail"}`; alta con campos (SEC-19, SEC-20), recorte (SEC-06, SEC-39), límites (SEC-07..10, SEC-42, SEC-43), `nombre` inválido (SEC-03..05), `subtitulo` vacío o de espacios → `null` (SEC-40, SEC-41); duplicados (SEC-11..14), prioridad 422 sobre 409 (SEC-21); `GET /secciones/{id}` (SEC-22, SEC-23) sin lista de productos ni `dado_de_baja` (SEC-02); `GET /secciones` → 405 (SEC-24); PUT (SEC-25, SEC-26, SEC-44), 404 (SEC-27), 422 antes que 404 (SEC-28), 404 antes que 409 (SEC-29), duplicado (SEC-15), propio nombre (SEC-16, SEC-17), productos asignados intactos (SEC-30, usa el endpoint de Plato desde la tarea 5.3 o el ORM); DELETE 204 sin cuerpo y GET posterior 404 (SEC-31), 404 (SEC-32), repetido (SEC-33), reutilización del nombre (SEC-18); la ruta usa `{seccion_id:int}`.
  - GREEN: `APIRouter(prefix=PREFIJO)` con `POST ""` 201, `GET/PUT/DELETE "/{seccion_id:int}"`, `MANEJADORES_EXCEPCIONES`; `main.py` registra el router y recorre ambos diccionarios de manejadores.
  - Escenarios (H): SEC-02..33, SEC-39..44 (SEC-30 se completa en 5.3).

- [x] **5.2 Manejador de `SeccionInexistente`** — Archivos: `Backend/src/productos/router.py`, `Backend/tests/productos/test_manejadores.py`. Depende de 4.1.
  - RED (H): `SeccionInexistente` → 422 con `{"detail": [{"loc": ["body","seccion_id"], "msg": ..., "type": "seccion_inexistente", "ids": [id]}]}`; el manejador de `ErrorConflicto` no la captura.
  - GREEN: entrada en `MANEJADORES_EXCEPCIONES` mediante `_error_de_campo`.
  - Escenarios: soporte de CAT-S-03, 05, 08.

- [x] **5.3 HTTP de Plato, Bebida y Postre con `seccion_id`** — Archivos: `Backend/tests/productos/platos/test_router.py`, `Backend/tests/productos/bebidas/test_router.py`, `Backend/tests/productos/postres/test_router.py`, `Backend/tests/productos/test_seccion_producto_http.py`. Depende de 5.2, 4.2. Sin cambios de código esperados en los routers (los esquemas ya exponen el campo): si una prueba falla, se corrige el cuerpo del router.
  - RED (H): crear con sección (CAT-S-01) y sin ella (CAT-S-02); inexistente → 422 sin producto (CAT-S-03); Bebida y Postre en alta con y sin sección inexistente (CAT-S-04, CAT-S-05, CAT-S-21); PUT cambia (CAT-S-06), omite (CAT-S-07), inexistente conserva (CAT-S-08), dado de baja (CAT-S-11); GET por id expone `seccion_id` (CAT-S-10); mismo nombre en otra sección → 409 (CAT-S-12); `"abc"` → 422 (CAT-S-13); 404 sobre 422 de sección (CAT-S-14); 422 de esquema sobre 422 de sección y el Plato no cambia (CAT-S-15); sección inexistente sobre nombre duplicado (CAT-S-18); un PUT de Plato sin tocar la sección tras `PUT /secciones` conserva `seccion_id` (SEC-30, H).
  - GREEN: ajustes mínimos si algún caso falla.
  - Escenarios (H): CAT-S-01..08, 10..15, 18, 21; SEC-30.

- [x] **5.4 HTTP de MenuEjecutivo con `seccion_id`** — Archivos: `Backend/tests/productos/menus_ejecutivos/test_router.py`. Depende de 5.3, 4.3.
  - RED (H): alta (CAT-S-04) y rechazo (CAT-S-05); PUT 200 y luego 422 con `seccion_id = 999` (CAT-S-09); Postre dado de baja más sección inexistente → 422 (CAT-S-17); "Menú A" con "Menú B" y Postre inactivo → 409 por componente (CAT-S-19).
  - GREEN: ajustes mínimos en el router si falla algún caso.
  - Escenarios (H): CAT-S-04, 05, 09, 17, 19.

- [x] **5.5 HTTP de ComboPromocion con `seccion_id`** — Archivos: `Backend/tests/productos/combos/test_router.py`. Depende de 5.4, 4.4.
  - RED (H): alta (CAT-S-04) y rechazo (CAT-S-05); PUT vigente 200 y luego 422 (CAT-S-09), cambio de sección (CAT-S-28); vencido más sección inexistente → 409 (CAT-S-16); `ComponenteInvalido` sobre inactivo → 422 (CAT-S-20); vencido: cambiar sección 409 (CAT-S-22), asignar 409 (CAT-S-23), baja conservando sección 200 (CAT-S-24), omitiéndola 409 (CAT-S-25), sin sección 200 (CAT-S-26), DELETE conserva sección (CAT-S-27).
  - GREEN: ajustes mínimos en el router si falla algún caso.
  - Escenarios (H): CAT-S-04, 05, 09, 16, 20, 22..28.
  - `[COMMIT]` (Fase 5 completa).

---

## Fase 6: Verificación final y trazabilidad

- [ ] **6.1 Desvinculación a nivel de base de datos (`ON DELETE SET NULL`)** — Archivos: `Backend/tests/productos/test_seccion_producto.py` (sección BD). Depende de Fase 5.
  - RED (BD): `test_sec_34_pragma_foreign_keys_esta_activo` (`PRAGMA foreign_keys` = 1 en el motor de pruebas); `DELETE FROM seccion` crudo deja `seccion_id` NULL con las filas de producto intactas para Plato y Bebida (SEC-34), solo desvincula la sección borrada (SEC-35), los cinco subtipos (SEC-36), combo vencido sin otros cambios (SEC-37) y Postre dado de baja (SEC-38).
  - GREEN: ajustes mínimos si algún caso falla (p. ej. falta `passive_deletes` o el `ondelete`).
  - Escenarios (BD): SEC-34..38.

- [ ] **6.2 Desvinculación vía HTTP** — Archivos: `Backend/tests/secciones/test_router.py` (sección borrado). Depende de 6.1.
  - RED (H): `DELETE /secciones/{id}` y consulta posterior de `GET /productos/platos/{id}` y `GET /productos/bebidas/{id}` con `seccion_id = null` (SEC-34); solo se desvincula la sección borrada (SEC-35); los cinco subtipos (SEC-36); combo vencido (SEC-37); Postre dado de baja (SEC-38).
  - GREEN: sin código esperado.
  - Escenarios (H): SEC-34..38.

- [ ] **6.3 Suite completa y base local** — Archivos: ninguno. Depende de 6.2.
  - Verificar `cd Backend && python -m pytest` en verde y `configure_mappers()` sin errores; `rg "from src.productos" Backend/src/secciones` sin resultados. Borrar `Backend/app.db` local, iniciar la aplicación para recrearla y comprobar `POST /secciones` y `DELETE /secciones/{id}`.
  - Hecho cuando: suite en verde, grafo de importaciones acíclico y base local recreada.

- [ ] **6.4 Trazabilidad de escenarios** — Archivos: ninguno (solo se agregan pruebas en archivos existentes). Depende de 6.3.
  - Revisar el Anexo A: para cada uno de los 72 escenarios (44 SEC + 28 CAT-S) debe existir una prueba cuyo nombre contenga `test_sec_NN` o `test_cat_s_NN`, con nivel H o BD donde aplica. Listar los huecos y cerrarlos con RED → GREEN o registrarlos como riesgo.
  - Hecho cuando: el listado sin cobertura está vacío y `python -m pytest` pasa.
  - `[COMMIT]` final (verify queda para `sdd-verify`).

---

## Resumen

| Fase | Tareas | Commits sugeridos |
|------|--------|-------------------|
| 1 Texto, modelo y FK | 1.1-1.4 | tras 1.4 |
| 2 Esquemas | 2.1-2.2 | tras 2.2 |
| 3 Servicios de secciones | 3.1-3.4 | tras 3.4 |
| 4 Integración en productos | 4.1-4.4 | tras 4.4 |
| 5 Routers y manejadores | 5.1-5.5 | tras 5.5 |
| 6 Verificación final | 6.1-6.4 | tras 6.4 |

Total: 6 fases, 23 tareas.

Paralelismo: 1.1 `||` 1.2; 2.1 `||` 2.2. Todo lo demás es secuencial porque modifica archivos compartidos (`productos/services.py`, `Backend/tests/conftest.py`, routers).

---

## Anexo A: Trazabilidad de escenarios

### section-management (SEC, 44 escenarios)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| SEC-01 | Los mappers se configuran con la nueva entidad | 1.3 |
| SEC-02 | La respuesta no incluye productos ni estado de baja | 2.1, 5.1 |
| SEC-03 | nombre vacío | 2.1, 5.1 |
| SEC-04 | nombre compuesto solo de espacios | 2.1, 5.1 |
| SEC-05 | nombre ausente | 2.1, 5.1 |
| SEC-06 | nombre se recorta antes de almacenarse | 2.1, 5.1 |
| SEC-07 | nombre en el límite de 100 caracteres | 2.1, 5.1 |
| SEC-08 | nombre demasiado largo | 2.1, 5.1 |
| SEC-09 | subtitulo en el límite de 200 caracteres | 2.1, 5.1 |
| SEC-10 | subtitulo demasiado largo | 2.1, 5.1 |
| SEC-11 | nombre duplicado en el alta | 3.2, 5.1 |
| SEC-12 | nombre duplicado sin distinguir mayúsculas | 3.2, 5.1 |
| SEC-13 | nombre duplicado con espacios sobrantes | 3.2, 5.1 |
| SEC-14 | Las tildes distinguen nombres | 3.2, 5.1 |
| SEC-15 | nombre duplicado en la modificación | 3.3, 5.1 |
| SEC-16 | La modificación conserva el propio nombre | 3.3, 5.1 |
| SEC-17 | La modificación puede cambiar solo mayúsculas del propio nombre | 3.3, 5.1 |
| SEC-18 | Reutilización del nombre tras el borrado | 3.4, 5.1 |
| SEC-19 | Crear sección con todos los campos | 3.2, 5.1 |
| SEC-20 | Crear sección sin subtitulo | 3.2, 5.1 |
| SEC-21 | Prioridad de 422 sobre 409 en el alta | 5.1 |
| SEC-22 | Obtener una sección existente | 3.1, 5.1 |
| SEC-23 | Obtener una sección inexistente | 3.1, 5.1 |
| SEC-24 | No existe el listado de secciones | 5.1 |
| SEC-25 | Modificar una sección | 3.3, 5.1 |
| SEC-26 | PUT como reemplazo completo | 3.3, 5.1 |
| SEC-27 | Actualizar una sección inexistente | 3.3, 5.1 |
| SEC-28 | Prioridad de 422 sobre 404 en la modificación | 5.1 |
| SEC-29 | Prioridad de 404 sobre 409 en la modificación | 3.3, 5.1 |
| SEC-30 | La modificación no altera los productos asignados | 3.3, 5.3 |
| SEC-31 | Borrar una sección | 3.4, 5.1 |
| SEC-32 | Borrar una sección inexistente | 3.4, 5.1 |
| SEC-33 | Borrado repetido | 3.4, 5.1 |
| SEC-34 | Los productos se conservan sin sección | 6.1, 6.2 |
| SEC-35 | Solo se desvinculan los productos de la sección borrada | 6.1, 6.2 |
| SEC-36 | Se desvinculan los cinco subtipos | 6.1, 6.2 |
| SEC-37 | Un combo vencido también se desvincula | 6.1, 6.2 |
| SEC-38 | Un producto dado de baja también se desvincula | 6.1, 6.2 |
| SEC-39 | subtitulo se recorta antes de almacenarse | 2.1, 5.1 |
| SEC-40 | subtitulo vacío se almacena como null | 2.1, 5.1 |
| SEC-41 | subtitulo compuesto solo de espacios se almacena como null | 2.1, 5.1 |
| SEC-42 | El límite de subtitulo se verifica tras el recorte | 2.1, 5.1 |
| SEC-43 | subtitulo demasiado largo tras el recorte | 2.1, 5.1 |
| SEC-44 | El PUT también recorta y normaliza subtitulo | 3.3, 5.1 |

### product-catalog (CAT-S, 28 escenarios)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| CAT-S-01 | Crear producto con sección | 4.2, 5.3 |
| CAT-S-02 | Crear producto sin sección | 2.2, 5.3 |
| CAT-S-03 | Crear producto con sección inexistente | 4.2, 5.2, 5.3 |
| CAT-S-04 | Todos los subtipos aceptan seccion_id en el alta | 4.2, 4.3, 4.4, 5.3, 5.4, 5.5 |
| CAT-S-05 | Todos los subtipos rechazan una sección inexistente en el alta | 4.3, 4.4, 5.3, 5.4, 5.5 |
| CAT-S-06 | Modificar la sección de un producto | 4.2, 5.3 |
| CAT-S-07 | PUT sin seccion_id desasigna la sección | 4.2, 5.3 |
| CAT-S-08 | PUT con sección inexistente | 4.2, 5.2, 5.3 |
| CAT-S-09 | Todos los subtipos aceptan y rechazan seccion_id en el PUT | 4.3, 4.4, 5.3, 5.4, 5.5 |
| CAT-S-10 | La consulta por id expone seccion_id | 5.3 |
| CAT-S-11 | Asignar sección a un producto dado de baja | 4.2, 5.3 |
| CAT-S-12 | La sección no afecta la unicidad del nombre | 4.2, 5.3 |
| CAT-S-13 | seccion_id de tipo inválido | 2.2, 5.3 |
| CAT-S-14 | Prioridad de 404 sobre 422 por sección inexistente | 4.2, 5.3 |
| CAT-S-15 | Prioridad de 422 de esquema sobre 422 de sección | 5.3 |
| CAT-S-16 | Prioridad de combo vencido (409) sobre sección inexistente (422) | 4.4, 5.5 |
| CAT-S-17 | Prioridad de sección inexistente (422) sobre componente inactivo (409) | 4.3, 5.4 |
| CAT-S-18 | Prioridad de sección inexistente (422) sobre nombre duplicado (409) | 4.2, 5.3 |
| CAT-S-19 | Prioridad de componente inactivo (409) sobre nombre duplicado (409) | 4.3, 5.4 |
| CAT-S-20 | Prioridad de referencias inexistentes (422) sobre componente inactivo (409) en un combo | 4.4, 5.5 |
| CAT-S-21 | El Postre acepta seccion_id además de los campos comunes | 5.3 |
| CAT-S-22 | Cambiar seccion_id en un combo vencido | 4.4, 5.5 |
| CAT-S-23 | Asignar sección a un combo vencido sin sección | 4.4, 5.5 |
| CAT-S-24 | Dar de baja un combo vencido conservando su seccion_id | 4.4, 5.5 |
| CAT-S-25 | Dar de baja un combo vencido omitiendo seccion_id | 4.4, 5.5 |
| CAT-S-26 | Dar de baja un combo vencido sin sección | 4.4, 5.5 |
| CAT-S-27 | Dar de baja un combo vencido vía DELETE no altera la sección | 4.4, 5.5 |
| CAT-S-28 | Un combo vigente puede cambiar de sección | 4.4, 5.5 |

El Anexo A es la numeración normativa; los nombres de prueba usan el id (`test_sec_NN_...`, `test_cat_s_NN_...`).

## Escenarios sin tarea asignada

Ninguno: los 72 escenarios (44 SEC + 28 CAT-S) están mapeados. La tarea 6.4 verifica que cada uno tenga su prueba.
