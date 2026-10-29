# Tareas: Productos Menú del Día

Cambio: `productos-menu`. Entradas: `proposal.md`, `design.md`, `specs/daily-menu-management/spec.md` (PMD, 40 escenarios). Comando de pruebas: `cd Backend && python -m pytest`. Los escenarios se numeran en el Anexo A.

Valores por defecto aprobados por el usuario: las respuestas de producto no cambian; DELETE ignora el estado del producto; un `producto_id` enviado en el PUT se ignora; un PUT sobre un producto dado de baja devuelve 409 aun conservando la misma fecha; las cinco fábricas de producto pasan a `Backend/tests/conftest.py`.

**Nota operativa (base local)**: `create_all` crea `producto_menu` en una base nueva, pero `Backend/app.db` debe recrearse por el cambio previo de `posicion`. Las pruebas usan SQLite en memoria. La tarea 6.3 repite el recordatorio.

## Pronóstico de carga de revisión

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | 1.100 a 1.600 (aprox. 30 % código, 70 % pruebas) |
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
| 1 | Fábricas compartidas, modelo, FK, índice, registro y esquemas | PR 1 | `cd Backend && python -m pytest tests/productos_menu tests/productos` | N/A: sin HTTP todavía | `Backend/src/productos_menu/{models,constants,schemas}.py`, relación en `Backend/src/productos/models.py`, `registro.py`, fábricas de `Backend/tests/conftest.py` |
| 2 | Excepciones y servicios (prioridad, rollback, respaldo del índice UNIQUE) | PR 2 | `cd Backend && python -m pytest tests/productos_menu` | N/A: sin HTTP todavía | `Backend/src/productos_menu/{exceptions,services}.py` y sus pruebas |
| 3 | Router, manejadores, `main.py` y verificación final | PR 3 | `cd Backend && python -m pytest` | `rm Backend/app.db`, iniciar la app y `POST/PUT/DELETE /productos-menu` | `Backend/src/productos_menu/router.py` y registro en `Backend/src/main.py` |

## Convenciones

- **TDD estricto**: cada tarea sigue RED (pruebas que fallan por el motivo correcto) → GREEN (código mínimo) → REFACTOR opcional con la suite en verde. Las pruebas de **caracterización** (comportamiento existente que el cambio no debe romper) nacen en verde y se rotulan **[CARACTERIZACIÓN: nace en verde]**; su paso RED se reemplaza por una comprobación de que la prueba pasa antes de tocar código.
- Nombres de prueba: `test_pmd_NN_<descripcion>`; a nivel esquema, servicio o BD se usa el mismo prefijo con el id del escenario.
- Niveles: **E** = esquema/unidad, **S** = servicio, **H** = HTTP con `TestClient`, **BD** = integración con SQLite. El Anexo A exige al menos una prueba H (o BD) por escenario cuando aplica.
- `[COMMIT]` = unidad confirmable con la suite en verde; commits convencionales, sin atribución de IA.
- Un solo escritor: varias tareas modifican `Backend/tests/conftest.py` y `Backend/src/productos_menu/services.py`.
- La fábrica `crear_producto_menu` se agrega en la tarea 2.3, después de existir el modelo: importar `ProductoMenu` en `Backend/tests/conftest.py` antes rompería la recolección de toda la suite.

---

## Fase 1: Infraestructura de pruebas (fábricas de producto compartidas)

- [ ] **1.1 Mover las cinco fábricas de producto a `Backend/tests/conftest.py`** — Archivos: `Backend/tests/conftest.py`, `Backend/tests/productos/conftest.py`, `Backend/tests/test_fabricas_producto.py`.
  - RED: `test_fabricas_producto_disponibles_fuera_de_tests_productos` solicita `crear_plato`, `crear_bebida`, `crear_postre`, `crear_menu` y `crear_combo` desde `Backend/tests/` (fuera de `tests/productos`) y persiste un ejemplar de cada una con `persistir`; falla con `fixture 'crear_plato' not found`.
  - GREEN: mover las cinco fixtures sin cambiar su cuerpo a `Backend/tests/conftest.py` (con los imports de `Decimal`, `date` y los modelos de subtipo) y eliminar `Backend/tests/productos/conftest.py` (queda vacío).
  - Escenarios: soporte de PMD-08, PMD-37..40.

- [ ] **1.2 Suite existente intacta tras el movimiento** — **[CARACTERIZACIÓN: nace en verde]** — Archivos: ninguno. Depende de 1.1.
  - RED (sustituido): `cd Backend && python -m pytest` debe pasar completa tal como está; `rg "def crear_(plato|bebida|postre|menu|combo)" Backend/tests` devuelve solo `Backend/tests/conftest.py`.
  - GREEN: sin código; si algo falla, corregir imports de la fábrica movida, sin tocar aserciones.
  - `[COMMIT]` (Fase 1 completa).

---

## Fase 2: Modelo, clave foránea, índice y registro

- [ ] **2.1 Constantes y paquete de pruebas** — Archivos: `Backend/src/productos_menu/__init__.py`, `Backend/src/productos_menu/constants.py`, `Backend/tests/productos_menu/__init__.py`, `Backend/tests/productos_menu/test_constantes.py`.
  - RED: `test_constantes_prefijo` (`PREFIJO == "/productos-menu"`).
  - GREEN: crear paquetes y `constants.py`.
  - Escenarios: soporte del router.

- [ ] **2.2 Modelo `ProductoMenu`, FK, índice UNIQUE y relación bidireccional** — Archivos: `Backend/src/productos_menu/models.py`, `Backend/src/productos/models.py`, `Backend/src/productos/registro.py`, `Backend/tests/productos_menu/test_modelos.py`, `Backend/tests/productos/test_registro.py`. Depende de 2.1, 1.1.
  - RED:
    - `test_pmd_01_mappers_se_configuran_con_la_nueva_entidad` (`configure_mappers()` tras importar solo `src.productos.registro`, sin error).
    - `test_pmd_02_relacion_bidireccional` (asignar `ProductoMenu.producto` con un Plato y leer `Producto.menus_del_dia`, y a la inversa).
    - Tabla `producto_menu` con columnas `id`, `producto_id`, `fecha`; `producto_id` y `fecha` NOT NULL (`IntegrityError` al omitirlas); FK `producto_id` → `producto.id` sin cláusula `ON DELETE`; índice simple sobre `producto_id`.
    - `test_pmd_15_indice_unico_rechaza_fecha_repetida` (BD): dos filas con la misma `fecha` lanzan `IntegrityError` con `producto_menu.fecha`.
    - `test_pmd_40_un_producto_con_varias_fechas` (BD): dos filas del mismo producto con fechas distintas conviven y `menus_del_dia` las contiene.
    - `registro.py` expone `ProductoMenu`; ningún módulo de `src/productos_menu/models.py` importa `src.productos`.
    - **[CARACTERIZACIÓN: nace en verde]** `RESTRICT_POR_TIPO` conserva su contenido anterior.
  - GREEN: `ProductoMenu(ModeloBase)` con `producto_id = mapped_column(ForeignKey("producto.id"), nullable=False, index=True)`, `fecha = mapped_column(Date, nullable=False)`, `Index("ux_producto_menu_fecha", "fecha", unique=True)` y `producto = relationship("Producto", back_populates="menus_del_dia")`; en `Producto`, `menus_del_dia = relationship("ProductoMenu", back_populates="producto")` por cadena y sin cascada `delete`; `registro.py` agrega la importación y `__all__`.
  - Escenarios: PMD-01, PMD-02, PMD-40 (BD); soporte de PMD-15.
  - Hecho cuando: suite completa en verde.

- [ ] **2.3 Fábrica `crear_producto_menu`** — Archivos: `Backend/tests/conftest.py`, `Backend/tests/productos_menu/test_fabrica.py`. Depende de 2.2.
  - RED: `test_fabrica_crear_producto_menu_persiste_con_fecha_explicita`; sin fecha, la primera llamada devuelve `date(2100, 1, 1)` y las siguientes días consecutivos (contador por prueba); dos llamadas con el mismo producto y sin fecha no violan el índice UNIQUE. Falla con fixture inexistente.
  - GREEN: fixture `crear_producto_menu(producto, fecha=None)` con `itertools.count()` por prueba e importación de `ProductoMenu`.
  - `[COMMIT]` (Fase 2 completa).

---

## Fase 3: Esquemas

- [ ] **3.1 Esquemas de menú del día** — Archivos: `Backend/src/productos_menu/schemas.py`, `Backend/tests/productos_menu/test_schemas.py`. Depende de 2.1.
  - RED (E):
    - `ProductoMenuCrear`: `producto_id` ausente (PMD-09), `"abc"` (PMD-10), `fecha` ausente (PMD-11), `"no-es-una-fecha"` y `"2026-02-30"` (PMD-12) → error; fecha pasada, de hoy y futura válidas (PMD-05..07); `"2026-10-28"` se parsea a `date`.
    - `ProductoMenuActualizar`: `fecha` ausente o inválida → error (PMD-27); `{fecha, producto_id}` valida y el modelo resultante solo contiene `fecha` (PMD-26).
    - `ProductoMenuRespuesta`: `from_attributes=True` y exactamente `id`, `producto_id`, `fecha` (PMD-03, parcial).
  - GREEN: los tres modelos Pydantic del diseño, con `date` laxo y `producto_id: int` laxo.
  - Escenarios (E): PMD-03, PMD-05..07, PMD-09..12, PMD-26, PMD-27.

- [ ] **3.2 Los esquemas de producto no exponen `menus_del_dia`** — **[CARACTERIZACIÓN: nace en verde]** — Archivos: `Backend/tests/productos/test_schemas.py`. Depende de 2.2.
  - RED (sustituido): parametrizada por los cinco subtipos, `menus_del_dia` no está en `model_fields` de ningún `*Respuesta` de producto; pasa antes de cualquier cambio de código.
  - GREEN: sin código; si falla, quitar el campo expuesto.
  - Escenarios (E): PMD-39.
  - `[COMMIT]` (Fase 3 completa; PR 1 cerrable aquí).

---

## Fase 4: Excepciones y servicios

- [ ] **4.1 Excepciones** — Archivos: `Backend/src/productos_menu/exceptions.py`, `Backend/tests/productos_menu/test_excepciones.py`. Depende de 2.1.
  - RED: `ErrorProductoMenu(Exception)` es base de `ProductoInexistente(producto_id)` (guarda `producto_id`), `ProductoDadoDeBaja`, `FechaMenuOcupada` y `ProductoMenuNoEncontrado`; la jerarquía es disjunta de `productos.ErrorDominio` y `secciones.ErrorSeccion`; cada una tiene mensaje; el módulo no importa FastAPI.
  - GREEN: crear las clases.
  - Escenarios: soporte de PMD-13, 14, 15, 24.

- [ ] **4.2 `obtener_producto_menu` y rollback en salida con error** — Archivos: `Backend/src/productos_menu/services.py`, `Backend/tests/productos_menu/test_servicios.py`. Depende de 4.1, 2.3.
  - RED (S): existente devuelve la fila; inexistente lanza `ProductoMenuNoEncontrado` y `sesion.in_transaction()` es falso tras el error (decisión 10).
  - GREEN: `obtener_producto_menu(sesion, id)` con rollback antes de lanzar.
  - Escenarios (S): soporte de PMD-24, 29, 33.

- [ ] **4.3 `crear_producto_menu`, verificaciones y `_confirmar`** — Archivos: `Backend/src/productos_menu/services.py`, `Backend/tests/productos_menu/test_servicios.py`. Depende de 4.2.
  - RED (S):
    - Alta válida persiste y devuelve `id` (PMD-04); fecha pasada, de hoy y futura (PMD-05..07); los cinco subtipos con fechas distintas (PMD-08); mismo producto en dos fechas (PMD-40).
    - `producto_id` inexistente → `ProductoInexistente` (PMD-13); producto dado de baja → `ProductoDadoDeBaja` (PMD-14); fecha ocupada → `FechaMenuOcupada` sin fila nueva y el existente intacto (PMD-15).
    - Prioridad: inexistente + fecha ocupada → `ProductoInexistente` (PMD-17); baja + fecha ocupada → `ProductoDadoDeBaja` (PMD-18).
    - Cada error deja `sesion.in_transaction()` en falso y el conjunto `select(id, producto_id, fecha)` idéntico (PMD-19).
    - Respaldo: con `_verificar_fecha_libre` anulado por `monkeypatch` y la fecha ya ocupada, `_confirmar` traduce el `IntegrityError` a `FechaMenuOcupada` (PMD-20); un `IntegrityError` ajeno a `producto_menu.fecha` (mensaje sintético) se propaga sin traducir.
  - GREEN: `crear_producto_menu` (`sesion.get(Producto, id)` → `_verificar_producto_activo` → `_verificar_fecha_libre` → `add` → `_confirmar`); `_confirmar` traduce solo el `IntegrityError` cuyo `orig` contiene `producto_menu.fecha` y hace rollback en todo error.
  - Escenarios (S): PMD-04..08, PMD-13..15, PMD-17..20, PMD-40.

- [ ] **4.4 `actualizar_fecha_producto_menu`** — Archivos: `Backend/src/productos_menu/services.py`, `Backend/tests/productos_menu/test_servicios.py`. Depende de 4.3.
  - RED (S):
    - Mover a fecha libre: misma `id` y `producto_id`, `F1` queda libre (PMD-21); conservar la fecha propia (PMD-22).
    - Fecha de otro registro → `FechaMenuOcupada` y ambos intactos (PMD-23).
    - `id` inexistente → `ProductoMenuNoEncontrado` (PMD-24); 404 antes que fecha ocupada (PMD-29).
    - Producto dado de baja con fecha libre → `ProductoDadoDeBaja` sin cambios (PMD-25); también con la misma fecha propia (default aprobado: 409 aun conservando la fecha).
    - Baja + fecha ocupada por otro → `ProductoDadoDeBaja` (PMD-30).
    - `ProductoMenuActualizar` con `producto_id` extra no cambia el producto asociado (PMD-26, nivel servicio).
    - Cada error deja `sesion.in_transaction()` en falso y el conjunto persistido idéntico (PMD-31).
    - Respaldo: `_verificar_fecha_libre` anulado por `monkeypatch` → `IntegrityError` traducido a `FechaMenuOcupada`.
  - GREEN: `obtener` → `_verificar_producto_activo(registro.producto)` → `_verificar_fecha_libre(fecha, excluir_id=id)` → asignar `fecha` solo después de verificar (`autoflush=False`) → `_confirmar`.
  - Escenarios (S): PMD-21..26, PMD-29..31.

- [ ] **4.5 `eliminar_producto_menu`** — Archivos: `Backend/src/productos_menu/services.py`, `Backend/tests/productos_menu/test_servicios.py`. Depende de 4.4.
  - RED (S): borra la fila (PMD-32); `id` inexistente (PMD-33) y repetido (PMD-34) → `ProductoMenuNoEncontrado`; con producto dado de baja el borrado se completa (PMD-35); tras borrar, `crear_producto_menu` con la fecha liberada funciona (PMD-36); el producto sigue existiendo.
  - GREEN: `obtener` → `sesion.delete` → `_confirmar`, sin consultar el estado del producto.
  - Escenarios (S): PMD-32..36.
  - `[COMMIT]` (Fase 4 completa; PR 2 cerrable aquí).

---

## Fase 5: Router, manejadores y `main.py`

- [ ] **5.1 Manejadores de excepciones** — Archivos: `Backend/src/productos_menu/router.py`, `Backend/tests/productos_menu/test_manejadores.py`. Depende de 4.1.
  - RED (H, aplicación mínima de prueba que lanza cada excepción): `ProductoInexistente` → 422 con `{"detail": [{"loc": ["body","producto_id"], "msg": ..., "type": "producto_inexistente", "ids": [id]}]}`; `ProductoDadoDeBaja` → 409 `{"detail": "El producto está dado de baja"}`; `FechaMenuOcupada` → 409 `{"detail": "Ya existe un menú del día en esa fecha"}`; `ProductoMenuNoEncontrado` → 404 `{"detail": "Menú del día no encontrado"}`; los mensajes de baja y de fecha ocupada difieren; los manejadores de `productos` no capturan estas excepciones.
  - GREEN: `router.py` con el helper `_error_de_campo` propio (decisión 11), `MANEJADORES_EXCEPCIONES` y un `APIRouter(prefix=PREFIJO)` aún sin rutas.
  - Escenarios: soporte de PMD-13, 14, 15, 18, 24, 30.

- [ ] **5.2 `POST /productos-menu` y registro en `main.py`** — Archivos: `Backend/src/productos_menu/router.py`, `Backend/src/main.py`, `Backend/tests/productos_menu/test_router_alta.py`. Depende de 5.1, 4.3, 3.1.
  - RED (H):
    - 201 con exactamente `id`, `producto_id`, `fecha` y registro persistido (PMD-03, PMD-04); fecha pasada, hoy y futura (PMD-05..07); los cinco subtipos (PMD-08).
    - 422 sin registro: `producto_id` ausente (PMD-09), `"abc"` (PMD-10), `fecha` ausente (PMD-11), `"no-es-una-fecha"` y `"2026-02-30"` (PMD-12), `producto_id` inexistente (PMD-13).
    - 409 sin registro: producto dado de baja (PMD-14), fecha ocupada con el existente intacto (PMD-15).
    - Prioridad: esquema sobre inexistente (PMD-16); inexistente sobre fecha ocupada (PMD-17); baja sobre fecha ocupada con mensaje distinto (PMD-18).
    - Rechazos 422 y 409 no cambian el conjunto persistido, con la sesión de prueba cerrada durante la petición (PMD-19).
    - Con `_verificar_fecha_libre` anulado por `monkeypatch`, la segunda alta con la misma fecha devuelve 409 y no 500 (PMD-20).
    - Segunda alta del mismo producto en otra fecha → 201 (PMD-40).
  - GREEN: `POST ""` con `status_code=201`, delgado sobre `crear_producto_menu`; `main.py` incluye el router y agrega `MANEJADORES_EXCEPCIONES` a la tupla de manejadores.
  - Escenarios (H): PMD-03..20, PMD-40.

- [ ] **5.3 `PUT /productos-menu/{producto_menu_id}`** — Archivos: `Backend/src/productos_menu/router.py`, `Backend/tests/productos_menu/test_router_modificacion.py`. Depende de 5.2, 4.4.
  - RED (H):
    - 200 al mover a fecha libre con `F1` liberada (PMD-21); conservar la fecha propia (PMD-22).
    - 409 con fecha de otro registro y ambos intactos (PMD-23); 404 con `id` inexistente (PMD-24).
    - 409 con producto dado de baja y fecha libre, también con la misma fecha (PMD-25).
    - `producto_id` en el cuerpo se ignora: 200 y el producto no cambia (PMD-26).
    - 422 con `fecha` ausente o inválida y registro sin cambios (PMD-27).
    - Prioridad: 422 sobre 404 (PMD-28); 404 sobre 409 (PMD-29); baja sobre fecha ocupada con mensaje distinto (PMD-30).
    - Rechazos 422, 404 y 409 no cambian el conjunto persistido (PMD-31).
  - GREEN: `PUT "/{producto_menu_id:int}"` con `status_code=200`.
  - Escenarios (H): PMD-21..31.

- [ ] **5.4 `DELETE /productos-menu/{producto_menu_id}`** — Archivos: `Backend/src/productos_menu/router.py`, `Backend/tests/productos_menu/test_router_borrado.py`. Depende de 5.3, 4.5.
  - RED (H): 204 sin cuerpo y registro ausente en la base (PMD-32); `id` inexistente → 404 (PMD-33); DELETE repetido → 404 (PMD-34); con producto dado de baja → 204 (PMD-35); `POST` posterior con la fecha liberada → 201 (PMD-36).
  - GREEN: `DELETE "/{producto_menu_id:int}"` con `status_code=204`.
  - Escenarios (H): PMD-32..36.

- [ ] **5.5 Baja lógica y respuestas de producto sin cambios** — **[CARACTERIZACIÓN: nace en verde]** — Archivos: `Backend/tests/productos_menu/test_integracion_productos.py`. Depende de 5.4.
  - RED (sustituido): las pruebas pasan sin cambios de código.
    - Baja lógica de un Plato con menús del día: mismo código de estado que sin menús (PMD-37); los dos registros siguen con su `producto_id` y `fecha` (PMD-38).
    - `GET` del producto con un menú del día: sin `menus_del_dia` y mismas claves que sin menú (PMD-39).
    - Mismo producto con dos fechas vía HTTP, y `Producto.menus_del_dia` contiene ambos (PMD-40).
  - GREEN: sin código; si falla, corregir el origen (p. ej. cascada o esquema de producto).
  - Escenarios (H): PMD-37..40.
  - `[COMMIT]` (Fase 5 completa).

---

## Fase 6: Verificación final y trazabilidad

- [ ] **6.1 Suite completa e importaciones** — **[CARACTERIZACIÓN: nace en verde]** — Archivos: ninguno. Depende de Fase 5.
  - Verificar `cd Backend && python -m pytest` en verde y `configure_mappers()` sin errores (PMD-01); `rg "from src.productos" Backend/src/productos_menu/models.py` sin resultados; `rg "productos_menu" Backend/src/productos` solo en `registro.py` y en cadenas de `models.py`.
  - Hecho cuando: suite en verde y grafo de importaciones acíclico.

- [ ] **6.2 Trazabilidad de escenarios** — Archivos: ninguno (solo se agregan pruebas en archivos existentes). Depende de 6.1.
  - Revisar el Anexo A: para cada uno de los 40 escenarios debe existir una prueba cuyo nombre contenga `test_pmd_NN`, con nivel H o BD donde aplica. Listar los huecos y cerrarlos con RED → GREEN o registrarlos como riesgo.
  - Hecho cuando: el listado sin cobertura está vacío y `python -m pytest` pasa.

- [ ] **6.3 Base local y comprobación manual** — Archivos: ninguno. Depende de 6.2.
  - Borrar `Backend/app.db` local, iniciar la aplicación para recrearla y comprobar `POST`, `PUT` y `DELETE /productos-menu`.
  - `[COMMIT]` final (verify queda para `sdd-verify`).

---

## Resumen

| Fase | Tareas | Commits sugeridos |
|------|--------|-------------------|
| 1 Infraestructura de pruebas | 1.1-1.2 | tras 1.2 |
| 2 Modelo, FK, índice y registro | 2.1-2.3 | tras 2.3 |
| 3 Esquemas | 3.1-3.2 | tras 3.2 |
| 4 Excepciones y servicios | 4.1-4.5 | tras 4.5 |
| 5 Router, manejadores y `main.py` | 5.1-5.5 | tras 5.5 |
| 6 Verificación final | 6.1-6.3 | tras 6.3 |

Total: 6 fases, 20 tareas.

Paralelismo: 3.1 `||` 4.1 (archivos disjuntos: `schemas.py` y `exceptions.py`). Todo lo demás es secuencial porque modifica archivos compartidos (`Backend/tests/conftest.py`, `services.py`, `router.py`).

---

## Anexo A: Trazabilidad de escenarios

### daily-menu-management (PMD, 40 escenarios)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| PMD-01 | Los mappers se configuran con la nueva entidad | 2.2, 6.1 |
| PMD-02 | La relación es bidireccional | 2.2 |
| PMD-03 | La respuesta expone solo id, producto_id y fecha | 3.1, 5.2 |
| PMD-04 | Alta válida | 4.3, 5.2 |
| PMD-05 | Fecha pasada | 3.1, 4.3, 5.2 |
| PMD-06 | Fecha de hoy | 3.1, 4.3, 5.2 |
| PMD-07 | Fecha futura | 3.1, 4.3, 5.2 |
| PMD-08 | Se acepta un producto de cualquiera de los cinco subtipos | 4.3, 5.2 |
| PMD-09 | producto_id ausente | 3.1, 5.2 |
| PMD-10 | producto_id no entero | 3.1, 5.2 |
| PMD-11 | fecha ausente | 3.1, 5.2 |
| PMD-12 | fecha inválida | 3.1, 5.2 |
| PMD-13 | producto inexistente | 4.3, 5.1, 5.2 |
| PMD-14 | producto dado de baja | 4.3, 5.1, 5.2 |
| PMD-15 | fecha ocupada | 2.2, 4.3, 5.2 |
| PMD-16 | Esquema inválido prevalece sobre producto inexistente | 5.2 |
| PMD-17 | Producto inexistente prevalece sobre fecha ocupada | 4.3, 5.2 |
| PMD-18 | Producto dado de baja prevalece sobre fecha ocupada (alta) | 4.3, 5.1, 5.2 |
| PMD-19 | Una solicitud rechazada no cambia nada (alta) | 4.3, 5.2 |
| PMD-20 | Carrera entre altas con la misma fecha | 4.3, 5.2 |
| PMD-21 | Mover a una fecha libre | 4.4, 5.3 |
| PMD-22 | Conservar la fecha propia | 4.4, 5.3 |
| PMD-23 | Fecha ocupada por otro registro | 4.4, 5.3 |
| PMD-24 | id inexistente (PUT) | 4.2, 4.4, 5.3 |
| PMD-25 | Producto dado de baja (PUT) | 4.4, 5.3 |
| PMD-26 | producto_id en el cuerpo se ignora | 3.1, 4.4, 5.3 |
| PMD-27 | fecha ausente o inválida en el PUT | 3.1, 5.3 |
| PMD-28 | Esquema inválido prevalece sobre id inexistente | 5.3 |
| PMD-29 | id inexistente prevalece sobre las reglas de negocio | 4.4, 5.3 |
| PMD-30 | Producto dado de baja prevalece sobre fecha ocupada (PUT) | 4.4, 5.1, 5.3 |
| PMD-31 | Una solicitud rechazada no cambia nada (PUT) | 4.4, 5.3 |
| PMD-32 | Borrado exitoso | 4.5, 5.4 |
| PMD-33 | id inexistente (DELETE) | 4.5, 5.4 |
| PMD-34 | DELETE repetido | 4.5, 5.4 |
| PMD-35 | El estado del producto no se verifica | 4.5, 5.4 |
| PMD-36 | La fecha liberada puede reutilizarse | 4.5, 5.4 |
| PMD-37 | La baja de un producto con menú del día está permitida | 5.5 |
| PMD-38 | Los registros permanecen tras la baja | 5.5 |
| PMD-39 | La respuesta de producto no incluye menús del día | 3.2, 5.5 |
| PMD-40 | Un producto con varias fechas | 2.2, 4.3, 5.2, 5.5 |

El Anexo A es la numeración normativa; los nombres de prueba usan el id (`test_pmd_NN_...`).

## Escenarios sin tarea asignada

Ninguno: los 40 escenarios PMD están mapeados. La tarea 6.2 verifica que cada uno tenga su prueba.
