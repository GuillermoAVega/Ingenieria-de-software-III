# Tareas: Productos Backend

Cambio: `productos-backend`. Entradas: `proposal.md`, `design.md`, `specs/product-catalog/spec.md` (CAT, 46 escenarios vigentes), `specs/product-logical-delete/spec.md` (LD, 23 escenarios vigentes). Comando de pruebas: `cd Backend && python -m pytest`. Los identificadores de escenario (CAT-nn, LD-nn) se definen en el Anexo A.

**Reducción de alcance (aprobada)**: el cambio implementa solo el ABM por subtipo y `GET /productos/<subtipo>/{id}`. Se eliminan los listados, la lectura polimórfica y `?incluir_bajas`: la Fase 8 queda eliminada, se quitan las partes de listado de 3.1, 7.2 y 7.4, y se agrega la tarea 2.7 (REFACTOR) para borrar la unión `ProductoRespuesta` ya implementada en 2.6. Las tareas ya marcadas `[x]` se conservan como historial con una nota; no se renumera nada.

## Convenciones

- **TDD estricto**: cada tarea de implementación sigue RED (escribir pruebas que fallan por el motivo correcto) → GREEN (código mínimo) → REFACTOR (opcional, con la suite en verde). El par prueba+código se entrega junto.
- **Punto de commit**: tarea marcada con `[COMMIT]` = unidad de trabajo lista para confirmar (pruebas + código, suite en verde). Se confirma con commits convencionales, sin atribución de IA.
- Rutas relativas a la raíz del repositorio. Las pruebas viven en `Backend/tests/`.
- Estructura (design.md, Estructura de módulos): lo compartido en `Backend/src/productos/`; cada subtipo en su subpaquete anidado `Backend/src/productos/<sub>/` (`platos`, `bebidas`, `postres`, `menus_ejecutivos`, `combos`). Las pruebas lo reflejan: `Backend/tests/productos/` (compartido) y `Backend/tests/productos/<sub>/`, cada carpeta con `__init__.py`. Las fases 0 y 1 se implementaron con la estructura plana; la tarea 1.5 las reorganiza antes de continuar.
- Los escenarios se cubren en dos niveles: **S** = nivel servicio (excepción de dominio / efecto en BD, fases 3 a 6) y **H** = nivel HTTP con `TestClient` (código de estado y cuerpo, fase 7). El criterio de cierre global exige que todo escenario tenga su prueba H (tarea 9.2).
- Desviación de orden respecto del pedido: `aplicar_cambio_estado` (fase 4) se coloca antes de MenuEjecutivo y ComboPromocion porque todos los PUT (incluidos los de los subtipos simples) lo invocan. `constants.py` se crea en la fase 1 (1.1) porque los modelos usan los `TIPO_*`.
- Orden de dependencias: Fase 0 → 1 (incluida 1.5) → 2 (incluida 2.7, que debe cerrarse antes de iniciar la Fase 3) → 3 → 4 → 5 → 6 → 7 → 9 (la Fase 8 fue eliminada). Dentro de cada fase el orden es secuencial salvo que se indique `||` (paralelizable).

---

## Fase 0: Infraestructura de pruebas

- [x] **0.1 Instalar pytest y configuración base** — Archivos: `Backend/requirements.txt`, `Backend/pytest.ini`, `Backend/tests/__init__.py` (si hace falta), `Backend/tests/test_smoke.py` (temporal).
  - RED: `python -m pytest` falla (pytest no instalado / sin configuración); prueba de humo trivial que importa `src` (requiere `pythonpath = .`).
  - GREEN: agregar `pytest` (versión fijada) a `requirements.txt`, instalarlo, crear `pytest.ini` con `pythonpath = .` y `testpaths = tests`. Verificar que `openspec/config.yaml` ya contiene `test_command` y `strict_tdd: true` (no requiere cambios).
  - Escenarios: CAT-50 (parcial).
  - Hecho cuando: `cd Backend && python -m pytest` descubre y ejecuta la prueba de humo en verde.

- [x] **0.2 Fixtures aisladas en `conftest.py`** — Archivos: `Backend/tests/conftest.py`, `Backend/tests/test_infraestructura.py`. Depende de 0.1.
  - RED: pruebas que usan fixtures `motor`, `sesion`, `cliente`, `HOY` y comprueban que `get_db` está sobrescrito, que `obtener_hoy` devuelve `HOY` y que el archivo SQLite real no se toca (URL del engine = `sqlite://`).
  - GREEN: `conftest.py` fija `os.environ["ENV"]="test"` y `os.environ["DB_URL"]="sqlite://"` antes de importar `src.main`; engine `sqlite://` con `StaticPool` y `check_same_thread=False`; `create_all`/`drop_all` por prueba; override de `get_db`; fixture `cliente = TestClient(app)`. El override de `obtener_hoy` queda diferido a 7.1 (donde nace la dependencia); aquí se deja la constante `HOY` fija y el fixture preparado.
  - Escenarios: CAT-50 (La suite se ejecuta de forma aislada), con ejecución sin variables de entorno externas.
  - Hecho cuando: las pruebas pasan sin variables de entorno externas y sin crear ni modificar el archivo SQLite real. Eliminar `test_smoke.py`.
  - `[COMMIT]` junto con 0.1 (infraestructura mínima ejecutable).

- [x] **0.3 `configurar_sqlite(engine)` en `database.py`** — Archivos: `Backend/src/database.py`, `Backend/tests/test_database.py`, `Backend/tests/conftest.py` (usar `configurar_sqlite` en el engine de prueba). Depende de 0.2.
  - RED: (a) prueba que inserta una fila con FK inexistente y espera `IntegrityError` (demuestra `PRAGMA foreign_keys=ON`); (b) prueba que una escritura confirma (`commit`) y es visible desde otra sesión del mismo engine bajo `BEGIN IMMEDIATE`; (c) prueba que el listener `begin` emite `BEGIN IMMEDIATE` (captura de eventos o `PRAGMA`/log); (d) prueba de que `get_db` ya no ejecuta el `PRAGMA`.
  - GREEN: crear `configurar_sqlite(engine)` con listener `connect` (`isolation_level=None`, `PRAGMA foreign_keys=ON`) y listener `begin` (`BEGIN IMMEDIATE`); aplicarlo al engine real; quitar el `PRAGMA` de `get_db`.
  - Escenarios: soporte de CAT-50; mitiga el riesgo de `BEGIN IMMEDIATE`/Python 3.14/SQLAlchemy 2.1 y respalda la atomicidad de CAT-30..33, CAT-34..40, LD-10..15.
  - Hecho cuando: las pruebas (a)–(d) pasan y la aplicación sigue arrancando (`import src.main` sin error).
  - `[COMMIT]` (Fase 0 completa).

---

## Fase 1: Constantes y modelos

- [x] **1.1 `constants.py`** — Archivos: `Backend/src/productos/__init__.py`, `Backend/src/productos/constants.py`, `Backend/tests/productos/__init__.py`, `Backend/tests/productos/test_constantes.py`.
  - RED: prueba que importa cada constante (`TIPO_PLATO`, `TIPO_BEBIDA`, `TIPO_POSTRE`, `TIPO_MENU_EJECUTIVO`, `TIPO_COMBO_PROMOCION`, `NOMBRE_MAX=100`, `DESCRIPCION_MAX=500`, `PRECIO_DIGITOS=10`, `PRECIO_DECIMALES=2`, `CANT_PERSONAS_MIN=1`, `TIPO_MAX=30`) y comprueba valores y que los `TIPO_*` son distintos y caben en `TIPO_MAX`.
  - GREEN: crear paquete y `constants.py`.
  - Escenarios: soporte (valores usados por CAT-18, CAT-20, CAT-28).
  - Hecho cuando: la prueba pasa.

- [x] **1.2 `Producto` abstracto + Plato, Bebida, Postre** — Archivos: `Backend/src/productos/models.py`, `Backend/tests/productos/test_modelos.py`. Depende de 1.1.
  - RED: `Producto()` lanza `TypeError` (CAT-02); `create_all` crea `producto`, `plato`, `bebida`, `postre` con las columnas del diseño; persistir un Plato, una Bebida y un Postre y releerlos con el `tipo` correcto; `CHECK precio > 0` y `CHECK cant_personas >= 1` rechazados por la BD; índice parcial `ux_producto_nombre_activo` existe, rechaza dos activos con igual `nombre_normalizado` y permite un activo + uno dado de baja (respaldo de CAT-25).
  - GREEN: `Producto(ModeloBase)` con `polymorphic_on`, `polymorphic_abstract` y `__init__` que rechaza la instancia directa; subtipos con herencia de tablas unidas; índice parcial único; CHECK.
  - Escenarios: CAT-02 (Instanciación directa rechazada, S); soporte de CAT-21..25.
  - Hecho cuando: las pruebas pasan.

- [x] **1.3 `MenuEjecutivo` y relaciones bidireccionales con Plato/Postre** — Archivos: `Backend/src/productos/models.py`, `Backend/tests/productos/test_modelos.py`. Depende de 1.2.
  - RED: `configure_mappers()` no lanza `AmbiguousForeignKeysError` (CAT-03); `MenuEjecutivo.plato` / `Plato.menus` y `MenuEjecutivo.postre` / `Postre.menus` son bidireccionales (`back_populates` comprobado asignando de un lado y leyendo del otro); FK a `plato.id`/`postre.id` rechaza con la BD un `plato_id` de una Bebida (FK ya activa por 0.3).
  - GREEN: `MenuEjecutivo` con `inherit_condition`, `foreign_keys` explícitos en cada relationship.
  - Escenarios: CAT-03 (Los mappers se configuran, parcial: se completa en 1.4).
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]` junto con 1.1 y 1.2 (jerarquía base) si se prefiere un solo commit de modelos parciales; de lo contrario, continuar a 1.4.

- [x] **1.4 `ComboPromocion`, tablas de asociación y propiedades `*_ids`** — Archivos: `Backend/src/productos/models.py`, `Backend/tests/productos/test_modelos.py`. Depende de 1.3.
  - RED: `configure_mappers()` global sin errores con los cinco subtipos (CAT-03); `combo_plato`/`combo_bebida`/`combo_postre` con PK compuesta (un duplicado lanza `IntegrityError`); relaciones `ComboPromocion.platos/bebidas/postres` ↔ `Plato.combos/Bebida.combos/Postre.combos` bidireccionales; `platos_ids`, `bebidas_ids`, `postres_ids` devuelven listas ordenadas; `CHECK fecha_desde <= fecha_hasta` rechazado por la BD (respaldo de CAT-29).
  - GREEN: modelo, tablas secundarias, propiedades, `back_populates`.
  - Escenarios: CAT-03 (completo); soporte de CAT-29.
  - Hecho cuando: pasan todas las pruebas de `test_modelos.py`.
  - `[COMMIT]` (Fase 1 completa: constantes + modelos).

- [x] **1.5 Reorganizar en subpaquetes anidados** — Depende de 1.4. Paso REFACTOR: el comportamiento no cambia y la suite permanece en verde.
  - Archivos de código: crear `Backend/src/productos/{platos,bebidas,postres,menus_ejecutivos,combos}/` con `__init__.py` (vacío) y los seis archivos de la convención (`models.py`, `schemas.py`, `exceptions.py`, `constants.py`, `services.py`, `router.py`); mover `Plato` a `platos/models.py`, `Bebida` a `bebidas/models.py`, `Postre` a `postres/models.py`, `MenuEjecutivo` a `menus_ejecutivos/models.py`, `ComboPromocion` y `combo_plato`/`combo_bebida`/`combo_postre` a `combos/models.py`; reducir `Backend/src/productos/models.py` a `Producto`; mover `CANT_PERSONAS_MIN` de `Backend/src/productos/constants.py` a `Backend/src/productos/platos/constants.py`; crear `Backend/src/productos/registro.py` (parte de modelos: importa los cinco `models.py`, `MODELOS_POR_TIPO`, reexporta las tablas de asociación). Los archivos aún sin contenido (`schemas.py`, `exceptions.py`, `services.py`, `router.py` de cada subpaquete) llevan solo el docstring del módulo con su responsabilidad; se completan en las tareas que los nombran.
  - Referencias entre subtipos solo por cadena: `relationship("MenuEjecutivo", foreign_keys="MenuEjecutivo.plato_id", ...)`, `secondary="combo_plato"`/`"combo_bebida"`/`"combo_postre"` en Plato/Bebida/Postre. Ningún `<sub>/models.py` importa otro subpaquete.
  - Archivos de prueba: `Backend/tests/conftest.py` (importa `src.productos.registro`); `Backend/tests/productos/conftest.py` (las funciones `crear_plato`, `crear_bebida`, `crear_postre`, `crear_menu`, `crear_combo` de `test_modelos.py` pasan a fixtures fábrica); dividir `Backend/tests/productos/test_modelos.py`: queda lo compartido (Producto abstracto, CHECK de precio, índice parcial, `create_all`, `configure_mappers()` con los cinco subtipos) y se crean `Backend/tests/productos/{platos,bebidas,postres,menus_ejecutivos,combos}/__init__.py` y `test_modelos.py` con las pruebas propias de cada subtipo; mover la verificación de `CANT_PERSONAS_MIN` de `test_constantes.py` a `Backend/tests/productos/platos/test_constantes.py`; crear `Backend/tests/productos/test_registro.py`.
  - RED: única prueba nueva, `test_registro.py`: `MODELOS_POR_TIPO` contiene los cinco `TIPO_*` y cada clase tiene su `polymorphic_identity`; `configure_mappers()` no falla tras importar solo `src.productos.registro`. El resto son pruebas existentes reubicadas, con sus importaciones adaptadas y sin cambiar aserciones.
  - GREEN/REFACTOR: mover el código; `cd Backend && python -m pytest` en verde con el mismo número de pruebas previas más las de `test_registro.py`.
  - Los archivos no confirmados de la fase 2 (`Backend/src/productos/exceptions.py`, `Backend/src/productos/schemas.py` y sus pruebas) quedan fuera de este commit; se retoman en 2.1 y 2.2 con la ubicación nueva.
  - Escenarios: CAT-02 y CAT-03 siguen cubiertos (sin cambio de comportamiento).
  - Hecho cuando: la suite completa pasa, `src/productos/models.py` solo define `Producto` y ningún `<sub>/models.py` importa otro subpaquete.
  - `[COMMIT]` (refactor: reorganización en subpaquetes).

---

## Fase 2: Excepciones y esquemas

- [x] **2.1 Excepciones compartidas y de combos** — Archivos: `Backend/src/productos/exceptions.py`, `Backend/src/productos/combos/exceptions.py`, `Backend/tests/productos/test_excepciones.py`, `Backend/tests/productos/combos/test_excepciones.py`. Depende de 1.5. `||` con 2.2.
  - RED: pruebas de la jerarquía compartida (`ErrorConflicto` base de `NombreDuplicado`, `ComponenteInactivo(ids)`, `BajaRestringida(bloqueantes)` con lista ordenada; `ProductoNoEncontrado`; `ComponenteInvalido(campo, ids)`) y de la de combos (`ComboVencidoInmutable` hereda de `ErrorConflicto`; `FechaHastaVencida` hereda de `ErrorDominio`); ningún módulo importa FastAPI (comprobar `sys.modules` o inspección de imports).
  - GREEN: crear las clases según el contrato de errores (design.md indica la ubicación de cada una); el borrador no confirmado de `productos/exceptions.py` se reparte entre ambos archivos.
  - Escenarios: soporte del contrato 404/409/422 (todas las pruebas H de las fases 7 y 8).
  - Hecho cuando: las pruebas pasan.

- [x] **2.2 `ProductoBase`: validación de campos comunes** — Archivos: `Backend/src/productos/schemas.py`, `Backend/tests/productos/test_schemas.py`. Depende de 1.5. `||` con 2.1.
  - RED (unidad Pydantic): nombre `""` → error (CAT-15); `"   "` → error (CAT-16); `"  Milanesa "` → `"Milanesa"` (CAT-17); 101 caracteres → error (CAT-18); `precio=0` → error (CAT-19); precio negativo, más de 2 decimales y más de 10 dígitos → error; `descripcion` de 501 → error (CAT-20); `descripcion`/`imagen` opcionales (`None`).
  - GREEN: `ProductoBase` con `field_validator("nombre", mode="before")` (strip), `condecimal(gt=0, max_digits=10, decimal_places=2)`, longitudes; `ProductoRespuestaBase` (`id`, `dado_de_baja`, `from_attributes`).
  - Escenarios (S, nivel esquema): CAT-15, CAT-16, CAT-17, CAT-18, CAT-19, CAT-20.
  - Hecho cuando: las pruebas pasan.

- [x] **2.3 Esquemas Plato, Bebida, Postre** — Archivos: `Backend/src/productos/platos/schemas.py`, `Backend/src/productos/bebidas/schemas.py`, `Backend/src/productos/postres/schemas.py`, `Backend/tests/productos/platos/test_schemas.py`, `Backend/tests/productos/bebidas/test_schemas.py`, `Backend/tests/productos/postres/test_schemas.py`. Depende de 2.2.
  - RED: `PlatoCrear` con `cant_personas=0` → error (CAT-28) y ausente → error; `BebidaCrear` sin `es_alcoholica` → error (CAT-27); `PostreCrear` acepta solo campos comunes; `*Actualizar` = Crear + `dado_de_baja: bool | None = None` (omitido → `None`); `*Respuesta` con `id`, `tipo: Literal`, `dado_de_baja` y `from_attributes`.
  - GREEN: esquemas Crear/Actualizar/Respuesta de los tres subtipos.
  - Escenarios (S): CAT-27, CAT-28; soporte de CAT-12 (`dado_de_baja` opcional).
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]` junto con 2.1 y 2.2 (excepciones + base de esquemas).

- [x] **2.4 Esquemas MenuEjecutivo** — Archivos: `Backend/src/productos/menus_ejecutivos/schemas.py`, `Backend/tests/productos/menus_ejecutivos/test_schemas.py`. Depende de 2.2.
  - RED: `MenuCrear` exige `plato_id` y `postre_id`; `MenuActualizar` agrega `dado_de_baja`; `MenuRespuesta` con `tipo="menu_ejecutivo"`.
  - GREEN: esquemas del menú.
  - Escenarios (S): soporte de CAT-30..33, CAT-42..44.
  - Hecho cuando: las pruebas pasan.

- [x] **2.5 Esquemas ComboPromocion** — Archivos: `Backend/src/productos/combos/schemas.py`, `Backend/tests/productos/combos/test_schemas.py`. Depende de 2.2.
  - RED: `ComboCrear` con tres listas vacías → error (CAT-35); un solo id en una lista → válido (CAT-36); ids repetidos en una lista → error (CAT-37); `fecha_desde > fecha_hasta` → error (CAT-29); falta de fechas o de una lista → error; `ComboRespuesta` expone `platos_ids/bebidas_ids/postres_ids` desde atributos del modelo.
  - GREEN: `ComboCrear` con `model_validator`; `ComboActualizar`; `ComboRespuesta`.
  - Escenarios (S, esquema): CAT-29, CAT-35, CAT-36, CAT-37.
  - Hecho cuando: las pruebas pasan.

- [x] **2.6 Unión discriminada `ProductoRespuesta`** — *Historial: tarea completada, pero la unión quedó obsoleta por la reducción de alcance (ningún endpoint la usa) y se elimina en la tarea 2.7.* Archivos: `Backend/src/productos/registro.py`, `Backend/tests/productos/test_registro.py`. Depende de 2.3, 2.4, 2.5. (Se ubica en `registro.py` para evitar el ciclo `productos.schemas ↔ <sub>.schemas`.)
  - RED: `TypeAdapter(ProductoRespuesta)` valida instancias ORM de los cinco subtipos y resuelve cada una al esquema correcto según `tipo`; `tipo` desconocido → error.
  - GREEN: `Annotated[Union[...], Field(discriminator="tipo")]`.
  - Escenarios (S): soporte de CAT-04, CAT-05.
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]` (excepciones y esquemas; 2.4–2.6 pueden ir en un commit aparte).

- [x] **2.7 REFACTOR: eliminar la unión `ProductoRespuesta` obsoleta** — Archivos: `Backend/src/productos/registro.py`, `Backend/tests/productos/test_registro.py`. Depende de 2.6. Debe completarse antes de continuar con la Fase 3.
  - Motivo: la reducción de alcance elimina la lectura polimórfica; ningún requisito usa `ProductoRespuesta`.
  - REFACTOR (sin RED nuevo; la suite permanece en verde): borrar `ProductoRespuesta` y los imports de `<sub>.schemas` que solo ella usaba de `registro.py` (que queda importando solo los `models`); borrar de `test_registro.py` las pruebas de la unión (`TypeAdapter(ProductoRespuesta)`, resolución por `tipo`, `tipo` desconocido). Se conservan `MODELOS_POR_TIPO`, `RESTRICT_POR_TIPO` (aún no creado; llega en 4.1), la reexportación de las tablas de asociación y las pruebas de `MODELOS_POR_TIPO` y `configure_mappers()`. Las clases `Respuesta` de cada subtipo (2.3–2.5) no se tocan.
  - Escenarios: ninguno nuevo; CAT-04 y CAT-05 (soporte de 2.6) quedan eliminados con el alcance.
  - Hecho cuando: `cd Backend && python -m pytest` pasa, `rg ProductoRespuesta Backend` no devuelve resultados salvo `ProductoRespuestaBase`, y `registro.py` ya no importa ningún `schemas`.
  - `[COMMIT]` (refactor: elimina la unión polimórfica de respuesta; Fase 2 completa).

---

## Fase 3: Servicios de subtipos simples (Plato, Bebida, Postre)

- [x] **3.1 Obtención por id genérica + unicidad de nombre** — Archivos: `Backend/src/productos/services.py`, `Backend/tests/productos/test_servicios_lectura.py`. Depende de 2.7, 1.5, 2.1. (Sin `listar` ni lectura polimórfica: fuera de alcance.)
  - RED: `obtener(db, modelo, id)` con `modelo` subtipo concreto devuelve dados de baja (CAT-10 S) y lanza `ProductoNoEncontrado` si el id no existe o es de otro subtipo (CAT-08 S); `normalizar_nombre()` = `strip().casefold()` y distingue tildes; `verificar_nombre_unico(db, nombre, excluir_id)` lanza `NombreDuplicado` frente a activo (CAT-21, CAT-22, CAT-23 S) e ignora dados de baja (CAT-25 S), tildes distintas OK (CAT-24 S), excluye el propio id (CAT-26 S); `obtener_hoy()` devuelve `date.today()`.
  - GREEN: `obtener_hoy`, `obtener`, `normalizar_nombre`, `verificar_nombre_unico`. `services.py` no importa subpaquetes.
  - Escenarios (S): CAT-08, CAT-10, CAT-21..26.
  - Hecho cuando: las pruebas pasan.

- [x] **3.2 `crear_plato` y `actualizar_plato`** — Archivos: `Backend/src/productos/platos/services.py`, `Backend/src/productos/services.py` (auxiliares compartidos: asignación de campos comunes y traducción de `IntegrityError`), `Backend/tests/productos/platos/test_servicios.py`. Depende de 3.1.
  - RED: crear persiste con `nombre_normalizado` calculado y devuelve id (CAT-07 S); nombre duplicado (exacto, mayúsculas, espacios) → `NombreDuplicado` (CAT-21..23 S); `IntegrityError` del índice parcial se traduce a `NombreDuplicado`; actualizar con el mismo nombre OK (CAT-26 S); actualizar id desconocido → `ProductoNoEncontrado` (CAT-11 S); actualizar es reemplazo completo: omitir `descripcion`/`imagen` los deja en `None` (CAT-13 S); `dado_de_baja` omitido conserva el estado (CAT-12 S, con el plato dado de baja y `dado_de_baja=None`; el cambio de estado explícito se cablea en 4.3).
  - GREEN: funciones mínimas con commit y rollback.
  - Escenarios (S): CAT-07, CAT-11, CAT-12, CAT-13, CAT-21..26 (para Plato).
  - Hecho cuando: las pruebas pasan.

- [x] **3.3 `crear_bebida` / `actualizar_bebida` y `crear_postre` / `actualizar_postre`** — Archivos: `Backend/src/productos/bebidas/services.py`, `Backend/src/productos/postres/services.py`, `Backend/tests/productos/bebidas/test_servicios.py`, `Backend/tests/productos/postres/test_servicios.py`. Depende de 3.2.
  - RED: crear/actualizar de cada uno (campos específicos `es_alcoholica`; Postre sin campos extra); duplicado de nombre entre subtipos distintos (un Plato "Milanesa" activo bloquea a una Bebida "Milanesa": CAT-21 S, unicidad global entre todos los productos); id de otro subtipo → `ProductoNoEncontrado` (CAT-08 S, CAT-11 S); reemplazo completo (CAT-13 S).
  - GREEN: reutilizar el patrón de 3.2 sin duplicar (los auxiliares compartidos de `productos/services.py`; REFACTOR de 3.2 si es útil).
  - Escenarios (S): CAT-07, CAT-08, CAT-11, CAT-13, CAT-21 (para Bebida y Postre).
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]` (Fase 3 completa: lecturas y servicios simples). REFACTOR: confirmar con la suite en verde que no queda duplicación entre subtipos.

---

## Fase 4: Cambio de estado y RESTRICT (servicio compartido)

- [x] **4.1 `buscar_bloqueantes`** — Archivos: `Backend/src/productos/registro.py` (`RESTRICT_POR_TIPO`), `Backend/src/productos/services.py`, `Backend/tests/productos/test_bloqueantes.py`. Depende de 1.5, 3.1.
  - RED (filas creadas con el ORM): Plato en un menú activo → `[10]` (LD-10); Bebida en un combo activo con `fecha_hasta >= HOY` → `[20]` (LD-11); Postre en combo con `fecha_desde` futura y `fecha_hasta >= HOY` → incluye el combo (LD-12); Plato en menú 10 y combo 20 → `[10, 20]` ordenado (LD-13); menú dado de baja y combo vencido → `[]` (LD-14); combo activo vencido (`fecha_hasta < HOY`) → `[]` (LD-15); `fecha_hasta == HOY` bloquea (límite).
  - GREEN: `RESTRICT_POR_TIPO` en `registro.py` y consulta UNION del diseño construida a partir de ese mapa (rama de menús para Plato y Postre; solo combos para Bebida; tipos ausentes del mapa → `[]`), con `hoy` recibido por parámetro. `services.py` obtiene tablas y modelos solo desde `registro`.
  - Escenarios (S): LD-12, LD-13, LD-14, LD-15 (completos a nivel servicio); LD-10 y LD-11 (parcial: detección sin excepción).
  - Hecho cuando: las pruebas pasan.

- [x] **4.2 `aplicar_cambio_estado` — baja y RESTRICT** — Archivos: `Backend/src/productos/services.py`, `Backend/tests/productos/test_estado_baja.py`. Depende de 4.1, 2.1.
  - RED: `nuevo_estado=None` o igual al actual → sin efecto ni consulta de bloqueantes (idempotente, LD-03 S, LD-04..09 soporte); `True` sobre Plato/Bebida/Postre con bloqueantes → `BajaRestringida(bloqueantes)` ordenada (LD-10, LD-11, LD-12, LD-13 S); `True` sin bloqueantes → baja (LD-14, LD-15 S); `True` sobre MenuEjecutivo y ComboPromocion sin RESTRICT (LD-16, LD-18 soporte S); tras `BajaRestringida` el estado persistido no cambia y el menú sigue activo (LD-23 S, invariante).
  - GREEN: rama de baja de `aplicar_cambio_estado`.
  - Escenarios (S): LD-10..15, LD-23.
  - Hecho cuando: las pruebas pasan.

- [x] **4.3 `aplicar_cambio_estado` — reactivación y `dar_de_baja`; cableado en PUT de Plato/Bebida/Postre** — Archivos: `Backend/src/productos/services.py`, `Backend/src/productos/platos/services.py`, `Backend/src/productos/bebidas/services.py`, `Backend/src/productos/postres/services.py`, `Backend/tests/productos/test_estado_reactivacion.py`, `Backend/tests/productos/platos/test_servicios.py`. Depende de 4.2, 3.3.
  - RED: reactivar Plato dado de baja → activo (LD-09 S); con `verificar_reactivacion` provisto, se invoca antes de la unicidad y su excepción se propaga sin cambiar el estado; reactivar Bebida dada de baja con nombre único → activa (LD-22 S); reactivar con nombre activo duplicado → `NombreDuplicado` (LD-21 S); `dar_de_baja(db, modelo, id, hoy)`: baja sin borrar la fila (LD-01 S), 404 id desconocido o de otro subtipo (LD-02 S), repetido idempotente (LD-03 S); PUT con `dado_de_baja=True` sobre Postre sin bloqueantes (LD-08 S); PUT con `dado_de_baja=False` sobre activo = edición normal (LD-05 S); PUT sin `dado_de_baja` sobre dado de baja conserva (LD-07 S, CAT-12 S); PUT `dado_de_baja=True` sobre ya dado de baja → 200 sin cambio. (LD-04 y LD-06 los resuelve el esquema, 2.2, y se prueban a nivel H en 7.3.)
  - GREEN: rama de reactivación (parámetro opcional `verificar_reactivacion`, que aquí queda en `None`; nombre, ya con `verificar_nombre_unico`), `dar_de_baja`, y llamada a `aplicar_cambio_estado` en `actualizar_plato/bebida/postre` (orden del diseño: carga → unicidad solo si el estado resultante es activo → estado → asignar → commit).
  - Escenarios (S): LD-01, LD-02, LD-03, LD-05, LD-07, LD-08, LD-09, LD-21, LD-22.
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]` (Fase 4 completa: estado + RESTRICT para subtipos simples). REFACTOR: confirmar que la lógica de baja/reactivación existe en una única función compartida.

---

## Fase 5: Servicios de MenuEjecutivo

- [ ] **5.1 Resolución y validación de componentes de menú** — Archivos: `Backend/src/productos/menus_ejecutivos/services.py`, `Backend/tests/productos/menus_ejecutivos/test_servicios.py`. Depende de 4.3, 2.4.
  - RED: `resolver_componentes_menu(db, plato_id, postre_id, exigir_activos)`: `plato_id` de una Bebida → `ComponenteInvalido("plato_id", [4])` (CAT-31 S); `postre_id` inexistente → `ComponenteInvalido("postre_id", [999])` (CAT-32 S); Plato dado de baja con `exigir_activos=True` → `ComponenteInactivo` (CAT-33 S); con `exigir_activos=False` no lanza.
  - GREEN: función auxiliar de validación (existencia/tipo siempre; actividad condicional); `Plato` y `Postre` se obtienen desde `productos.registro`.
  - Escenarios (S): CAT-31, CAT-32, CAT-33.
  - Hecho cuando: las pruebas pasan.

- [ ] **5.2 `crear_menu` y `actualizar_menu`** — Archivos: `Backend/src/productos/menus_ejecutivos/services.py`, `Backend/tests/productos/menus_ejecutivos/test_servicios.py`. Depende de 5.1.
  - RED: crear con Plato y Postre activos → persiste (CAT-30 S); nombre duplicado → `NombreDuplicado` (CAT-21 S); actualizar menú activo con Postre dado de baja → `ComponenteInactivo` y el menú no cambia (CAT-42 S); editar menú dado de baja con Plato inactivo, manteniéndolo de baja (`dado_de_baja=True` u omitido) → OK (CAT-43 S); PUT de menú dado de baja con `postre_id=999` manteniéndolo de baja → `ComponenteInvalido` (CAT-44 S); reactivar menú con componente inactivo → `ComponenteInactivo` y sigue de baja (LD-19 S); reactivar menú con componentes activos → OK (soporte LD-20); reactivar con nombre en conflicto → `NombreDuplicado`; cambio de precio de un Plato no cambia el del menú (CAT-41 S); `dar_de_baja` de un menú sin RESTRICT, componentes intactos (LD-16 S); prioridad de errores en el servicio: 404 → componentes → nombre (CAT-14 parcial S: 404 antes que 409/422 de componentes).
  - GREEN: funciones respetando el orden de validación del diseño y `aplicar_cambio_estado` (con `verificar_reactivacion` = verificación de componentes activos del menú).
  - Escenarios (S): CAT-21, CAT-30, CAT-33, CAT-41, CAT-42, CAT-43, CAT-44, LD-16, LD-19.
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]` (Fase 5 completa).

---

## Fase 6: Servicios de ComboPromocion

- [ ] **6.1 Resolución de componentes de combo y creación** — Archivos: `Backend/src/productos/combos/services.py`, `Backend/tests/productos/combos/test_servicios.py`. Depende de 5.2, 2.5.
  - RED: `crear_combo` válido con componentes activos y `fecha_hasta >= HOY` (CAT-34 S); un solo componente en una lista (CAT-36 S); `bebidas_ids` con un id de Plato o inexistente → `ComponenteInvalido("bebidas_ids", ids)` (CAT-38 S); Bebida dada de baja → `ComponenteInactivo` (CAT-39 S); `fecha_hasta < HOY` → `FechaHastaVencida` (CAT-40 S); `fecha_hasta == HOY` aceptada; nombre duplicado (CAT-21 S); atomicidad: ante error no queda fila parcial.
  - GREEN: `resolver_componentes_combo` y `crear_combo`.
  - Escenarios (S): CAT-21, CAT-34, CAT-36, CAT-38, CAT-39, CAT-40.
  - Hecho cuando: las pruebas pasan.

- [ ] **6.2 `actualizar_combo`: revalidación de componentes y estado** — Archivos: `Backend/src/productos/combos/services.py`, `Backend/tests/productos/combos/test_servicios.py`. Depende de 6.1.
  - RED: actualizar combo activo con componente inactivo → `ComponenteInactivo`, sin cambios (CAT-42 análogo S); combo de baja editado manteniéndolo de baja con componente inactivo → OK (CAT-43 análogo S); id de componente inexistente con combo de baja → `ComponenteInvalido` (CAT-44 análogo S); reactivar combo no vencido con componentes activos → activo (LD-20 S); reactivar con componente inactivo → `ComponenteInactivo`; reactivar con nombre en conflicto → `NombreDuplicado`.
  - GREEN: `actualizar_combo` con el orden del diseño y `aplicar_cambio_estado` (con `verificar_reactivacion` = combo vencido → `ComboVencidoInmutable`, luego componentes activos).
  - Escenarios (S): LD-20 (completo), soporte CAT-42..44 para combos.
  - Hecho cuando: las pruebas pasan.

- [ ] **6.3 Combos vencidos inmutables y baja libre de compuestos** — Archivos: `Backend/src/productos/combos/services.py`, `Backend/tests/productos/combos/test_servicios_vencido.py`. Depende de 6.2.
  - RED: PUT con nueva `descripcion` sobre combo con `fecha_hasta` de ayer → `ComboVencidoInmutable` (CAT-45 S); reactivar combo vencido de baja → `ComboVencidoInmutable` (CAT-46 S); PUT `dado_de_baja=True` sin otros cambios sobre combo vencido activo → queda de baja (CAT-47 S); igual sobre combo vencido ya de baja → 200 sin escritura (CAT-48 S, verificar que no hay commit/cambio); `dado_de_baja=True` con nuevo `precio` → `ComboVencidoInmutable` y sin cambios (CAT-49 S); `_sin_otros_cambios` compara `nombre` recortado, `precio` como `Decimal`, `descripcion`/`imagen` incluido `None`, fechas y listas como conjuntos; `dar_de_baja` de combo vencido activo → queda de baja (LD-17 S); PUT de baja de combo no vencido con datos válidos → de baja (LD-18 S).
  - GREEN: `_sin_otros_cambios` y paso 3 del orden de validación.
  - Escenarios (S): CAT-45, CAT-46, CAT-47, CAT-48, CAT-49, LD-17, LD-18.
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]` (Fase 6 completa: todos los servicios).

---

## Fase 7: Router, manejadores de excepciones y `main.py` (pruebas HTTP)

- [ ] **7.1 Router base (`POST /productos` → 405), composición de subrouters, manejadores y registro en `main.py`** — Archivos: `Backend/src/productos/router.py`, `Backend/src/productos/{platos,bebidas,postres,menus_ejecutivos,combos}/router.py` (`APIRouter(prefix=PREFIJO)` sin rutas aún), `Backend/src/productos/{platos,bebidas,postres,menus_ejecutivos,combos}/constants.py` (`PREFIJO`), `Backend/src/main.py`, `Backend/tests/conftest.py` (override de `obtener_hoy`), `Backend/tests/productos/test_manejadores.py`. Depende de Fase 6.
  - RED: `POST /productos` → 405 (CAT-01 H) y no crea nada; manejadores traducen `ProductoNoEncontrado` → 404 `{"detail"}`, `ComponenteInvalido`/`FechaHastaVencida` → 422 con la forma de Pydantic (`loc`, `msg`, `type`, `ids`), `ErrorConflicto` → 409 (incluido `ComboVencidoInmutable`, por MRO), `ComponenteInactivo` agrega `ids`, `BajaRestringida` agrega `bloqueantes` ordenados; no existe ninguna ruta GET en `/productos` (`GET /productos` y `GET /productos/{id}` no están definidas); las rutas por id de los subpaquetes usan `{producto_id:int}`; los `PREFIJO` valen `/platos`, `/bebidas`, `/postres`, `/menus-ejecutivos`, `/combos`; `main.py` importa `src.productos.registro` antes de `create_all` y registra el router y los `MANEJADORES_EXCEPCIONES`.
  - GREEN: `APIRouter(prefix="/productos")` con `include_router` de los cinco subrouters, `MANEJADORES_EXCEPCIONES` (importa `FechaHastaVencida` de `combos/exceptions.py`), ruta explícita `POST ""` que responde 405 (design.md, decisión 7); cambios en `main.py`. La dependencia `obtener_hoy` ya existe en `productos/services.py` (3.1).
  - Escenarios (H): CAT-01.
  - Hecho cuando: las pruebas pasan y la app arranca con el router registrado.

- [ ] **7.2 Endpoints de Plato, Bebida y Postre (GET por id, POST, PUT)** — Archivos: `Backend/src/productos/platos/router.py`, `Backend/src/productos/bebidas/router.py`, `Backend/src/productos/postres/router.py`, `Backend/tests/productos/platos/test_router.py`, `Backend/tests/productos/bebidas/test_router.py`, `Backend/tests/productos/postres/test_router.py`. Depende de 7.1.
  - RED (HTTP): crear plato → 201 con id (CAT-07); `GET /productos/platos/{id}` con id de una Bebida → 404 (CAT-08); `GET /productos/postres/{id}` dado de baja → 200 con `dado_de_baja=true` (CAT-10); PUT id desconocido → 404 (CAT-11); PUT sin `dado_de_baja` conserva estado (CAT-12); PUT reemplazo completo (CAT-13); `precio=0` en PUT a id 999 → 422 antes que 404 (CAT-14); validaciones de campos vía HTTP para POST de plato/bebida/postre: nombre `""` (CAT-15), `"   "` (CAT-16), recorte (CAT-17), 101 caracteres (CAT-18), `precio=0` (CAT-19), descripcion 501 (CAT-20); duplicados exacto/mayúsculas/espacios → 409 (CAT-21, CAT-22, CAT-23); tildes → 201 (CAT-24); reutilización tras baja → 201 (CAT-25); PUT con el mismo nombre → 200 (CAT-26); Bebida sin `es_alcoholica` → 422 (CAT-27); `cant_personas=0` → 422 (CAT-28).
  - GREEN: endpoints GET por id, POST, PUT por subtipo con respuestas desde el esquema, declarados en el cuerpo de cada `<sub>/router.py`. No se implementa ningún listado.
  - Escenarios (H): CAT-07, CAT-08, CAT-10..28 (excepto los de menú/combo; CAT-09 fue eliminado).
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]` (endpoints simples).

- [ ] **7.3 DELETE lógico y PUT de estado para Plato, Bebida y Postre** — Archivos: `Backend/src/productos/platos/router.py`, `Backend/src/productos/bebidas/router.py`, `Backend/src/productos/postres/router.py`, `Backend/tests/productos/test_baja_logica.py` (transversal a los subtipos). Depende de 7.2, 4.3.
  - RED (HTTP): DELETE plato libre → 204 sin cuerpo y GET muestra `dado_de_baja=true` (LD-01); DELETE bebida 999 → 404 (LD-02); DELETE repetido de Postre → 204 (LD-03); PUT `dado_de_baja=true` y `precio=0` → 422 y sigue activo (LD-04); PUT `dado_de_baja=false` sobre activo → 200 con nueva descripción (LD-05); PUT `dado_de_baja=false` con `nombre=""` → 422 (LD-06); PUT sin `dado_de_baja` sobre Postre dado de baja → 200 sigue de baja (LD-07); Postre de baja vía PUT → 200 (LD-08); reactivar Plato vía PUT → 200 (LD-09); DELETE bloqueado por menú activo → 409 con `bloqueantes=[10]` y el plato sigue activo (LD-10 y LD-23); PUT de Bebida bloqueado por combo → 409 con `[20]` (LD-11); combo futuro bloquea (LD-12); múltiples bloqueantes `[10, 20]` (LD-13); compuestos de baja/vencidos no bloquean (LD-14); combo vencido activo no bloquea y responde 204 (LD-15); reactivar con nombre en conflicto → 409 (LD-21); reactivar Bebida única → 200 (LD-22).
  - GREEN: endpoints DELETE (204) y PUT con `dado_de_baja` para los tres subtipos simples; sin lógica nueva de servicio.
  - Escenarios (H): LD-01..15 (ver Anexo para la numeración), LD-21, LD-22, LD-23.
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]` (baja lógica HTTP de subtipos simples).

- [ ] **7.4 Endpoints de MenuEjecutivo** — Archivos: `Backend/src/productos/menus_ejecutivos/router.py`, `Backend/tests/productos/menus_ejecutivos/test_router.py`. Depende de 7.3, 5.2.
  - RED (HTTP): menú válido → 201 (CAT-30); `plato_id` de una Bebida → 422 con `loc ["body","plato_id"]` (CAT-31); `postre_id=999` → 422 (CAT-32); Plato inactivo → 409 (CAT-33); cambio de precio de Plato no altera el del menú (CAT-41); PUT con Postre inactivo → 409 y menú sin cambios (CAT-42); PUT de menú de baja con Plato inactivo manteniéndolo de baja, con `dado_de_baja=true` y sin el campo → 200 (CAT-43); PUT de menú de baja con `postre_id=999` → 422 (CAT-44); DELETE de menú → 204 y componentes sin cambios (LD-16); reactivar menú con Plato inactivo → 409 y sigue de baja (LD-19); `GET /productos/menus-ejecutivos/{id}` verifica el estado (sin listado).
  - GREEN: endpoints GET por id/POST/PUT/DELETE de `/productos/menus-ejecutivos`.
  - Escenarios (H): CAT-30..33, CAT-41..44, LD-16, LD-19.
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]`.

- [ ] **7.5 Endpoints de ComboPromocion** — Archivos: `Backend/src/productos/combos/router.py`, `Backend/tests/productos/combos/test_router.py`. Depende de 7.4, 6.3.
  - RED (HTTP): combo válido → 201 (CAT-34); listas vacías → 422 (CAT-35); un único componente → 201 (CAT-36); ids duplicados → 422 (CAT-37); `bebidas_ids` con id de Plato o inexistente → 422 con `ids` (CAT-38); Bebida inactiva → 409 con `ids` (CAT-39); `fecha_hasta` anterior a hoy → 422 con `loc ["body","fecha_hasta"]` (CAT-40); `fecha_desde > fecha_hasta` → 422 (CAT-29); editar combo vencido → 409 (CAT-45); reactivar vencido → 409 (CAT-46); baja vía PUT de combo vencido activo → 200 de baja (CAT-47); repetida → 200 sin cambios (CAT-48); baja con nuevo `precio` → 409 sin cambios (CAT-49); DELETE de combo vencido → 204 (LD-17); baja de combo no vencido vía PUT → 200 (LD-18); reactivar combo con componentes activos → 200 (LD-20).
  - GREEN: endpoints GET por id/POST/PUT/DELETE de `/productos/combos` (sin listado).
  - Escenarios (H): CAT-29, CAT-34..40, CAT-45..49, LD-17, LD-18, LD-20.
  - Hecho cuando: las pruebas pasan.
  - `[COMMIT]`.

---

## Fase 8: ELIMINADA (fuera de alcance)

~~8.1 `GET /productos` y `GET /productos/{producto_id:int}` (lectura polimórfica)~~ — eliminada por la reducción de alcance aprobada. Los listados, la lectura polimórfica y `?incluir_bajas` no se implementan. Escenarios eliminados: CAT-04, CAT-05, CAT-06, CAT-09, LD-24, LD-25, LD-26 (véase Anexo A). La numeración de fases no se altera: la Fase 9 conserva su número.

---

## Fase 9: Cierre

- [ ] **9.1 Suite completa y verificación de la invariante** — Archivos: `Backend/tests/productos/test_invariante.py` (si hace falta prueba adicional). Depende de la Fase 7 (la Fase 8 fue eliminada).
  - RED: prueba de propiedad ligera: tras una secuencia de operaciones (altas, bajas bloqueadas y permitidas, reactivaciones, ediciones, combos vencidos) ningún menú activo ni combo activo con `fecha_hasta >= HOY` referencia un componente inactivo (LD-23, invariante general; respaldo de LD-10..15).
  - GREEN: ajustes mínimos si la invariante falla; ejecutar `cd Backend && python -m pytest` completo en verde; comprobar que `Producto` no se puede crear por HTTP ni instanciar.
  - Escenarios: LD-23 (completo), criterios de éxito de la propuesta.
  - Hecho cuando: suite completa en verde, sin advertencias nuevas relevantes (la advertencia de `Numeric` en SQLite es aceptada) y sin tocar el archivo SQLite real.

- [ ] **9.2 Verificación de trazabilidad de escenarios** — Archivos: ninguno (revisión; solo se corrige añadiendo pruebas en los archivos de pruebas existentes). Depende de 9.1.
  - Revisar el Anexo A: para cada uno de los 69 escenarios vigentes (46 CAT + 23 LD; los 7 marcados "eliminado" no se verifican) debe existir al menos una prueba H (o S/unidad para CAT-02, CAT-03, CAT-50) con el nombre del escenario en el nombre o docstring de la prueba. Listar cualquier escenario sin prueba; cada hueco se cierra con RED → GREEN o se registra como riesgo.
  - Hecho cuando: el listado de escenarios sin cobertura está vacío (o documentado) y `python -m pytest` pasa.
  - `[COMMIT]` final del cambio (verify queda para la fase `sdd-verify`).

---

## Resumen

| Fase | Tareas | Commits sugeridos |
|------|--------|-------------------|
| 0 Infraestructura | 0.1, 0.2, 0.3 | tras 0.2 y tras 0.3 |
| 1 Constantes y modelos | 1.1–1.5 | tras 1.2 (opcional), tras 1.4 y tras 1.5 (refactor a subpaquetes) |
| 2 Excepciones y esquemas | 2.1–2.7 | tras 2.3, tras 2.6 y tras 2.7 (refactor) |
| 3 Servicios simples | 3.1–3.3 | tras 3.3 |
| 4 Estado y RESTRICT | 4.1–4.3 | tras 4.3 |
| 5 MenuEjecutivo (servicio) | 5.1–5.2 | tras 5.2 |
| 6 ComboPromocion (servicio) | 6.1–6.3 | tras 6.3 |
| 7 Router y HTTP | 7.1–7.5 | tras 7.2, 7.3, 7.4, 7.5 |
| 8 Lectura polimórfica | ~~8.1~~ (eliminada) | — |
| 9 Cierre | 9.1–9.2 | tras 9.2 |

Total: 9 fases activas (la Fase 8 está eliminada), 33 tareas (se eliminó 8.1 y se agregó 2.7).

Paralelismo: 2.1 `||` 2.2; 2.3, 2.4 y 2.5 `||` entre sí tras 2.2 (escriben en subpaquetes distintos). El resto es secuencial porque cada tarea depende de servicios previos o modifica archivos compartidos (`productos/services.py`, `productos/router.py`, `productos/registro.py`; un solo escritor).

---

## Anexo A: Numeración de escenarios

Criterio de numeración: los ids se mantienen estables (no se renumera). Los escenarios que dejan de existir por la reducción de alcance se conservan en la tabla marcados como "eliminado (fuera de alcance)", sin tarea asignada y sin prueba requerida; los ids eliminados no se reutilizan.

### product-catalog (CAT, 46 vigentes + 4 eliminados = 50 ids)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| CAT-01 | La creación genérica no es posible | 7.1 |
| CAT-02 | Instanciación directa rechazada | 1.2 |
| CAT-03 | Los mappers se configuran | 1.3, 1.4 |
| CAT-04 | ~~Listado mixto~~ — eliminado (fuera de alcance) | — |
| CAT-05 | ~~Obtener por id un producto dado de baja (polimórfico)~~ — eliminado (fuera de alcance) | — |
| CAT-06 | ~~Id desconocido (polimórfico)~~ — eliminado (fuera de alcance) | — |
| CAT-07 | Crear plato | 3.2, 7.2 |
| CAT-08 | Id de subtipo incorrecto | 3.1, 3.3, 7.2 |
| CAT-09 | ~~El listado por subtipo excluye las bajas por defecto~~ — eliminado (fuera de alcance) | — |
| CAT-10 | Obtener por id un producto dado de baja (reformulado: sin `incluir_bajas`, por subtipo) | 3.1, 7.2 |
| CAT-11 | Actualizar un id desconocido | 3.2, 3.3, 7.2 |
| CAT-12 | PUT sin dado_de_baja conserva el estado actual | 3.2, 4.3, 7.2 |
| CAT-13 | PUT como reemplazo completo | 3.2, 3.3, 7.2 |
| CAT-14 | Prioridad de errores 422 sobre 404 | 5.2 (parcial), 7.2 |
| CAT-15 | nombre vacío | 2.2, 7.2 |
| CAT-16 | nombre compuesto solo de espacios | 2.2, 7.2 |
| CAT-17 | nombre se recorta antes de almacenarse | 2.2, 7.2 |
| CAT-18 | nombre demasiado largo | 2.2, 7.2 |
| CAT-19 | precio no positivo | 2.2, 7.2 |
| CAT-20 | descripcion demasiado larga | 2.2, 7.2 |
| CAT-21 | nombre activo duplicado | 3.1, 3.2, 3.3, 5.2, 6.1, 7.2 |
| CAT-22 | nombre activo duplicado sin distinguir mayúsculas | 3.1, 3.2, 7.2 |
| CAT-23 | nombre activo duplicado con espacios sobrantes | 3.1, 3.2, 7.2 |
| CAT-24 | Las tildes distinguen nombres | 3.1, 7.2 |
| CAT-25 | Reutilización del nombre tras la baja | 1.2, 3.1, 7.2 |
| CAT-26 | La actualización conserva el propio nombre | 3.1, 3.2, 7.2 |
| CAT-27 | Bebida sin es_alcoholica | 2.3, 7.2 |
| CAT-28 | cant_personas inválido | 2.3, 7.2 |
| CAT-29 | Rango de fechas invertido | 2.5, 7.5 |
| CAT-30 | Menú válido | 5.2, 7.4 |
| CAT-31 | plato_id es una Bebida | 5.1, 7.4 |
| CAT-32 | postre_id inexistente | 5.1, 7.4 |
| CAT-33 | Plato inactivo | 5.1, 5.2, 7.4 |
| CAT-34 | Combo válido | 6.1, 7.5 |
| CAT-35 | Combo vacío | 2.5, 7.5 |
| CAT-36 | Combo con un único componente en una sola lista | 2.5, 6.1, 7.5 |
| CAT-37 | Ids de componentes duplicados | 2.5, 7.5 |
| CAT-38 | Tipo incorrecto o id inexistente | 6.1, 7.5 |
| CAT-39 | Componente inactivo | 6.1, 7.5 |
| CAT-40 | Vencido en la creación | 6.1, 7.5 |
| CAT-41 | Cambio de precio de un componente | 5.2, 7.4 |
| CAT-42 | Actualizar un menú con un componente inactivo | 5.2, 6.2, 7.4 |
| CAT-43 | Editar un menú dado de baja cuyo componente está inactivo | 5.2, 6.2, 7.4 |
| CAT-44 | Un id de componente inexistente se rechaza aunque el compuesto quede dado de baja | 5.2, 6.2, 7.4 |
| CAT-45 | Editar un combo vencido | 6.3, 7.5 |
| CAT-46 | Reactivar un combo vencido | 6.3, 7.5 |
| CAT-47 | Dar de baja un combo vencido vía PUT | 6.3, 7.5 |
| CAT-48 | Dar de baja de nuevo un combo vencido ya dado de baja vía PUT | 6.3, 7.5 |
| CAT-49 | Dar de baja un combo vencido vía PUT modificando otros campos | 6.3, 7.5 |
| CAT-50 | La suite se ejecuta de forma aislada | 0.1, 0.2, 0.3 |

### product-logical-delete (LD, 23 vigentes + 3 eliminados = 26 ids)

| ID | Escenario | Tarea(s) |
|----|-----------|----------|
| LD-01 | Dar de baja un plato | 4.3, 7.3 |
| LD-02 | Id desconocido (DELETE) | 4.3, 7.3 |
| LD-03 | DELETE repetido | 4.2, 4.3, 7.3 |
| LD-04 | PUT con dado_de_baja true y cuerpo inválido | 7.3 (el 422 lo resuelve el esquema, 2.2) |
| LD-05 | PUT con dado_de_baja false sobre un producto activo | 4.3, 7.3 |
| LD-06 | PUT con dado_de_baja false sobre un producto activo y cuerpo inválido | 2.2, 7.3 |
| LD-07 | PUT sin dado_de_baja sobre un producto dado de baja | 4.3, 7.3 |
| LD-08 | Dar de baja vía PUT | 4.3, 7.3 |
| LD-09 | Reactivar vía PUT | 4.3, 7.3 |

| LD-10 | Bloqueado por un menú activo (DELETE) | 4.1, 4.2, 7.3 |
| LD-11 | Bloqueado por un combo activo (PUT) | 4.1, 4.2, 7.3 |
| LD-12 | Bloqueado por un combo futuro | 4.1, 4.2, 7.3 |
| LD-13 | Múltiples bloqueantes | 4.1, 4.2, 7.3 |
| LD-14 | Los compuestos dados de baja o vencidos no bloquean | 4.1, 4.2, 7.3 |
| LD-15 | Un combo vencido pero activo no bloquea la baja | 4.1, 4.2, 7.3 |
| LD-16 | Dar de baja un menú | 4.2, 5.2, 7.4 |
| LD-17 | Dar de baja un combo vencido mediante DELETE | 6.3, 7.5 |
| LD-18 | Dar de baja un combo vía PUT | 6.3, 7.5 |
| LD-19 | Reactivar un menú con un componente inactivo | 5.2, 7.4 |
| LD-20 | Reactivar un combo con componentes activos | 6.2, 7.5 |
| LD-21 | Conflicto de nombre en la reactivación | 4.3, 7.3 |
| LD-22 | Reactivar un componente | 4.3, 7.3 |
| LD-23 | Invariante tras una baja bloqueada | 4.2, 7.3, 9.1 |
| LD-24 | ~~Excluye por defecto~~ — eliminado (fuera de alcance) | — |
| LD-25 | ~~Incluir bajas~~ — eliminado (fuera de alcance) | — |
| LD-26 | ~~Valor de bandera inválido~~ — eliminado (fuera de alcance) | — |

Nota: LD-09 (Reactivar vía PUT) también se cubre en 4.3 (S). El Anexo A es la numeración normativa; los nombres de prueba deben usar el nombre del escenario tal como figura aquí.

## Escenarios sin tarea asignada

Ninguno: los 69 escenarios vigentes (46 CAT + 23 LD) están mapeados en el Anexo A; los 7 ids eliminados (CAT-04, CAT-05, CAT-06, CAT-09, LD-24, LD-25, LD-26) no requieren tarea. La tarea 9.2 verifica que cada escenario vigente tenga una prueba con su nombre.
