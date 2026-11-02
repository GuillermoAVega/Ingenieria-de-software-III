# Diseño: Productos Backend

## Enfoque técnico

Módulo `Backend/src/productos/` según la convención de una carpeta por entidad (rules.design: lo compartido queda en `Backend/src/`). Como `Producto` es una jerarquía, cada subclase concreta tiene su propio subpaquete anidado (`platos/`, `bebidas/`, `postres/`, `menus_ejecutivos/`, `combos/`) con los seis archivos de la convención; `productos/` conserva la raíz abstracta y lo compartido (véase Estructura de módulos). Capas en cada nivel: `router.py` (HTTP, delgado) → `services.py` (reglas de negocio, sin FastAPI) → `models.py` (SQLAlchemy 2, herencia de tablas unidas sobre `ModeloBase`). Una petición = una sesión = una transacción. Las excepciones de dominio se traducen a HTTP mediante manejadores que `productos/router.py` expone y `main.py` registra. Implementa `specs/product-catalog` y `specs/product-logical-delete`.

**Alcance (reducción aprobada)**: solo ABM por subtipo y `GET /productos/<subtipo>/{id}`. No hay listados, ni lectura polimórfica, ni `incluir_bajas`; por tanto no existen la función `listar` ni la unión `ProductoRespuesta`. `productos/router.py` solo compone los routers de subpaquetes, declara la respuesta 405 de `POST /productos` y expone `MANEJADORES_EXCEPCIONES`.

```
HTTP ─→ <sub>/router.py ─(Pydantic 422)─→ <sub>/services.py ─→ productos/services.py ─→ models ─→ SQLite
            ▲                                     │ ErrorDominio
            └── manejadores (productos/router.py, registrados en main.py) ◀── 404 / 409 / 422
```

## Decisiones de arquitectura

| # | Tema | Opciones | Compromiso | Decisión |
|---|------|----------|------------|----------|
| 1 | Unicidad case-insensitive entre activos | (a) solo servicio; (b) índice parcial sobre `lower(nombre)`; (c) columna `nombre_normalizado` + índice parcial único | (b) `lower()` de SQLite es solo ASCII: "Ñandú" y "ñandú" no colisionan. Registrar una función Python en SQLite rompe el archivo para otras herramientas. (c) agrega una columna redundante | **(c) + verificación en servicio**. `nombre_normalizado = nombre.strip().casefold()` lo calcula el servicio en cada alta/edición (el `nombre` ya llega recortado por el validador de Pydantic). Índice `ux_producto_nombre_activo` UNIQUE sobre `nombre_normalizado` `WHERE dado_de_baja = 0` como respaldo. El servicio verifica primero (409 con mensaje claro); un `IntegrityError` de ese índice también se traduce a 409. Distingue tildes ("Á" ≠ "A"); solo ignora mayúsculas |
| 2 | Check-then-act en SQLite | (a) confiar en el escritor único de SQLite; (b) `BEGIN IMMEDIATE` mediante listeners del engine; (c) bloqueos a nivel aplicación | (a) pysqlite inicia la transacción recién en el primer DML, por lo que dos peticiones pueden pasar la verificación. (b) serializa también las lecturas (aceptable en un proyecto académico). (c) no protege frente a varios procesos | **(b)**. Función `configurar_sqlite(engine)` en `database.py`: listener `connect` (fija `isolation_level=None` y ejecuta `PRAGMA foreign_keys=ON`) y listener `begin` (emite `BEGIN IMMEDIATE`). Se aplica al engine real y al de pruebas. El `PRAGMA` sale de `get_db`, porque dentro de una transacción es un no-op |
| 3 | Excepciones | (a) `HTTPException` en servicios; (b) try/except en cada endpoint; (c) excepciones de dominio + manejadores globales | (a) acopla servicios a FastAPI. (b) duplica código | **(c)**. Los `exceptions.py` son Python puro: los compartidos en `productos/exceptions.py`, los exclusivos de combos en `combos/exceptions.py` (véase Contrato de errores). `productos/router.py` expone `MANEJADORES_EXCEPCIONES` y `main.py` los registra con `app.add_exception_handler`. Las excepciones raíz (`DetailedHTTPException`) no se usan en servicios porque importan FastAPI |
| 4 | Esquemas | (a) un esquema genérico con campos opcionales; (b) Base/Create/Update/Respuesta por subtipo + unión discriminada | (a) pierde la validación por subtipo | **(b)**. Bases comunes en `productos/schemas.py`; esquemas de cada subtipo en `<sub>/schemas.py`. Cada endpoint responde con el esquema `Respuesta` de su subtipo. La unión discriminada `ProductoRespuesta` (creada en la tarea 2.6) ya no la requiere ningún endpoint y se elimina (tarea 2.7) |
| 5 | Fecha "hoy" | (a) `date.today()` dentro del servicio; (b) parámetro `hoy` en servicios + dependencia `obtener_hoy` | (a) no es testeable sin monkeypatch | **(b)**. Los servicios reciben `hoy: date`; los routers lo obtienen con `Depends(obtener_hoy)` (única función, en `productos/services.py`); las pruebas lo sobrescriben con `app.dependency_overrides` |
| 6 | Pruebas | (a) archivo temporal; (b) SQLite en memoria con `StaticPool` | (a) más lento, requiere limpieza | **(b)**, esquema recreado por prueba |
| 7 | `POST /productos` → 405 sin rutas GET en `/productos` | (a) confiar en el 405 nativo; (b) ruta explícita `POST ""` que responde 405 | (a) ya no aplica: sin `GET /productos` la ruta no existe y FastAPI devolvería 404, no 405 | **(b)**. `productos/router.py` declara `POST ""` (sin cuerpo ni dependencias) que responde 405 Method Not Allowed y no crea nada. Las rutas por id de cada subpaquete usan `{producto_id:int}` |
| 8 | Registro de mappers y agregación de subpaquetes | (a) `productos/__init__.py` importa todos los modelos; (b) módulo explícito `productos/registro.py`; (c) importaciones diferidas dentro de funciones | (a) importar `src.productos.constants` cargaría todo el ORM, y el paquete padre parcialmente inicializado favorece ciclos. (c) oculta el grafo real | **(b)**. `registro.py` es el único módulo que conoce todos los subpaquetes; solo importa sus `models` (hojas). `productos/__init__.py` queda vacío |
| 9 | Lógica específica en el cambio de estado compartido | (a) `aplicar_cambio_estado` importa servicios/excepciones de menús y combos; (b) gancho `verificar_reactivacion` inyectado por el servicio del subtipo | (a) ciclo `combos.services → productos.services → combos.*` | **(b)**. La función sigue siendo única (decisión 1 de la propuesta); el subtipo compuesto aporta su verificación de reactivación |

### Contrato de errores

| Excepción | Ubicación | HTTP | Cuerpo |
|---|---|---|---|
| `ErrorDominio` (base abstracta) | `productos/exceptions.py` | — | — |
| `ProductoNoEncontrado` | `productos/exceptions.py` | 404 | `{"detail": msg}` |
| `ComponenteInvalido(campo, ids)` (inexistente o de tipo incorrecto) | `productos/exceptions.py` (la usan menús y combos) | 422 | `{"detail": [{"loc": ["body", campo], "msg": msg, "type": "componente_invalido", "ids": [...]}]}` (misma forma que el 422 de Pydantic) |
| `FechaHastaVencida` (alta de combo) | `combos/exceptions.py` | 422 | idem, `loc: ["body","fecha_hasta"]` |
| `ErrorConflicto` (base 409) | `productos/exceptions.py` | 409 | `{"detail": msg}` |
| └ `NombreDuplicado`, `ComponenteInactivo(ids)` | `productos/exceptions.py` | 409 | `ComponenteInactivo` agrega `"ids": [...]` |
| └ `ComboVencidoInmutable` | `combos/exceptions.py` (hereda de `ErrorConflicto`) | 409 | `{"detail": msg}` |
| └ `BajaRestringida(bloqueantes)` | `productos/exceptions.py` | 409 | `{"detail": msg, "bloqueantes": [10, 20]}` (ordenados) |

`MANEJADORES_EXCEPCIONES` se indexa por `ProductoNoEncontrado`, `ComponenteInvalido`, `FechaHastaVencida` y `ErrorConflicto`; Starlette resuelve por MRO, por lo que el manejador de `ErrorConflicto` cubre también `ComboVencidoInmutable`.

## Modelo de datos

| Tabla | Columnas | Restricciones |
|---|---|---|
| `producto` | `id` PK, `tipo` String(30) NOT NULL, `nombre` String(100) NOT NULL, `nombre_normalizado` String(100) NOT NULL, `precio` Numeric(10,2) NOT NULL, `descripcion` String(500) NULL, `imagen` String NULL, `dado_de_baja` Boolean NOT NULL default false | Índice parcial único `ux_producto_nombre_activo`; CHECK `precio > 0` |
| `plato` | `id` PK/FK→`producto.id`, `cant_personas` Integer NOT NULL | CHECK `cant_personas >= 1` |
| `bebida` | `id` PK/FK, `es_alcoholica` Boolean NOT NULL | |
| `postre` | `id` PK/FK | |
| `menu_ejecutivo` | `id` PK/FK→`producto.id`, `plato_id` FK→`plato.id` NOT NULL, `postre_id` FK→`postre.id` NOT NULL | Las FK apuntan a la tabla del subtipo: el tipo también lo garantiza la BD |
| `combo_promocion` | `id` PK/FK, `fecha_desde` Date, `fecha_hasta` Date | CHECK `fecha_desde <= fecha_hasta` |
| `combo_plato` / `combo_bebida` / `combo_postre` | `combo_id` FK→`combo_promocion.id`, `<x>_id` FK→`<x>.id` | PK compuesta (impide duplicados) |

Mapeo (puntos no obvios). Las referencias entre subtipos son siempre por nombre (cadena), de modo que ningún `models.py` de un subpaquete importa a otro:

```python
# productos/models.py: solo la raíz abstracta
class Producto(ModeloBase):
    __mapper_args__ = {"polymorphic_on": "tipo", "polymorphic_abstract": True}
    def __new__(cls, *a, **kw):  # __init__ lo envuelve la instrumentación de SQLAlchemy
        if cls is Producto:
            raise TypeError("Producto es abstracto")
        return super().__new__(cls)

# menus_ejecutivos/models.py: importa solo productos.models y productos.constants
class MenuEjecutivo(Producto):
    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    plato_id = mapped_column(ForeignKey("plato.id"))
    postre_id = mapped_column(ForeignKey("postre.id"))
    __mapper_args__ = {"polymorphic_identity": TIPO_MENU_EJECUTIVO,
                       "inherit_condition": id == Producto.id}
    plato = relationship("Plato", foreign_keys=[plato_id], back_populates="menus")
    postre = relationship("Postre", foreign_keys=[postre_id], back_populates="menus")

# platos/models.py
#   menus  = relationship("MenuEjecutivo", foreign_keys="MenuEjecutivo.plato_id", back_populates="plato")
#   combos = relationship("ComboPromocion", secondary="combo_plato", back_populates="platos")
# combos/models.py: define combo_plato/combo_bebida/combo_postre (dueño de la composición)
#   platos = relationship("Plato", secondary=combo_plato, back_populates="combos"), idem bebidas/postres
```

`secondary="combo_plato"` se resuelve contra `ModeloBase.metadata` en `configure_mappers`, por lo que basta con que `combos/models.py` esté cargado (lo garantiza `registro.py`). `ComboPromocion` expone propiedades `platos_ids`, `bebidas_ids`, `postres_ids` (listas ordenadas de ids) para la serialización con `from_attributes`.
## Estructura de módulos

```
Backend/src/productos/
├── __init__.py      vacío (sin efectos de importación)
├── constants.py     TIPO_* (los cinco discriminadores), NOMBRE_MAX, DESCRIPCION_MAX, PRECIO_DIGITOS, PRECIO_DECIMALES, TIPO_MAX
├── models.py        Producto abstracto, índice parcial, CHECK de precio
├── schemas.py       ProductoBase (campos comunes + strip de nombre), ProductoRespuestaBase (id, dado_de_baja, from_attributes)
├── exceptions.py    jerarquía compartida (véase Contrato de errores)
├── registro.py      MODELOS_POR_TIPO, RESTRICT_POR_TIPO (la unión ProductoRespuesta se elimina, tarea 2.7)
├── services.py      lógica compartida
├── router.py        POST "" → 405, include_router de subpaquetes, MANEJADORES_EXCEPCIONES
└── platos/ bebidas/ postres/ menus_ejecutivos/ combos/
    └── __init__.py (vacío), models.py, schemas.py, exceptions.py, constants.py, services.py, router.py
```

Contenido de cada subpaquete (ningún archivo queda vacío sin motivo; los delgados declaran su responsabilidad en el docstring del módulo):

| Subpaquete | models | schemas | exceptions | constants | services | router |
|---|---|---|---|---|---|---|
| `platos` | `Plato` | `PlatoCrear/Actualizar/Respuesta` | docstring: usa las compartidas | `CANT_PERSONAS_MIN=1`, `PREFIJO="/platos"` | `crear_plato`, `actualizar_plato` | POST, GET por id, PUT, DELETE |
| `bebidas` | `Bebida` | `Bebida*` | docstring: usa las compartidas | `PREFIJO="/bebidas"` | `crear_bebida`, `actualizar_bebida` | POST, GET por id, PUT, DELETE |
| `postres` | `Postre` | `Postre*` | docstring: usa las compartidas | `PREFIJO="/postres"` | `crear_postre`, `actualizar_postre` | POST, GET por id, PUT, DELETE |
| `menus_ejecutivos` | `MenuEjecutivo` | `Menu*` | docstring: usa `ComponenteInvalido/Inactivo` compartidas | `PREFIJO="/menus-ejecutivos"` | `resolver_componentes_menu`, `crear_menu`, `actualizar_menu` | POST, GET por id, PUT, DELETE |
| `combos` | `ComboPromocion`, `combo_plato`, `combo_bebida`, `combo_postre` | `Combo*` (`model_validator`) | `FechaHastaVencida`, `ComboVencidoInmutable` | `PREFIJO="/combos"` | `resolver_componentes_combo`, `_sin_otros_cambios`, `crear_combo`, `actualizar_combo` | POST, GET por id, PUT, DELETE |

### Grafo de importaciones (sin ciclos)

Cada módulo importa solo de niveles estrictamente inferiores:

| Nivel | Módulos | Restricción |
|---|---|---|
| 1 | `src/main.py` | importa `src.productos.registro` antes de `create_all` y `productos.router` |
| 2 | `productos/router.py` | incluye los `router` de cada subpaquete |
| 3 | `<sub>/router.py` | — |
| 4 | `<sub>/services.py` | usa `productos.services`; un compuesto obtiene los modelos de sus componentes desde `productos.registro` |
| 5 | `productos/services.py` | nunca importa `productos.<sub>.*`; accede a subtipos solo mediante `productos.registro` |
| 6 | `productos/registro.py` | importa solo `<sub>.models` |
| 7 | `<sub>/models`, `schemas`, `exceptions`, `constants` | solo su propio subpaquete y el nivel 8; nunca otro subpaquete |
| 8 | `productos/models`, `schemas`, `exceptions`, `constants`; `src/models.py`, `src/database.py` | — |

Registro de mappers: como las relaciones usan cadenas, `configure_mappers()`/`create_all` exigen que los cinco `models.py` estén cargados. Lo garantiza `productos/registro.py`, importado por `src/main.py` (tarea 7.1) y por `Backend/tests/conftest.py` (tarea 1.5), de modo que incluso una prueba que solo importa `platos.models` encuentra todos los mappers.

### Servicios compartidos y por subtipo

| `productos/services.py` (compartido) | `<sub>/services.py` |
|---|---|
| `obtener_hoy`, `normalizar_nombre`, `verificar_nombre_unico`, `obtener(db, modelo, id)` (`modelo` es siempre un subtipo concreto; no hay lectura polimórfica ni `listar`), `asignar_campos_comunes`, traducción de `IntegrityError` a `NombreDuplicado`, `buscar_bloqueantes`, `aplicar_cambio_estado`, `dar_de_baja(db, modelo, id, hoy)` | Altas y ediciones del subtipo, resolución de componentes, orden de validación del PUT; invocan las funciones compartidas |

RESTRICT sin ciclos: `registro.py` declara `RESTRICT_POR_TIPO = {TIPO_PLATO: ("plato_id", combo_plato, "plato_id"), TIPO_POSTRE: ("postre_id", combo_postre, "postre_id"), TIPO_BEBIDA: (None, combo_bebida, "bebida_id")}` (columna en `menu_ejecutivo` o `None`, tabla de asociación y su columna). `buscar_bloqueantes` arma la consulta UNION con esos datos y con `MenuEjecutivo`/`ComboPromocion` obtenidos de `registro`; un tipo ausente del mapa (compuestos) no tiene RESTRICT.

### Composición de routers

Cada `<sub>/router.py` declara `router = APIRouter(prefix=PREFIJO)` con todas sus rutas en el cuerpo del módulo (FastAPI copia las rutas al incluir; una ruta agregada después se perdería). `productos/router.py` declara `router = APIRouter(prefix="/productos")` con la ruta `POST ""` que responde 405 y ejecuta `router.include_router(...)` para los cinco subpaquetes; no declara ningún GET. `main.py` registra solo `productos.router.router` y recorre `MANEJADORES_EXCEPCIONES`.

### Función compartida de estado

`aplicar_cambio_estado(db, producto, nuevo_estado: bool | None, hoy, verificar_reactivacion=None)`; la usan DELETE y todos los PUT:
- `None` (campo `dado_de_baja` omitido en el PUT: conserva el estado actual) o igual al estado actual: no hace nada (DELETE repetido = 204 idempotente; PUT repetido con `dado_de_baja=True` = 200 idempotente).
- `True` (baja): si `producto.tipo` está en `RESTRICT_POR_TIPO` (Plato/Bebida/Postre) → `buscar_bloqueantes`; si hay → `BajaRestringida`. Los compuestos no tienen RESTRICT.
- `False` (reactivación): ejecuta `verificar_reactivacion(producto)` si se proporcionó (combos: vencido → `ComboVencidoInmutable`, luego componentes activos; menús: componentes activos → `ComponenteInactivo`); después, unicidad de nombre (`NombreDuplicado`). El gancho reutiliza la misma función de verificación de componentes del paso 4 del PUT.

### Orden de validación en PUT

Prioridad de errores cuando fallan varias reglas: 422 → 404 → combo vencido → componentes → nombre.

1. Pydantic (422; incluye el `strip` de `nombre`) → 2. carga por subtipo (404) → 3. combo vencido: solo pasa si `dado_de_baja=True` y `_sin_otros_cambios(combo, datos)`, esté el combo activo (queda dado de baja) o ya dado de baja (200 sin cambios, idempotente, sin escritura); cualquier otro caso, 409 → 4. componentes: existencia/tipo (422, siempre); verificación de que estén activos (409) solo si el `dado_de_baja` resultante es `False` (es decir, el compuesto queda activo) → 5. unicidad del nombre si el estado resultante es activo → 6. `aplicar_cambio_estado` → 7. asignar campos y commit.

`dado_de_baja` resultante = el valor del payload, o el estado actual si se omitió. Ejemplo: editar un menú dado de baja cuyo plato también está dado de baja, manteniéndolo dado de baja → 200.

`_sin_otros_cambios` compara el payload (sin `dado_de_baja`) con lo persistido: `nombre` (ya recortado) exacto, `precio` como `Decimal`, `descripcion`/`imagen` incluido `None`, fechas, y las listas de ids como conjuntos. PUT es reemplazo completo: un campo opcional omitido se interpreta como `None` (excepto `dado_de_baja`, que conserva el estado actual).

## Archivos por responsabilidad

| Archivo | Acción | Responsabilidad |
|---|---|---|
| `Backend/src/productos/__init__.py` | Crear (vacío) | Paquete |
| `Backend/src/productos/constants.py` | Crear; reducir en 1.5 | Constantes compartidas (`CANT_PERSONAS_MIN` pasa a `platos/constants.py`) |
| `Backend/src/productos/models.py` | Crear; reducir en 1.5 | Solo `Producto` |
| `Backend/src/productos/schemas.py` | Crear | `ProductoBase` (nombre, precio, descripcion, imagen; un `field_validator("nombre", mode="before")` aplica `strip()` antes de validar la longitud 1–100, de modo que vacío o solo espacios → 422; precio `condecimal(gt=0, max_digits=10, decimal_places=2)`), `ProductoRespuestaBase` |
| `Backend/src/productos/exceptions.py` | Crear | Jerarquía compartida |
| `Backend/src/productos/registro.py` | Crear; reducir en 2.7 | `MODELOS_POR_TIPO`, `RESTRICT_POR_TIPO`, reexporta tablas de asociación. `ProductoRespuesta` se elimina en 2.7 |
| `Backend/src/productos/services.py` | Crear | Servicios compartidos (tabla anterior) |
| `Backend/src/productos/router.py` | Crear | `APIRouter(prefix="/productos")`, `POST ""` → 405, inclusión de subrouters, `MANEJADORES_EXCEPCIONES` |
| `Backend/src/productos/<sub>/*.py` (×5 subpaquetes, 7 archivos cada uno) | Crear | Según la tabla de contenido por subpaquete. `<X>Actualizar` = `<X>Crear` + `dado_de_baja: bool \| None = None`; `<X>Respuesta` = `ProductoRespuestaBase` + campos propios + `tipo: Literal[...]`; `ComboCrear` con `model_validator` (≥1 id total, sin duplicados por lista, `fecha_desde <= fecha_hasta`) |
| `Backend/src/main.py` | Modificar | Importar `src.productos.registro` antes de `create_all`, `include_router`, registrar manejadores |
| `Backend/src/database.py` | Modificar | `configurar_sqlite(engine)`; quitar el `PRAGMA` de `get_db` |
| `Backend/requirements.txt` | Modificar | Agregar `pytest` (versión fijada al aplicar) |
| `Backend/pytest.ini` | Crear | `pythonpath = .`, `testpaths = tests` |
| `Backend/tests/conftest.py` | Crear | Entorno, engine, fixtures; importa `src.productos.registro` |
| `Backend/tests/productos/**` | Crear | Suite espejo de la estructura (ver Estrategia de pruebas) |
| `openspec/config.yaml` | Modificar | `test_command: "cd Backend && python -m pytest"`, `strict_tdd: true`; convención de subpaquetes anidados |

## Flujo: DELETE /productos/platos/{id} con RESTRICT

```
Cliente ─DELETE─→ platos/router.eliminar_plato(id, db, hoy=Depends(obtener_hoy))
  → productos/services.dar_de_baja(db, Plato, id, hoy)
      BEGIN IMMEDIATE (listener)
      obtener(db, Plato, id) ──── no existe ─→ ProductoNoEncontrado → 404
      aplicar_cambio_estado(db, plato, True, hoy)
        buscar_bloqueantes(db, plato, hoy) ── [10, 20] ─→ BajaRestringida → rollback → 409
      plato.dado_de_baja = True; commit ─→ 204 sin cuerpo
```

Consulta de bloqueantes (Plato; Postre análoga con `postre_id`/`combo_postre`; Bebida solo la rama de combos; columnas y tablas tomadas de `RESTRICT_POR_TIPO`):

```sql
SELECT m.id FROM menu_ejecutivo m JOIN producto p ON p.id = m.id
 WHERE m.plato_id = :id AND p.dado_de_baja = 0
UNION
SELECT c.id FROM combo_plato cp
  JOIN combo_promocion c ON c.id = cp.combo_id
  JOIN producto p ON p.id = c.id
 WHERE cp.plato_id = :id AND p.dado_de_baja = 0 AND c.fecha_hasta >= :hoy
ORDER BY 1
```

## Estrategia de pruebas

`conftest.py`: antes de importar `src.main` fija `os.environ["ENV"]="test"` y `os.environ["DB_URL"]="sqlite://"` (`load_dotenv` no sobrescribe); importa `src.productos.registro`. Engine `sqlite://` con `StaticPool` y `check_same_thread=False`, `configurar_sqlite(engine)`, `create_all`/`drop_all` por prueba. Sobrescribe `get_db` y `obtener_hoy` (fecha fija `HOY`). Fixture `client` = `TestClient(app)`. Comando: `cd Backend && python -m pytest`.

Las pruebas reflejan la estructura: `Backend/tests/productos/` para lo compartido y `Backend/tests/productos/<sub>/` por subpaquete. Cada carpeta de pruebas tiene `__init__.py` (obligatorio: los nombres de archivo se repiten entre carpetas). Las funciones auxiliares de creación de objetos ORM pasan a fixtures fábrica en `Backend/tests/productos/conftest.py`, visibles para todas las subcarpetas.

| Capa | Archivo(s) | Qué prueba |
|---|---|---|
| Unidad | `productos/test_modelos.py`, `productos/test_registro.py` | `Producto()` lanza error, índice parcial, `configure_mappers()` global, `MODELOS_POR_TIPO` |
| Unidad | `productos/<sub>/test_modelos.py`, `test_schemas.py` | Tablas, CHECK y relaciones bidireccionales del subtipo; validación de esquemas |
| Integración (servicio) | `productos/test_servicios_lectura.py` (obtención por id y unicidad de nombre), `test_bloqueantes.py`, `test_estado_baja.py`, `test_estado_reactivacion.py`; `productos/<sub>/test_servicios.py` | Reglas compartidas y por subtipo |
| Integración (HTTP) | `productos/test_manejadores.py`, `test_baja_logica.py`, `test_invariante.py` | Manejadores, 404, 405, DELETE/PUT de estado, RESTRICT, invariante |
| Integración (HTTP) | `productos/<sub>/test_router.py` | ABM, GET por id y validación de campos por subtipo, composición, 422 vs 409, combos vencidos |

## Matriz de amenazas

N/A — sin enrutamiento de shell, subprocesos, automatización VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

No hay migraciones: `create_all` crea las tablas nuevas. Una base existente no tiene tablas de producto, por lo que no hay conflicto. La reorganización en subpaquetes (tarea 1.5) no cambia nombres de tablas ni columnas.

## Riesgos

- `BEGIN IMMEDIATE` con Python 3.14 y SQLAlchemy 2.1: verificar con una prueba que se aplique `PRAGMA foreign_keys` (FK rechazada) y que las escrituras confirmen.
- Las tildes no se normalizan ("Milanesa" ≠ "Milanésa"); decisión aceptada (véase Decisiones resueltas).
- `Numeric` en SQLite emite una advertencia de Decimal; es aceptable.
- `date.today()` usa la zona horaria del servidor.
- Un módulo que use un subtipo sin que `registro.py` esté cargado falla en `configure_mappers` (nombre no resuelto). Mitigación: `conftest.py` y `main.py` importan `registro.py`; prueba de `configure_mappers()` global.
- Sin `GET /productos`, la ruta `/productos` no existe salvo por el `POST ""` explícito: si se omitiera, `POST /productos` devolvería 404 en lugar de 405. Lo cubre la prueba CAT-01 (tarea 7.1).
- Código ya escrito que queda obsoleto por la reducción de alcance: `ProductoRespuesta` y sus pruebas (se eliminan en la tarea 2.7). Las clases `Respuesta` de cada subtipo se conservan.

## Decisiones resueltas

Aprobadas por el usuario; sustituyen al informe de ambigüedades.

1. **Desactivación idempotente de un combo vencido ya dado de baja**: un PUT con `dado_de_baja = true` y sin otros cambios sobre un combo con `fecha_hasta < today` que YA está dado de baja devuelve 200 sin cambios (coherente con DELETE repetido → 204). Cualquier otro cambio sobre un combo vencido sigue devolviendo 409.
2. **Validación de componentes solo si el compuesto queda activo**: en el PUT de MenuEjecutivo/ComboPromocion, la comprobación de que los componentes existen y están ACTIVOS (409 si alguno está inactivo) se ejecuta solo si el `dado_de_baja` resultante es `false`. Las comprobaciones de existencia/tipo de los ids (422) se aplican siempre. Ejemplo: editar un menú dado de baja cuyo plato está dado de baja, manteniéndolo dado de baja → 200.
3. **Recorte de `nombre`**: se recortan los espacios iniciales y finales antes de validar, almacenar y comprobar unicidad (validador de Pydantic para `strip`; `nombre_normalizado` = strip + casefold). Vacío o solo espacios → 422; la longitud 1–100 se aplica tras el recorte; "  Milanesa " entra en conflicto (409) con un "Milanesa" activo.
4. **Decisiones adicionales aceptadas**:
   - Un `dado_de_baja` omitido en el PUT conserva el estado actual.
   - El PUT es reemplazo completo: los campos opcionales omitidos pasan a `null`.
   - Solo se ignoran las mayúsculas; las tildes son distintas ("Milanesa" ≠ "Milanésa").
   - Prioridad de errores cuando fallan varias reglas: 422 → 404 → combo vencido → componentes → nombre.
5. **Subpaquetes anidados por subtipo**: cada subclase concreta de `Producto` tiene su carpeta dentro de `productos/` con los seis archivos de la convención; `productos/` conserva la raíz abstracta y lo compartido.
6. **Reducción de alcance**: solo ABM por subtipo y `GET /productos/<subtipo>/{id}`. Se eliminan del diseño `GET /productos`, `GET /productos/{id}`, los listados por subtipo, `?incluir_bajas`, la función `listar` y la unión `ProductoRespuesta`. Se conservan `MODELOS_POR_TIPO` y `RESTRICT_POR_TIPO` (los usa RESTRICT) y todas las reglas de negocio.
