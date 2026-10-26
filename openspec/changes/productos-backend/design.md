# Diseño: Productos Backend

## Enfoque técnico

Módulo `Backend/src/productos/` según la convención de una carpeta por entidad (rules.design: lo compartido queda en `Backend/src/`). Capas: `router.py` (HTTP, delgado) → `services.py` (reglas de negocio, sin FastAPI) → `models.py` (SQLAlchemy 2, herencia de tablas unidas sobre `ModeloBase`). Una petición = una sesión = una transacción. Las excepciones de dominio se traducen a HTTP mediante manejadores registrados en `main.py`. Implementa `specs/product-catalog` y `specs/product-logical-delete`.

```
HTTP ─→ router.py ─(Pydantic 422)─→ services.py ─→ models.py ─→ SQLite
            ▲                            │ ErrorDominio
            └── manejadores (main.py) ◀──┘  404 / 409 / 422
```

## Decisiones de arquitectura

| # | Tema | Opciones | Compromiso | Decisión |
|---|------|----------|------------|----------|
| 1 | Unicidad case-insensitive entre activos | (a) solo servicio; (b) índice parcial sobre `lower(nombre)`; (c) columna `nombre_normalizado` + índice parcial único | (b) `lower()` de SQLite es solo ASCII: "Ñandú" y "ñandú" no colisionan. Registrar una función Python en SQLite rompe el archivo para otras herramientas. (c) agrega una columna redundante | **(c) + verificación en servicio**. `nombre_normalizado = nombre.strip().casefold()` lo calcula el servicio en cada alta/edición (el `nombre` ya llega recortado por el validador de Pydantic). Índice `ux_producto_nombre_activo` UNIQUE sobre `nombre_normalizado` `WHERE dado_de_baja = 0` como respaldo. El servicio verifica primero (409 con mensaje claro); un `IntegrityError` de ese índice también se traduce a 409. Distingue tildes ("Á" ≠ "A"); solo ignora mayúsculas |
| 2 | Check-then-act en SQLite | (a) confiar en el escritor único de SQLite; (b) `BEGIN IMMEDIATE` mediante listeners del engine; (c) bloqueos a nivel aplicación | (a) pysqlite inicia la transacción recién en el primer DML, por lo que dos peticiones pueden pasar la verificación. (b) serializa también las lecturas (aceptable en un proyecto académico). (c) no protege frente a varios procesos | **(b)**. Función `configurar_sqlite(engine)` en `database.py`: listener `connect` (fija `isolation_level=None` y ejecuta `PRAGMA foreign_keys=ON`) y listener `begin` (emite `BEGIN IMMEDIATE`). Se aplica al engine real y al de pruebas. El `PRAGMA` sale de `get_db`, porque dentro de una transacción es un no-op |
| 3 | Excepciones | (a) `HTTPException` en servicios; (b) try/except en cada endpoint; (c) excepciones de dominio + manejadores globales | (a) acopla servicios a FastAPI. (b) duplica código | **(c)**. `productos/exceptions.py` es Python puro. `router.py` expone `MANEJADORES_EXCEPCIONES` y `main.py` los registra con `app.add_exception_handler`. Las excepciones raíz (`DetailedHTTPException`) no se usan en servicios porque importan FastAPI |
| 4 | Esquemas | (a) un esquema genérico con campos opcionales; (b) Base/Create/Update/Respuesta por subtipo + unión discriminada | (a) pierde la validación por subtipo | **(b)**. Respuesta polimórfica = `Annotated[Union[...], Field(discriminator="tipo")]` |
| 5 | Fecha "hoy" | (a) `date.today()` dentro del servicio; (b) parámetro `hoy` en servicios + dependencia `obtener_hoy` | (a) no es testeable sin monkeypatch | **(b)**. Los servicios reciben `hoy: date`; el router lo obtiene con `Depends(obtener_hoy)`; las pruebas lo sobrescriben con `app.dependency_overrides` |
| 6 | Pruebas | (a) archivo temporal; (b) SQLite en memoria con `StaticPool` | (a) más lento, requiere limpieza | **(b)**, esquema recreado por prueba |
| 7 | Ruta por id polimórfica | `{producto_id}` vs `{producto_id:int}` | Sin convertidor, `/productos/platos` podría capturarse como id y devolver 422 según el orden de registro | **`{producto_id:int}`** en todas las rutas por id. `POST /productos` devuelve 405 de forma nativa (la ruta existe solo con GET) |

### Contrato de errores

| Excepción (`productos/exceptions.py`) | HTTP | Cuerpo |
|---|---|---|
| `ErrorDominio` (base abstracta) | — | — |
| `ProductoNoEncontrado` | 404 | `{"detail": msg}` |
| `ComponenteInvalido(campo, ids)` (inexistente o de tipo incorrecto) | 422 | `{"detail": [{"loc": ["body", campo], "msg": msg, "type": "componente_invalido", "ids": [...]}]}` (misma forma que el 422 de Pydantic) |
| `FechaHastaVencida` (alta de combo) | 422 | idem, `loc: ["body","fecha_hasta"]` |
| `ErrorConflicto` (base 409) | 409 | `{"detail": msg}` |
| └ `NombreDuplicado`, `ComponenteInactivo(ids)`, `ComboVencidoInmutable` | 409 | `ComponenteInactivo` agrega `"ids": [...]` |
| └ `BajaRestringida(bloqueantes)` | 409 | `{"detail": msg, "bloqueantes": [10, 20]}` (ordenados) |

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

Mapeo (puntos no obvios):

```python
class Producto(ModeloBase):
    __mapper_args__ = {"polymorphic_on": "tipo", "polymorphic_abstract": True}
    def __init__(self, **kw):
        if type(self) is Producto:
            raise TypeError("Producto es abstracto")
        super().__init__(**kw)

class MenuEjecutivo(Producto):
    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    plato_id = mapped_column(ForeignKey("plato.id"))
    postre_id = mapped_column(ForeignKey("postre.id"))
    __mapper_args__ = {"polymorphic_identity": TIPO_MENU_EJECUTIVO,
                       "inherit_condition": id == Producto.id}
    plato = relationship("Plato", foreign_keys=[plato_id], back_populates="menus")
    postre = relationship("Postre", foreign_keys=[postre_id], back_populates="menus")
# Plato.menus = relationship("MenuEjecutivo", foreign_keys="MenuEjecutivo.plato_id", back_populates="plato")
# ComboPromocion.platos = relationship("Plato", secondary=combo_plato, back_populates="combos"), idem bebidas/postres
```

`ComboPromocion` expone propiedades `platos_ids`, `bebidas_ids`, `postres_ids` (listas ordenadas de ids) para la serialización con `from_attributes`. Los listados usan `selectin_polymorphic`/`selectinload` para evitar N+1.

## Archivos por responsabilidad

| Archivo | Acción | Responsabilidad |
|---|---|---|
| `Backend/src/productos/__init__.py` | Crear | Paquete |
| `Backend/src/productos/constants.py` | Crear | `TIPO_PLATO="plato"`, `TIPO_BEBIDA="bebida"`, `TIPO_POSTRE="postre"`, `TIPO_MENU_EJECUTIVO="menu_ejecutivo"`, `TIPO_COMBO_PROMOCION="combo_promocion"`; `NOMBRE_MAX=100`, `DESCRIPCION_MAX=500`, `PRECIO_DIGITOS=10`, `PRECIO_DECIMALES=2`, `CANT_PERSONAS_MIN=1`, `TIPO_MAX=30` |
| `Backend/src/productos/models.py` | Crear | Jerarquía, tablas de asociación, índice parcial |
| `Backend/src/productos/schemas.py` | Crear | `ProductoBase` (nombre, precio, descripcion, imagen; un `field_validator("nombre", mode="before")` aplica `strip()` antes de validar la longitud 1–100, de modo que vacío o solo espacios → 422); `<X>Crear`, `<X>Actualizar` (= Crear + `dado_de_baja: bool \| None = None`), `<X>Respuesta` (+ `id`, `tipo: Literal[...]`, `dado_de_baja`); `ComboCrear` con `model_validator` (≥1 id total, sin duplicados por lista, `fecha_desde <= fecha_hasta`); `ProductoRespuesta` unión discriminada. Precio: `condecimal(gt=0, max_digits=10, decimal_places=2)` |
| `Backend/src/productos/exceptions.py` | Crear | Jerarquía de la tabla anterior |
| `Backend/src/productos/services.py` | Crear | `obtener_hoy()`, lecturas genéricas `listar(db, modelo, incluir_bajas)` / `obtener(db, modelo, id)`, `crear_<x>`, `actualizar_<x>`, `dar_de_baja(db, modelo, id, hoy)`, y la función compartida `aplicar_cambio_estado(db, producto, nuevo_estado, hoy)` |
| `Backend/src/productos/router.py` | Crear | `APIRouter(prefix="/productos")`, endpoints, `MANEJADORES_EXCEPCIONES` |
| `Backend/src/main.py` | Modificar | `include_router`, registrar manejadores, importar modelos antes de `create_all` |
| `Backend/src/database.py` | Modificar | `configurar_sqlite(engine)`; quitar el `PRAGMA` de `get_db` |
| `Backend/requirements.txt` | Modificar | Agregar `pytest` (versión fijada al aplicar) |
| `Backend/pytest.ini` | Crear | `pythonpath = .`, `testpaths = tests` |
| `Backend/tests/conftest.py` | Crear | Entorno, engine, fixtures |
| `Backend/tests/productos/test_*.py` | Crear | Suite (ver Estrategia de pruebas) |
| `openspec/config.yaml` | Modificar | `test_command: "cd Backend && python -m pytest"`, `strict_tdd: true` |

### Función compartida de estado

`aplicar_cambio_estado(db, producto, nuevo_estado: bool | None, hoy)`; la usan DELETE y todos los PUT:
- `None` (campo `dado_de_baja` omitido en el PUT: conserva el estado actual) o igual al estado actual: no hace nada (DELETE repetido = 204 idempotente; PUT repetido con `dado_de_baja=True` = 200 idempotente).
- `True` (baja): si es Plato/Bebida/Postre → `buscar_bloqueantes`; si hay → `BajaRestringida`. Los compuestos no tienen RESTRICT.
- `False` (reactivación): combo vencido → `ComboVencidoInmutable`; compuesto → componentes activos (`ComponenteInactivo`); unicidad de nombre (`NombreDuplicado`).

### Orden de validación en PUT

Prioridad de errores cuando fallan varias reglas: 422 → 404 → combo vencido → componentes → nombre.

1. Pydantic (422; incluye el `strip` de `nombre`) → 2. carga por subtipo (404) → 3. combo vencido: solo pasa si `dado_de_baja=True` y `_sin_otros_cambios(combo, datos)`, esté el combo activo (queda dado de baja) o ya dado de baja (200 sin cambios, idempotente, sin escritura); cualquier otro caso, 409 → 4. componentes: existencia/tipo (422, siempre); verificación de que estén activos (409) solo si el `dado_de_baja` resultante es `False` (es decir, el compuesto queda activo) → 5. unicidad del nombre si el estado resultante es activo → 6. `aplicar_cambio_estado` → 7. asignar campos y commit.

`dado_de_baja` resultante = el valor del payload, o el estado actual si se omitió. Ejemplo: editar un menú dado de baja cuyo plato también está dado de baja, manteniéndolo dado de baja → 200.

`_sin_otros_cambios` compara el payload (sin `dado_de_baja`) con lo persistido: `nombre` (ya recortado) exacto, `precio` como `Decimal`, `descripcion`/`imagen` incluido `None`, fechas, y las listas de ids como conjuntos. PUT es reemplazo completo: un campo opcional omitido se interpreta como `None` (excepto `dado_de_baja`, que conserva el estado actual).

## Flujo: DELETE /productos/platos/{id} con RESTRICT

```
Cliente ─DELETE─→ router.eliminar_plato(id, db, hoy=Depends(obtener_hoy))
  → services.dar_de_baja(db, Plato, id, hoy)
      BEGIN IMMEDIATE (listener)
      obtener(db, Plato, id) ──── no existe ─→ ProductoNoEncontrado → 404
      aplicar_cambio_estado(db, plato, True, hoy)
        buscar_bloqueantes(db, plato, hoy) ── [10, 20] ─→ BajaRestringida → rollback → 409
      plato.dado_de_baja = True; commit ─→ 204 sin cuerpo
```

Consulta de bloqueantes (Plato; Postre análoga con `postre_id`/`combo_postre`; Bebida solo la rama de combos):

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

`conftest.py`: antes de importar `src.main` fija `os.environ["ENV"]="test"` y `os.environ["DB_URL"]="sqlite://"` (`load_dotenv` no sobrescribe). Engine `sqlite://` con `StaticPool` y `check_same_thread=False`, `configurar_sqlite(engine)`, `create_all`/`drop_all` por prueba. Sobrescribe `get_db` y `obtener_hoy` (fecha fija `HOY`). Fixture `client` = `TestClient(app)`. Comando: `cd Backend && python -m pytest`.

| Capa | Archivo | Qué prueba |
|---|---|---|
| Unidad | `test_modelos.py` | `configure_mappers()`, `Producto()` lanza error, relaciones bidireccionales |
| Integración | `test_lecturas.py` | Polimorfismo, 404, 405, `incluir_bajas` (incluido 422) |
| Integración | `test_platos_bebidas_postres.py` | CRUD y validación de campos, unicidad (incluidos "Ñ"/mayúsculas) |
| Integración | `test_menus.py`, `test_combos.py` | Composición, 422 vs 409, combos vencidos |
| Integración | `test_baja_logica.py` | DELETE, PUT de estado, RESTRICT, reactivación, invariante |

`strict_tdd` sigue en false hasta que pytest esté instalado; la primera tarea de apply es la infraestructura de pruebas.

## Matriz de amenazas

N/A — sin enrutamiento de shell, subprocesos, automatización VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

No hay migraciones: `create_all` crea las tablas nuevas. Una base existente no tiene tablas de producto, por lo que no hay conflicto.

## Riesgos

- `BEGIN IMMEDIATE` con Python 3.14 y SQLAlchemy 2.1: verificar con una prueba que se aplique `PRAGMA foreign_keys` (FK rechazada) y que las escrituras confirmen.
- Las tildes no se normalizan ("Milanesa" ≠ "Milanésa"); decisión aceptada (véase Decisiones resueltas).
- `Numeric` en SQLite emite una advertencia de Decimal; es aceptable.
- `date.today()` usa la zona horaria del servidor.

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
