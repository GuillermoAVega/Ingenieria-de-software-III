# Diseño: Posición de las Secciones

## Enfoque técnico

Todo el cambio queda en `Backend/src/secciones/` (rules.design: código de la entidad en su carpeta). Se agrega la columna `posicion` con índice único, el campo obligatorio en el esquema, una excepción 409 nueva y verificaciones previas de unicidad en orden fijo (`nombre` → `posicion`) dentro de la transacción. Los índices únicos siguen siendo la garantía final. Implementa el delta de `specs/section-management`.

```
HTTP ─→ router ─(Pydantic 422)─→ services: [obtener 404] → _verificar_unicidad (nombre 409 → posicion 409)
                                          → asignar → _confirmar (IntegrityError: nombre_normalizado → posicion)
```

Prioridad resultante: 422 esquema → 404 → 409 `nombre` → 409 `posicion`.

## Decisiones de arquitectura

| # | Tema | Opciones | Compromiso | Decisión |
|---|------|----------|------------|----------|
| 1 | Modelo | — | — | `posicion = mapped_column(Integer, nullable=False)` e `Index("ux_seccion_posicion", "posicion", unique=True)` en `__table_args__`. Sin `CHECK`: el `>= 1` lo garantiza el esquema, igual que `cant_personas` |
| 2 | Tipo del campo | (a) `int` laxo + `Field(ge=1)`; (b) `Field(ge=1, strict=True)` | (b) rechaza `"3"`, pero rompe la convención: `cant_personas` y `seccion_id` son `int` laxos y las pruebas envían `precio` como cadena. En (a), `3.5` ya da 422 (`int_from_float`); `"3"` y `3.0` se aceptan como `3` | **(a)**. Consistencia con el resto de la API. `SeccionRespuesta` agrega `posicion: int` |
| 3 | Prioridad ante doble colisión | (a) verificaciones previas ordenadas + índice; (b) solo índice e inspección del `IntegrityError`; (c) índice y consulta posterior al error | (b) SQLite informa una sola restricción y el orden en que recorre los índices no está documentado: no es determinista por contrato. (c) consulta tras el rollback, fuera de la transacción. (a) agrega una consulta por índice; `BEGIN IMMEDIATE` (en `configurar_sqlite`) toma el bloqueo de escritura en la primera sentencia, así que la verificación y el commit quedan serializados | **(a)**. Reemplaza la decisión 3 del diseño archivado (`nombre` solo por índice): se prioriza el determinismo sobre la consistencia con lo anterior. Las pruebas existentes de `NombreSeccionDuplicado` no cambian de resultado |
| 4 | Traducción en `_confirmar` | — | — | Tras `rollback`, se inspecciona `str(error.orig)` en orden: contiene `nombre_normalizado` → `NombreSeccionDuplicado`; contiene `seccion.posicion` → `PosicionSeccionDuplicada`; otro → se propaga. Solo se alcanza ante una carrera o un bug |
| 5 | Excepción | — | — | `PosicionSeccionDuplicada(ErrorSeccion)`, `MENSAJE = "Ya existe una sección en esa posición"`. Manejador `manejar_posicion_duplicada` → 409 `{"detail": mensaje}`, registrado en `MANEJADORES_EXCEPCIONES` (`main.py` ya los recorre) |
| 6 | Rollback | — | — | Toda salida con error revierte: `_verificar_unicidad` hace `sesion.rollback()` antes de lanzar (como `obtener_seccion`); `_confirmar` conserva su rollback |
| 7 | Fixture `crear_seccion` | (a) contador desde 1; (b) contador desde 1001 | (a) colisiona con posiciones pequeñas que las pruebas envían explícitamente | **(b)**. Parámetro `posicion=None`; si es `None`, toma `next(contador)` de un `itertools.count(1001)` creado dentro del fixture (alcance de función: se reinicia por prueba). Las pruebas usan valores explícitos menores a 1001 |
| 8 | Intercambio | — | — | Fuera de alcance: requiere tres PUT (A → temporal libre, B → posición de A, A → posición de B), cada uno con el cuerpo completo |

## Interfaces / contratos

```python
def _verificar_unicidad(sesion, nombre_normalizado: str, posicion: int, excluir_id: int | None = None) -> None:
    """Orden fijo: nombre antes que posición. Revierte y lanza el primer conflicto."""
    for columna, valor, error in (
        (Seccion.nombre_normalizado, nombre_normalizado, NombreSeccionDuplicado),
        (Seccion.posicion, posicion, PosicionSeccionDuplicada),
    ):
        consulta = select(Seccion.id).where(columna == valor)
        if excluir_id is not None:
            consulta = consulta.where(Seccion.id != excluir_id)
        if sesion.scalar(consulta) is not None:
            sesion.rollback()
            raise error()
```

`crear_seccion`: verificar → `add` → `_confirmar`. `actualizar_seccion`: `obtener` → verificar (excluyendo la propia fila) → asignar `nombre`, `nombre_normalizado`, `subtitulo`, `posicion` → `_confirmar`. La verificación precede a la asignación (la sesión usa `autoflush=False`).

## Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `Backend/src/secciones/models.py` | Modificar | Columna e índice |
| `Backend/src/secciones/schemas.py` | Modificar | `posicion: int = Field(ge=1)`; respuesta |
| `Backend/src/secciones/exceptions.py`, `router.py` | Modificar | Excepción, manejador y registro |
| `Backend/src/secciones/services.py` | Modificar | `_verificar_unicidad`, asignación, traducción |
| `Backend/tests/conftest.py` | Modificar | Autoasignación en `crear_seccion` |
| `Backend/tests/secciones/test_router.py` | Modificar | `_crear` agrega `posicion` única (contador de módulo); PUT con `posicion` (SEC-15, 16, 17, 25, 26, 27, 29, 44); respuestas exactas con `posicion` (SEC-02, 22, 25) |
| `Backend/tests/secciones/test_servicios.py` | Modificar | Todo `SeccionCrear`/`SeccionActualizar`, incluido el parametrizado de 404 |
| `Backend/tests/secciones/test_schemas.py` | Modificar | Helper `crear` con `posicion=1`; campos de la respuesta |
| `Backend/tests/secciones/test_modelos.py` | Modificar | Conjunto de columnas; los cuatro `Seccion(...)` directos con `posicion` distinta |
| `Backend/tests/secciones/test_fabrica.py`, `test_excepciones.py`, `test_manejadores.py` | Modificar | Autoasignación; jerarquía; 409 |
| `Backend/tests/productos/test_seccion_producto_http.py` | Modificar | SEC-30: POST y PUT con `posicion` |

Las demás pruebas de productos usan el fixture y no cambian.

## Estrategia de pruebas

TDD estricto: cada prueba se escribe en rojo antes del código.

| Capa | Qué prueba |
|---|---|
| Unidad | Índice `ux_seccion_posicion` único y `IntegrityError` directo; `posicion` ausente, `0`, `-1`, `3.5` → `ValidationError`; `"3"` → `3`; manejador 409 |
| Servicio | Posición repetida en alta y PUT → `PosicionSeccionDuplicada`; propia posición conservada; doble colisión → `NombreSeccionDuplicado`; sin transacción abierta tras el error; traducción en `_confirmar` con `_verificar_unicidad` anulada por `monkeypatch` (`nombre_normalizado` gana sobre `seccion.posicion`) |
| HTTP | 409 con `{"detail": ...}`; doble colisión en POST y PUT → 409 de nombre; petición rechazada no cambia nada (GET idéntico y sin fila nueva); borrar libera la posición sin renumerar; huecos permitidos; intercambio en tres PUT |

## Matriz de amenazas

N/A — sin enrutamiento de shell, subprocesos, automatización VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

Sin migraciones. `create_all` no agrega columnas: borrar `Backend/app.db` (no versionado) antes de iniciar. Las pruebas usan SQLite en memoria.

## Preguntas abiertas

- [x] ¿Se acepta que `"3"` y `3.0` se conviertan en `3` (modo laxo, como `cant_personas`), en lugar de responder 422? **Resuelta: sí, aprobado por el usuario (escenario POS-29).**
