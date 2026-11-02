# Diseño: Ids de Productos en la Respuesta de Sección

## Enfoque técnico

El cambio queda en `Backend/src/secciones/` (rules.design). `Seccion` gana una propiedad de solo lectura `productos_ids` que recorre la relación existente `productos`, descarta los dados de baja y ordena los ids. `SeccionRespuesta` agrega `productos_ids: list[int]` y lo lee por `from_attributes`. No cambian servicios, router, columnas ni la dirección de importación. Implementa el delta de `specs/section-management`.

```
router ─→ services (commit) ─→ Seccion (expirada) ─→ SeccionRespuesta.model_validate
                                   └─ productos_ids ─→ carga diferida de `productos` (1 SELECT) ─→ filtro + sorted
```

## Decisiones de arquitectura

| # | Tema | Opciones | Compromiso | Decisión |
|---|------|----------|------------|----------|
| 1 | Cálculo | (a) propiedad sobre `productos`; (b) consulta en un servicio; (c) relación filtrada (`primaryjoin` por cadena, `viewonly`, `order_by`) | (a) filtra en Python, sin importar `productos`: lee `p.dado_de_baja` sobre instancias; sigue el precedente de `platos_ids` en combos. (b) `secciones.services` necesitaría `Producto` (rompe la restricción) o `ModeloBase.metadata.tables["producto"]`/`text()` (acoplamiento por cadena de tabla y columna), y el router tendría que armar la respuesta a mano. (c) filtra y ordena en SQL, pero agrega una segunda relación sobre la misma FK que mantener y probar | **(a)**. Mínimo cambio y patrón conocido. (c) queda como evolución si el volumen crece |
| 2 | Carga | `lazy="select"` (actual); `selectin`/`joined` | Cada respuesta serializa una sola sección y no hay listado de secciones: la carga diferida emite exactamente un `SELECT` sobre `producto` por respuesta, sin N+1. `selectin`/`joined` cargarían productos en toda carga de `Seccion` (incluido `obtener_seccion` dentro del borrado), contra la prueba `test_eliminar_no_carga_los_productos_de_la_seccion` | **Sin cambios** en la relación. Un futuro listado usará `selectinload` en su propia consulta |
| 3 | Costo polimórfico | — | `Producto` usa herencia de tablas unidas sin `with_polymorphic`: la carga consulta solo la tabla `producto` (que contiene `id`, `tipo`, `dado_de_baja`, `seccion_id`) e instancia el subtipo por `tipo`. Como la propiedad solo lee columnas de la base, no se disparan cargas de tablas hijas por fila | Aceptado; cubierto por una prueba de conteo de sentencias |
| 4 | Respuesta | — | `from_attributes` lee propiedades igual que columnas (precedente: `ComboRespuesta`) | `productos_ids: list[int]` en `SeccionRespuesta`, después de `posicion` |
| 5 | Frescura tras commit | — | `SessionLocal` y las sesiones de prueba usan `expire_on_commit=True` (valor por defecto; `database.py` no lo cambia). El servicio retorna tras `commit`; FastAPI serializa dentro del alcance de la dependencia `get_db`, así que la sesión sigue abierta y el acceso a `productos` recarga desde la BD. En POST la colección nunca se cargó; en PUT tampoco (el servicio no la toca) y, si se hubiera cargado, el commit la expira. `passive_deletes=True` solo afecta al borrado (no carga hijos) y no interviene en la lectura | **Sin código adicional**. Se fija con pruebas HTTP de POST y PUT. Riesgo documentado: cambiar `expire_on_commit=False` exigiría `sesion.refresh` |
| 6 | Esquema de BD | — | La propiedad no es columna | Sin migración; `app.db` no se recrea |

## Interfaces / contratos

```python
# Backend/src/secciones/models.py
@property
def productos_ids(self):
    """Ids de los productos activos de la sección, ascendentes (para from_attributes)."""
    return sorted(p.id for p in self.productos if not p.dado_de_baja)
```

## Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `Backend/src/secciones/models.py` | Modificar | Propiedad `productos_ids` |
| `Backend/src/secciones/schemas.py` | Modificar | `productos_ids: list[int]` |
| `Backend/tests/secciones/test_router.py` | Modificar | SEC-02 se reescribe (la respuesta incluye `productos_ids` con el plato); igualdades exactas agregan `productos_ids: []` (SEC-25, POS-01 y toda otra comparación `== {...}` de una sección); pruebas nuevas |
| `Backend/tests/secciones/test_schemas.py` | Modificar | Conjunto de campos con `productos_ids`; `SimpleNamespace` con `productos_ids=[...]` |
| `Backend/tests/secciones/test_modelos.py` | Modificar | Pruebas unitarias de la propiedad |
| `Backend/tests/secciones/test_excepciones.py` | Modificar | Hoy solo verifica `exceptions`; se agrega la verificación de importaciones de `models`, `schemas`, `services` y `router` |

## Estrategia de pruebas

TDD estricto: cada prueba se escribe en rojo antes del código.

| Capa | Qué prueba |
|---|---|
| Unidad (modelo) | Sección sin productos → `[]`; activos e inactivos mezclados → solo activos; ids insertados en desorden → ascendentes; los cinco subtipos cuentan; combo vencido activo cuenta |
| Unidad (esquema) | `productos_ids` en `model_fields`; `model_validate` desde atributos lo copia |
| Unidad (costo) | Con `before_cursor_execute`: leer `productos_ids` emite un único `SELECT` y no consulta tablas de subtipos |
| HTTP | POST → `productos_ids == []`; GET con activos e inactivos de los cinco subtipos; DELETE de producto lo quita; PUT de producto con `dado_de_baja: false` lo reincorpora; mover un producto de sección (PUT con otro `seccion_id`) lo quita de una y lo agrega a la otra; quitarle la sección (`null`) lo quita; orden ascendente; frescura: PUT de sección con productos ya asignados devuelve los ids vigentes e igual al GET siguiente; POST/PUT rechazados no alteran el GET |
| Importaciones | `src.secciones.models`, `schemas`, `services` y `router` no importan `src.productos` |

## Matriz de amenazas

N/A — sin enrutamiento de shell, subprocesos, automatización VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

Sin migraciones ni recreación de `Backend/app.db`. Las pruebas usan SQLite en memoria.

## Preguntas abiertas

- [x] ¿Se confirman los valores por defecto derivados de la propuesta (orden ascendente, `[]` para una sección nueva y combo vencido pero activo incluido)? El diseño los asume; no bloquean la implementación. Resuelta: aprobada por el usuario.
