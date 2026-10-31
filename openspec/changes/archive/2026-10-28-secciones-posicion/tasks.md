# Tareas: Posición de las Secciones

Cambio: `secciones-posicion`. Entradas: `proposal.md`, `design.md`, `specs/section-management/spec.md` (delta: 29 escenarios POS-01..29; los SEC-xx modificados conservan su resultado esperado). Comando de pruebas: `cd Backend && python -m pytest`. Los escenarios se numeran en el Anexo A.

**Nota operativa (base local)**: `create_all` no agrega columnas a una tabla existente. Antes de iniciar la aplicación o de verificar manualmente, se debe borrar `Backend/app.db` (archivo local no versionado) para que se recree con la columna `seccion.posicion` y el índice `ux_seccion_posicion`. Las pruebas usan SQLite en memoria y no se ven afectadas. La tarea 6.2 repite el recordatorio.

## Orden de las fases y suite en verde

Las fases siguen la dependencia real del código, con una desviación respecto del orden "modelo → esquemas": la columna `posicion` es `NOT NULL`, así que en cuanto exista el modelo todo servicio que cree una `Seccion` debe poder informar `posicion`. Por eso:

- La Fase 1 actualiza primero los cuerpos y llamadas de las pruebas existentes. Es posible sin romper nada porque Pydantic ignora los campos extra: las pruebas siguen en verde antes de que exista el campo.
- La Fase 2 agrega `posicion` al esquema de entrada (ya todas las pruebas la envían).
- La Fase 3 agrega modelo, índice, asignación mínima en el servicio, respuesta y fixture en unidades atómicas, para que la suite no quede en rojo entre tareas. La fábrica `crear_seccion` y los cuatro `Seccion(...)` directos de `test_modelos.py` solo pueden actualizarse aquí, porque `Seccion(posicion=...)` falla mientras la columna no exista.

## Pronóstico de carga de revisión

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | 700 a 1.000 (aprox. 10 % código, 90 % pruebas) |
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
| 1 | Pruebas existentes con `posicion`, esquema de entrada, modelo, índice, respuesta y fixture | PR 1 | `cd Backend && python -m pytest tests/secciones tests/productos` | N/A: sin comportamiento HTTP nuevo de 409 | `models.py`, `schemas.py`, `services.py` (asignación), `Backend/tests/conftest.py` |
| 2 | Servicios: excepción, `_verificar_unicidad`, `_confirmar`, prioridad determinista | PR 2 | `cd Backend && python -m pytest tests/secciones/test_servicios.py tests/secciones/test_excepciones.py` | N/A: sin HTTP todavía | `exceptions.py`, `services.py` |
| 3 | Manejador 409, pruebas HTTP y verificación final | PR 3 | `cd Backend && python -m pytest` | `rm Backend/app.db`, iniciar la app y `POST/PUT/DELETE /secciones` | `router.py` |

## Convenciones

- **TDD estricto**: cada tarea sigue RED (pruebas que fallan por el motivo correcto) → GREEN (código mínimo) → REFACTOR opcional con la suite en verde. Las pruebas de **caracterización** (comportamiento que el cambio no debe romper o que ya se cumple) nacen en verde y se rotulan así; en ellas el RED es registrar la línea base verde antes de editar y el GREEN es mantenerla.
- Nombres de prueba: `test_pos_NN_<descripcion>` para los escenarios POS; las pruebas de apoyo sin escenario usan `test_posicion_<descripcion>`. Los SEC-xx modificados conservan su prefijo `test_sec_NN`.
- Niveles: **E** = esquema/unidad, **S** = servicio, **H** = HTTP con `TestClient`, **BD** = integración con SQLite. El Anexo A exige al menos una prueba H (o BD) por escenario cuando aplica.
- Las posiciones explícitas en las pruebas son menores a 1001; las autoasignadas (fixture `crear_seccion` y helper `_crear`) parten de 1001 para no colisionar con ellas.
- `[COMMIT]` = unidad confirmable con la suite en verde; commits convencionales, sin atribución de IA.
- Un solo escritor: varias tareas modifican `services.py`, `test_servicios.py`, `test_router.py` y `Backend/tests/conftest.py`.

---

## Fase 1: Actualización de las pruebas existentes (caracterización, verde)

- [x] **1.1 Cuerpos HTTP con `posicion`** — Archivos: `Backend/tests/secciones/test_router.py`, `Backend/tests/productos/test_seccion_producto_http.py`, y todo otro llamador de `POST/PUT /secciones` (localizar con `rg '"/secciones' Backend/tests`, p. ej. `Backend/tests/productos/menus_ejecutivos/test_router.py`). `||` con 1.2.
  - RED (caracterización): registrar la línea base verde de `cd Backend && python -m pytest tests/secciones tests/productos`.
  - GREEN: el helper `_crear` agrega una `posicion` única con un contador de módulo (`itertools.count(1001)`); los PUT de SEC-15, 16, 17, 25, 26, 27, 29 y 44 envían `posicion` explícita y distinta; SEC-30 (POST y PUT) envía `posicion`. Cuando una prueba crea varias secciones, cada una lleva una posición distinta. Sin cambios de aserciones. La suite sigue en verde (Pydantic ignora el campo extra).
  - Escenarios: soporte de los SEC-xx modificados (SEC-19..21, 25..30).

- [x] **1.2 Llamadas de servicio y helper de esquemas con `posicion`** — Archivos: `Backend/tests/secciones/test_servicios.py`, `Backend/tests/secciones/test_schemas.py`, `Backend/tests/productos/menus_ejecutivos/test_servicios.py`. `||` con 1.1.
  - RED (caracterización): línea base verde de `cd Backend && python -m pytest tests/secciones tests/productos`.
  - GREEN: todo `SeccionCrear(...)` y `SeccionActualizar(...)`, incluido el parametrizado de 404, recibe `posicion` explícita y distinta cuando la prueba crea más de una sección; el helper `crear` de `test_schemas.py` usa `posicion=1` por defecto. Sin cambios de aserciones.
  - Escenarios: soporte de SEC-19..21 y 25..30 a nivel servicio.
  - `[COMMIT]` (Fase 1 completa; suite en verde).

---

## Fase 2: Esquema de entrada

- [x] **2.1 `posicion` en `SeccionCrear` / `SeccionActualizar`** — Archivos: `Backend/src/secciones/schemas.py`, `Backend/tests/secciones/test_schemas.py`. Depende de 1.2.
  - RED (E): `posicion` ausente → `ValidationError` (POS-02, POS-03); `0` (POS-04, POS-06) y `-1` (POS-05) → error; `"abc"` → error (POS-07); `3.5` y `1.5` → error (POS-08); `1` válido y conservado (POS-09); modo laxo: `"3"` → `3` y `3.0` → `3`, ambos de tipo `int` (POS-29); `SeccionActualizar` equivale a `SeccionCrear`.
  - GREEN: `posicion: int = Field(ge=1)` en `SeccionCrear` (sin `strict`, decisión 2 del diseño); `SeccionActualizar = SeccionCrear` ya lo hereda. Las pruebas de otras capas siguen en verde porque la Fase 1 ya envía `posicion`.
  - Escenarios (E): POS-02..09, POS-29.

- [x] **2.2 Validación 422 de `posicion` por HTTP** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de 2.1.
  - RED (H): POST sin `posicion` → 422 y GET posterior sin filas nuevas (POS-02); PUT sin `posicion` → 422 (POS-03); POST con `0` (POS-04), `-1` (POS-05), `"abc"` (POS-07) y `1.5` (POS-08) → 422 sin crear sección; PUT con `0` → 422 (POS-06); PUT con `nombre = "Aperitivos"`, `subtitulo = "Para compartir"` y `posicion = -3` → 422 y un GET posterior devuelve `Entradas`, `Para comenzar` y `posicion = 1` (POS-10). Fallan hoy porque el campo se ignora y devuelve 201/200.
  - GREEN: sin código adicional si 2.1 está completa; si una prueba falla, corregir el esquema.
  - Escenarios (H): POS-02..08, POS-10.
  - `[COMMIT]` (Fase 2 completa).

---

## Fase 3: Modelo, índice, respuesta y fixture

- [x] **3.1 Columna, índice único, asignación mínima en el servicio y fixture** — Archivos: `Backend/src/secciones/models.py`, `Backend/src/secciones/services.py`, `Backend/tests/conftest.py`, `Backend/tests/secciones/test_modelos.py`, `Backend/tests/secciones/test_fabrica.py`. Depende de 2.2. Unidad atómica: columna `NOT NULL`, asignación en el servicio y fábrica deben entrar juntas para no dejar la suite en rojo.
  - RED (BD/E): conjunto de columnas de `seccion` incluye `posicion` (entero, no anulable); `test_pos_11_indice_unico_rechaza_posicion_repetida` (dos filas con la misma `posicion` y nombres distintos → `IntegrityError` cuyo mensaje menciona `seccion.posicion`); existe el índice único `ux_seccion_posicion` sobre `posicion`; los cuatro `Seccion(...)` directos de `test_modelos.py` pasan `posicion` distinta; `test_fabrica_crear_seccion_autoasigna_posiciones_unicas_desde_1001` (primera llamada 1001, segunda 1002, y el contador se reinicia en la prueba siguiente); `test_fabrica_crear_seccion_respeta_posicion_explicita` (no consume el contador); crear una sección vía servicio persiste la `posicion` informada.
  - GREEN: `posicion = mapped_column(Integer, nullable=False)` e `Index("ux_seccion_posicion", "posicion", unique=True)` en `__table_args__` (sin `CHECK`); `crear_seccion` pasa `posicion=datos.posicion` y `actualizar_seccion` asigna `seccion.posicion = datos.posicion`; fixture `crear_seccion(nombre="Entradas", subtitulo=None, posicion=None)` con `itertools.count(1001)` creado dentro del fixture (alcance de función). La suite completa vuelve a verde, incluidas las pruebas de productos que usan el fixture.
  - Escenarios (BD): POS-11 (índice); soporte de POS-16.

- [x] **3.2 `SeccionRespuesta.posicion` y comportamiento observable de lectura/escritura** — Archivos: `Backend/src/secciones/schemas.py`, `Backend/tests/secciones/test_schemas.py`, `Backend/tests/secciones/test_router.py`. Depende de 3.1.
  - RED (E/H): `SeccionRespuesta` expone `id`, `nombre`, `subtitulo` y `posicion`, sin productos ni `dado_de_baja`; GET de una sección con `posicion = 4` devuelve 4 junto con los demás campos (POS-01); POST con `posicion = 1` devuelve 201 y `posicion = 1` (POS-09); `posicion = "3"` y `3.0` devuelven 201 y `posicion = 3` (POS-29); POST con `posicion = 2` devuelve `posicion = 2` (POS-22); POST con `posicion = 10` sin otras secciones devuelve 201 y 10 (POS-19); PUT conservando la propia `posicion = 3` con nuevo `subtitulo` devuelve 200 y 3 (POS-14); PUT a la posición libre 5 devuelve 200 y 5 (POS-15); PUT a la posición libre 7 devuelve 7 (POS-25). Las respuestas exactas de SEC-02, SEC-22 y SEC-25 pasan a incluir `posicion` (RED por diferencia de claves).
  - GREEN: `posicion: int` en `SeccionRespuesta`.
  - Escenarios (E/H): POS-01, 09, 14, 15, 19, 22, 25, 29; SEC-02, SEC-22, SEC-25 (respuesta exacta).
  - `[COMMIT]` (Fase 3 completa; PR 1 cerrable aquí).

---

## Fase 4: Servicios

- [x] **4.1 Excepción `PosicionSeccionDuplicada`** — Archivos: `Backend/src/secciones/exceptions.py`, `Backend/tests/secciones/test_excepciones.py`. Depende de 3.2.
  - RED (E): `PosicionSeccionDuplicada` hereda de `ErrorSeccion`, es disjunta de `productos.ErrorDominio` y de `NombreSeccionDuplicado`, `MENSAJE == "Ya existe una sección en esa posición"` y `str(excepcion)` lo devuelve; el módulo no importa FastAPI ni `src.productos`.
  - GREEN: agregar la clase.
  - Escenarios: soporte de POS-11.

- [x] **4.2 `_verificar_unicidad` en el alta** — Archivos: `Backend/src/secciones/services.py`, `Backend/tests/secciones/test_servicios.py`. Depende de 4.1.
  - RED (S): `_verificar_unicidad(sesion, nombre_normalizado, posicion)` con `posicion` repetida lanza `PosicionSeccionDuplicada` (POS-11 alta); con `excluir_id` ignora la propia fila; con nombre y posición libres no lanza; `crear_seccion` con posición repetida → `PosicionSeccionDuplicada` sin fila nueva, y `sesion.in_transaction()` es falso tras el error (rollback); "Postres" en `posicion = 2` con "Entradas", "Postres"-vecino y "Bebidas" en 1, 2 y 3 → 409 y las tres conservan 1, 2 y 3 (POS-16); doble colisión (`nombre` y `posicion`) → `NombreSeccionDuplicado`, no `PosicionSeccionDuplicada` (POS-23); reutilizar una posición tras borrar la sección → crea (POS-17, nivel servicio); hueco `posicion = 10` → crea (POS-19, nivel servicio).
  - GREEN: `_verificar_unicidad` con el bucle ordenado `nombre → posicion` del diseño (rollback antes de lanzar); `crear_seccion`: verificar → `add` → `_confirmar`.
  - Escenarios (S): POS-11, POS-16, POS-17, POS-19, POS-23.

- [x] **4.3 `actualizar_seccion` con verificación previa** — Archivos: `Backend/src/secciones/services.py`, `Backend/tests/secciones/test_servicios.py`. Depende de 4.2.
  - RED (S): posición repetida en el PUT → `PosicionSeccionDuplicada` y ambas secciones conservan `nombre` y `posicion` (POS-13); conservar la propia `posicion` actualiza el `subtitulo` sin conflicto (POS-14); mover a una posición libre (POS-15); doble colisión (`nombre = "entradas"` y `posicion = 1` sobre "Postres" en 2) → `NombreSeccionDuplicado` y "Postres" conserva nombre y posición (POS-26); id inexistente con posición ocupada → `SeccionNoEncontrada` (POS-27, guarda del orden: nace verde); PUT directo de A a la posición de B → `PosicionSeccionDuplicada` sin cambios (POS-21); intercambio en tres PUT (A a 99, B a 1, A a 2) termina con A en 2 y B en 1 (POS-20); sin transacción abierta tras cada error.
  - GREEN: `actualizar_seccion`: `obtener` → `_verificar_unicidad(..., excluir_id=seccion_id)` → asignar `nombre`, `nombre_normalizado`, `subtitulo`, `posicion` → `_confirmar`. La verificación precede a la asignación (la sesión usa `autoflush=False`).
  - Escenarios (S): POS-13, 14, 15, 20, 21, 26, 27.

- [x] **4.4 `_confirmar`: traducción del `IntegrityError` y prioridad determinista** — Archivos: `Backend/src/secciones/services.py`, `Backend/tests/secciones/test_servicios.py`. Depende de 4.3.
  - RED (S, con `monkeypatch` anulando `_verificar_unicidad`): una colisión solo de `posicion` llega al índice y se traduce a `PosicionSeccionDuplicada` en alta (POS-11) y en PUT; una doble colisión de `nombre` y `posicion` se traduce siempre a `NombreSeccionDuplicado` (POS-23, POS-26), porque `nombre_normalizado` se inspecciona antes que `seccion.posicion` aunque SQLite informe una sola restricción; un `IntegrityError` ajeno se propaga sin traducir; todo error deja `sesion.in_transaction()` en falso.
  - GREEN: en `_confirmar`, tras `rollback`, inspeccionar `str(error.orig)` en orden: `nombre_normalizado` → `NombreSeccionDuplicado`; `seccion.posicion` → `PosicionSeccionDuplicada`; otro → propagar.
  - Escenarios (S): POS-11, POS-23, POS-26 (ruta de carrera).

- [x] **4.5 Liberación de posiciones tras el borrado (caracterización)** — Archivos: `Backend/tests/secciones/test_servicios.py`. Depende de 4.4.
  - RED (caracterización, nace verde): borrar "Postres" (posición 2) deja "Entradas" en 1 y "Bebidas" en 3 sin renumerar (POS-18); tras borrar "Entradas" (posición 1), crear "Postres" en 1 → crea (POS-17).
  - GREEN: sin código esperado (`eliminar_seccion` no cambia). Si alguna prueba falla, corregir el servicio.
  - Escenarios (S): POS-17, POS-18.
  - `[COMMIT]` (Fase 4 completa; PR 2 cerrable aquí).

---

## Fase 5: Router y manejador

- [x] **5.1 Manejador `manejar_posicion_duplicada`** — Archivos: `Backend/src/secciones/router.py`, `Backend/tests/secciones/test_manejadores.py`. Depende de 4.1.
  - RED (H/E): `PosicionSeccionDuplicada` → 409 con cuerpo `{"detail": "Ya existe una sección en esa posición"}` (POS-12); la forma del cuerpo es igual a la del 409 de `NombreSeccionDuplicado` (objeto con la clave `detail`); la excepción figura en `MANEJADORES_EXCEPCIONES`; `main.py` ya recorre el diccionario, sin cambios.
  - GREEN: función `manejar_posicion_duplicada` y su entrada en `MANEJADORES_EXCEPCIONES`.
  - Escenarios: POS-12 (manejador).

- [x] **5.2 HTTP del alta: 409, cuerpo y prioridades** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de 5.1, 4.2.
  - RED (H): POST de "Postres" en `posicion = 1` con "Entradas" en 1 → 409 y GET posterior sin fila nueva (POS-11); el cuerpo es un objeto con la clave `detail` (POS-12); "Sopas" en `posicion = 2` con tres secciones en 1, 2 y 3 → 409 y las tres conservan sus posiciones (POS-16); `nombre = "Entradas"` y `posicion = 1` repetidos → un único 409 cuyo `detail` es el mensaje de nombre duplicado (POS-23); `posicion = 1` repetida con `subtitulo` de 201 caracteres → 422 (POS-24, guarda de prioridad: nace verde).
  - GREEN: sin código adicional si 5.1 y 4.2 están completas.
  - Escenarios (H): POS-11, 12, 16, 23, 24.

- [x] **5.3 HTTP de la modificación: 409, 404 y prioridades** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de 5.2, 4.3.
  - RED (H): PUT de "Postres" a `posicion = 1` con "Entradas" en 1 → 409 y un GET de ambas confirma nombres y posiciones intactos (POS-13); PUT directo de A a la posición de B → 409 sin cambios (POS-21); PUT de "Postres" con `nombre = "entradas"` y `posicion = 1` → un único 409 de nombre y "Postres" conserva `nombre = "Postres"` y `posicion = 2` (POS-26); PUT a `/secciones/999` con `posicion = 1` ocupada → 404 (POS-27); PUT de B a `posicion = 1` con `subtitulo` de 201 caracteres → 422 y B conserva `posicion = 2` (POS-28, guarda de prioridad: nace verde).
  - GREEN: sin código adicional si 5.1 y 4.3 están completas.
  - Escenarios (H): POS-13, 21, 26, 27, 28.
  - `[COMMIT]` (Fase 5 completa).

---

## Fase 6: Verificación final y trazabilidad

- [x] **6.1 Liberación, huecos e intercambio por HTTP (caracterización)** — Archivos: `Backend/tests/secciones/test_router.py`. Depende de Fase 5.
  - RED (caracterización, nace verde): `DELETE /secciones/{id}` seguido de `POST` con la misma `posicion = 1` → 201 y `posicion = 1` (POS-17); borrar "Postres" deja `posicion = 1` y `3` en "Entradas" y "Bebidas" al consultarlas (POS-18); alta con `posicion = 10` sin otras secciones → 201 y 10 (POS-19); intercambio de A y B en tres PUT: los tres devuelven 200 y al final A tiene 2 y B tiene 1 (POS-20).
  - GREEN: sin código esperado.
  - Escenarios (H): POS-17, 18, 19, 20.

- [x] **6.2 Suite completa y base local** — Archivos: ninguno. Depende de 6.1.
  - Verificar `cd Backend && python -m pytest` en verde y `configure_mappers()` sin errores; `rg "from src.productos" Backend/src/secciones` sin resultados. **Borrar `Backend/app.db` local y recrearla** al iniciar la aplicación (la base existente no tiene la columna `posicion`); comprobar manualmente `POST /secciones` con `posicion`, un 409 por posición repetida y `DELETE /secciones/{id}`.
  - Nota de ejecución (apply): la suite y `configure_mappers()` pasan y `rg "from src.productos" Backend/src/secciones` no devuelve resultados. El borrado y la recreación de `Backend/app.db` y la comprobación manual con la aplicación en marcha quedan como acción manual del usuario: `app.db` es un archivo local no versionado y no se tocó ni se creó otro.
  - Hecho cuando: suite en verde, grafo de importaciones acíclico y base local recreada.

- [x] **6.3 Trazabilidad de escenarios** — Archivos: ninguno (solo se agregan pruebas en archivos existentes). Depende de 6.2.
  - Revisar el Anexo A: para cada uno de los 29 escenarios POS debe existir una prueba cuyo nombre contenga `test_pos_NN`, con nivel H o BD donde aplica; confirmar que los SEC-xx modificados (SEC-01, 02, 19..21, 25..30) siguen pasando con su resultado esperado. Listar los huecos y cerrarlos con RED → GREEN o registrarlos como riesgo.
  - Hecho cuando: el listado sin cobertura está vacío y `python -m pytest` pasa.
  - `[COMMIT]` final (verify queda para `sdd-verify`).

---

## Resumen

| Fase | Tareas | Commits sugeridos |
|------|--------|-------------------|
| 1 Pruebas existentes con `posicion` | 1.1-1.2 | tras 1.2 |
| 2 Esquema de entrada | 2.1-2.2 | tras 2.2 |
| 3 Modelo, índice, respuesta y fixture | 3.1-3.2 | tras 3.2 |
| 4 Servicios | 4.1-4.5 | tras 4.5 |
| 5 Router y manejador | 5.1-5.3 | tras 5.3 |
| 6 Verificación final | 6.1-6.3 | tras 6.3 |

Total: 6 fases, 17 tareas.

Paralelismo: 1.1 `||` 1.2 (archivos de prueba distintos). Todo lo demás es secuencial porque modifica archivos compartidos (`services.py`, `schemas.py`, `test_servicios.py`, `test_router.py`, `Backend/tests/conftest.py`). 5.1 solo depende de 4.1 y podría adelantarse, pero se mantiene en orden para un único escritor.

---

## Anexo A: Trazabilidad de escenarios

### section-management, delta de posición (POS, 29 escenarios)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| POS-01 | La respuesta de consulta incluye posicion | 3.2 |
| POS-02 | posicion ausente en el alta | 2.1, 2.2 |
| POS-03 | posicion ausente en la modificación | 2.1, 2.2 |
| POS-04 | posicion igual a cero en el alta | 2.1, 2.2 |
| POS-05 | posicion negativa en el alta | 2.1, 2.2 |
| POS-06 | posicion igual a cero en la modificación | 2.1, 2.2 |
| POS-07 | posicion con texto no numérico | 2.1, 2.2 |
| POS-08 | posicion decimal | 2.1, 2.2 |
| POS-09 | posicion en el límite inferior | 2.1, 3.2 |
| POS-10 | Una modificación rechazada por validación no cambia la sección | 2.2 |
| POS-11 | posicion duplicada en el alta | 3.1, 4.2, 4.4, 5.2 |
| POS-12 | El 409 por posicion usa el cuerpo estándar | 5.1, 5.2 |
| POS-13 | posicion duplicada en la modificación | 4.3, 5.3 |
| POS-14 | La modificación conserva la propia posicion | 3.2, 4.3 |
| POS-15 | Mover una sección a una posición libre | 3.2, 4.3 |
| POS-16 | Una colisión no desplaza a otras secciones | 4.2, 5.2 |
| POS-17 | Reutilización de la posicion tras el borrado | 4.2, 4.5, 6.1 |
| POS-18 | El borrado no renumera las demás secciones | 4.5, 6.1 |
| POS-19 | Se permiten huecos en las posiciones | 3.2, 4.2, 6.1 |
| POS-20 | Intercambio de dos secciones en tres PUT | 4.3, 6.1 |
| POS-21 | El intercambio directo es rechazado | 4.3, 5.3 |
| POS-22 | El alta devuelve la posicion informada | 3.2 |
| POS-23 | Doble colisión en el alta devuelve el 409 de nombre | 4.2, 4.4, 5.2 |
| POS-24 | Prioridad de 422 sobre 409 por posicion en el alta | 5.2 |
| POS-25 | La modificación devuelve la nueva posicion | 3.2 |
| POS-26 | Doble colisión en la modificación devuelve el 409 de nombre | 4.3, 4.4, 5.3 |
| POS-27 | Prioridad de 404 sobre 409 por posicion en la modificación | 4.3, 5.3 |
| POS-28 | Prioridad de 422 sobre 409 por posicion en la modificación | 5.3 |
| POS-29 | posicion como texto numérico o decimal sin parte fraccionaria | 2.1, 3.2 |

### Escenarios SEC existentes con cuerpos o respuestas afectados (resultado esperado sin cambios)

| ID | Efecto | Tarea(s) |
|----|--------|----------|
| SEC-01 | Mappers con la nueva columna | 3.1 |
| SEC-02 | La respuesta exacta incluye `posicion` | 3.2 |
| SEC-19, SEC-20, SEC-21 | Cuerpos del alta con `posicion` | 1.1, 1.2, 6.3 |
| SEC-22 | La respuesta exacta incluye `posicion` | 3.2 |
| SEC-25, SEC-26, SEC-27, SEC-28, SEC-29 | Cuerpos del PUT con `posicion` | 1.1, 1.2, 6.3 |
| SEC-25 | La respuesta exacta incluye `posicion` | 3.2 |
| SEC-30 | POST y PUT de la prueba HTTP con `posicion` | 1.1 |

El Anexo A es la numeración normativa; los nombres de prueba usan el id (`test_pos_NN_...`).

## Escenarios sin tarea asignada

Ninguno: los 29 escenarios POS están mapeados. La tarea 6.3 verifica que cada uno tenga su prueba.
