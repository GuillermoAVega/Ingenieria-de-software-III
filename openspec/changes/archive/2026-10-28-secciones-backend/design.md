# Diseño: Secciones Backend

## Enfoque técnico

Nuevo módulo `Backend/src/secciones/` con los seis archivos de la convención (rules.design: lo compartido queda en `Backend/src/`) y las mismas capas que `productos`: `router.py` (delgado) → `services.py` (sin FastAPI) → `models.py` (SQLAlchemy 2 sobre `ModeloBase`). La FK `producto.seccion_id` delega en SQLite (`PRAGMA foreign_keys=ON`, ya activo en `configurar_sqlite`) la desvinculación al borrar. En `productos` se agrega `seccion_id` a los esquemas comunes y una validación compartida en `productos/services.py`. Implementa `specs/section-management` y el delta de `specs/product-catalog`.

```
HTTP ─→ secciones/router ─(Pydantic 422)─→ secciones/services ─→ Seccion ─→ SQLite
                ▲                                │ ErrorSeccion / IntegrityError→409
                └─ secciones/router.MANEJADORES_EXCEPCIONES (registrados en main.py)
productos/<sub>/services ─→ productos/services.verificar_seccion ─→ Seccion (422 SeccionInexistente)
```

## Decisiones de arquitectura

| # | Tema | Opciones | Compromiso | Decisión |
|---|------|----------|------------|----------|
| 1 | Dirección de dependencias | (a) `secciones` importa `productos`; (b) `productos` importa `secciones`; (c) ninguno | (a) obligaría a `secciones` a conocer la jerarquía de productos. (c) impide validar `seccion_id` | **(b)**. `productos` es el dueño de la FK y de la validación referencial; `secciones` no importa nada de `productos` (las referencias inversas van por cadena). Grafo acíclico |
| 2 | `normalizar_nombre` compartido | (a) `secciones` importa `productos.services`; (b) duplicar; (c) mover a `src/texto.py` | (a) viola la decisión 1. (b) dos reglas de unicidad que pueden divergir | **(c)**. `Backend/src/texto.py` define `normalizar_nombre` (`strip().casefold()`); `productos/services.py` la importa desde ahí (sigue disponible como `services.normalizar_nombre`, sin romper pruebas). El validador de recorte de Pydantic (3 líneas) se repite en `secciones/schemas.py`, aplicado a `nombre` y a `subtitulo` (este último con vacío → `None`) |
| 3 | Unicidad de `nombre` | (a) verificación en servicio + índice; (b) solo índice UNIQUE | (a) duplica la regla; aquí no hay filtro por estado que justifique el mensaje previo | **(b)**. Índice `ux_seccion_nombre_normalizado` UNIQUE sobre todas las filas. `secciones/services._confirmar` traduce el `IntegrityError` cuyo `orig` menciona `nombre_normalizado` a `NombreSeccionDuplicado` (409), con rollback, igual que `confirmar_cambios`. Excluir la propia fila es implícito (misma fila) |
| 4 | Borrado de una sección | (a) ORM anula hijos (`passive_deletes=False`); (b) `passive_deletes=True` + `ON DELETE SET NULL` | (a) carga todos los productos (consulta polimórfica con JOIN) y emite un UPDATE por fila; funciona sin FK activas, pero duplica la regla. (b) depende del `PRAGMA`, que `configurar_sqlite` garantiza en el engine real y en el de pruebas | **(b)**. Un solo DELETE; la BD es la fuente de verdad. Sin cascada `delete`: los productos nunca se borran. Los objetos ya cargados se refrescan por `expire_on_commit` |
| 5 | Excepciones | (a) reutilizar `productos.ErrorDominio`; (b) jerarquía propia en `secciones/exceptions.py` | (a) viola la decisión 1 | **(b)**. `ErrorSeccion` → `SeccionNoEncontrada` (404), `NombreSeccionDuplicado` (409). Jerarquías disjuntas: el manejador de `ErrorConflicto` de productos no las captura |
| 6 | Sección inexistente en un producto | (a) reutilizar `ComponenteInvalido`; (b) `SeccionInexistente` en `secciones/exceptions.py`; (c) `SeccionInexistente(ErrorDominio)` en `productos/exceptions.py` | (a) `type` engañoso. (b) quedaría fuera del `except ErrorDominio` de los servicios de productos | **(c)**. Es un error referencial del catálogo. Se mapea en `productos/router.MANEJADORES_EXCEPCIONES` (sin cambio extra en `main.py`) |
| 7 | Carga de mappers | (a) `secciones/__init__` carga modelos; (b) `productos/registro.py` importa `src.secciones.models` | (b) respeta la decisión 1 y reutiliza el punto único ya importado por `main.py` y `conftest.py` | **(b)**. `registro.py` agrega `from src.secciones.models import Seccion`; así `configure_mappers` resuelve `"Seccion"` y `"Producto"` |
| 8 | Base de datos existente | (a) migración (Alembic); (b) `ALTER TABLE` manual; (c) recrear `app.db` | (a)/(b) fuera de alcance | **(c)**. `create_all` no agrega columnas: se borra `Backend/app.db` (no versionado) y se recrea al iniciar |

### Contrato de errores (nuevo)

| Excepción | Ubicación | HTTP | Cuerpo |
|---|---|---|---|
| `SeccionInexistente(seccion_id)` | `productos/exceptions.py` | 422 | `{"detail": [{"loc": ["body","seccion_id"], "msg": msg, "type": "seccion_inexistente", "ids": [id]}]}` (forma del 422 de Pydantic, vía `_error_de_campo`) |
| `SeccionNoEncontrada` | `secciones/exceptions.py` | 404 | `{"detail": msg}` |
| `NombreSeccionDuplicado` | `secciones/exceptions.py` | 409 | `{"detail": msg}` |

## Modelo de datos

| Tabla | Columnas | Restricciones |
|---|---|---|
| `seccion` | `id` PK, `nombre` String(100) NOT NULL, `nombre_normalizado` String(100) NOT NULL, `subtitulo` String(200) NULL | `ux_seccion_nombre_normalizado` UNIQUE |
| `producto` (modificada) | + `seccion_id` Integer NULL | FK → `seccion.id` `ON DELETE SET NULL`, índice simple |

```python
# productos/models.py (Producto, raíz abstracta; lo heredan los cinco subtipos)
seccion_id = mapped_column(ForeignKey("seccion.id", ondelete="SET NULL"), nullable=True, index=True)
seccion = relationship("Seccion", back_populates="productos")
# secciones/models.py (sin importar productos)
productos = relationship("Producto", back_populates="seccion", passive_deletes=True)
```

## Integración en productos

- `ProductoBase.seccion_id: int | None = None`; `ProductoRespuestaBase.seccion_id: int | None`. Tipo inválido → 422 de Pydantic.
- `services.verificar_seccion(sesion, seccion_id)`: `None` no hace nada; `sesion.get(Seccion, id) is None` → `SeccionInexistente`.
- `asignar_campos_comunes` copia `seccion_id` (reemplazo completo: omitido → `null`).
- `crear_producto`: `verificar_seccion` → nombre; captura `ErrorDominio` (no solo `NombreDuplicado`) para el rollback. `actualizar_producto`: `obtener` (404) → `verificar_seccion` → nombre → estado. Cubre platos, bebidas y postres sin cambios en sus servicios.
- `combos._sin_otros_cambios` agrega `datos.seccion_id == combo.seccion_id`.

### Orden de validación (verificado contra el código)

Prioridad: 422 esquema → 404 → 409 combo vencido → 422 referencias (componentes, luego `seccion_id`) → 409 componentes inactivos → 409 nombre.

Hoy `resolver_componentes_*` valida existencia y actividad juntas; para intercalar `seccion_id`, menús y combos llaman `resolver_componentes_*(…, exigir_activos=False)`, luego `services.verificar_seccion`, luego `verificar_componentes_activos(...)` si el compuesto queda activo (en el alta, siempre).

| Subtipo | Flujo |
|---|---|
| Plato/Bebida/Postre | carga (PUT) → sección → nombre → estado |
| MenuEjecutivo | carga (PUT) → existencia de componentes → sección → actividad → (compartido: sección de nuevo, nombre, estado). `actualizar_menu`/`crear_menu` capturan `ErrorDominio` |
| ComboPromocion | alta: `FechaHastaVencida` → existencia → sección → actividad → nombre. PUT: carga → vencido (409 o baja sin cambios, incluido `seccion_id`) → existencia → sección → actividad → compartido |

La segunda llamada en `actualizar_producto`/`crear_producto` es redundante para los compuestos pero garantiza la regla para todo subtipo (costo: un `get` contra el mapa de identidad).

## Secciones: servicios y router

`services.py`: `obtener_seccion` (404), `crear_seccion`, `actualizar_seccion` (reemplazo completo; recalcula `nombre_normalizado`), `eliminar_seccion` (`obtener` → `sesion.delete` → commit; repetir → 404). Rollback en todo error. `router.py`: `APIRouter(prefix="/secciones")`, `POST ""` 201, `GET/PUT/DELETE "/{seccion_id:int}"` (DELETE 204), `MANEJADORES_EXCEPCIONES` (`SeccionNoEncontrada`, `NombreSeccionDuplicado`). `GET /secciones` responde 405 de forma nativa porque `POST ""` existe. `constants.py`: `NOMBRE_MAX=100`, `SUBTITULO_MAX=200`, `PREFIJO`. `SeccionActualizar = SeccionCrear`. `nombre` y `subtitulo` se recortan en un `field_validator(mode="before")`; el `subtitulo` vacío o solo de espacios tras el recorte se convierte en `None` (se almacena `null`) y el máximo de 200 se verifica sobre el valor ya recortado (el validador corre antes que `max_length`); `SeccionRespuesta`: `id`, `nombre`, `subtitulo`.

## Grafo de importaciones

`main.py` → `secciones.router`, `productos.router` → `productos.<sub>.services` → `productos.services` → `productos.registro` → `secciones.models` → `secciones.constants`, `src.models`. `productos.services` también importa `src.texto`; `secciones.services` importa `src.texto`. Ningún módulo de `secciones` importa `productos`. `main.py` registra `secciones.router.router` y recorre ambos diccionarios de manejadores.

## Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `Backend/src/texto.py` | Crear | `normalizar_nombre` |
| `Backend/src/secciones/{__init__,models,schemas,exceptions,constants,services,router}.py` | Crear | Módulo de la entidad |
| `Backend/src/productos/{models,schemas,exceptions,services,registro,router}.py` | Modificar | FK, relación, campo, validación, excepción y manejador, carga de `Seccion` |
| `Backend/src/productos/menus_ejecutivos/services.py`, `combos/services.py` | Modificar | Orden de validación, `_sin_otros_cambios` |
| `Backend/src/main.py` | Modificar | Router y manejadores de secciones |
| `Backend/tests/conftest.py` | Modificar | Recibe `persistir` (movido desde `tests/productos/conftest.py`) y la fábrica `crear_seccion` |
| `Backend/tests/secciones/**`, `Backend/tests/productos/**` | Crear/Modificar | Pruebas |

## Estrategia de pruebas

TDD estricto con los fixtures existentes (`motor`, `sesion`, `cliente`, `HOY`, fábricas). `tests/secciones/__init__.py` obligatorio.

| Capa | Archivo | Qué prueba |
|---|---|---|
| Unidad | `tests/test_texto.py`; `secciones/test_modelos.py`, `test_schemas.py`, `test_constantes.py` | Normalización; índice único (IntegrityError), `configure_mappers()` con la relación bidireccional; recorte de `nombre` y `subtitulo`, `subtitulo` vacío → `None`, límites tras el recorte |
| Integración (servicio) | `secciones/test_servicios.py` | Alta, 404, duplicado en alta y modificación traducido a 409, propio nombre y cambio de mayúsculas |
| Integración (BD) | `productos/test_seccion_producto.py` | `PRAGMA foreign_keys` = 1; `DELETE FROM seccion` crudo deja `seccion_id` NULL y las filas de producto intactas (cinco subtipos, vencido, dado de baja); solo la sección borrada se desvincula; el borrado vía servicio no carga `Seccion.productos` |
| Integración (HTTP) | `secciones/test_router.py`; `productos/<sub>/test_router.py`, `test_manejadores.py` | SEC-01..44; CAT-S-01..28 incluidas las prioridades y los combos vencidos; cuerpo del 422 `seccion_inexistente` |

## Matriz de amenazas

N/A — sin enrutamiento de shell, subprocesos, automatización VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

Sin migraciones. Borrar `Backend/app.db` antes de iniciar; `create_all` crea `seccion` y `producto` con la columna nueva. Las pruebas usan SQLite en memoria y no se ven afectadas.

## Riesgos

- Importar `secciones.models` sin `productos.registro` deja `"Producto"` sin resolver en `configure_mappers`. Mitigación: `main.py` y `conftest.py` importan `registro`.
- Si el `PRAGMA` dejara de aplicarse, el borrado fallaría silenciosamente (FK colgante). Mitigación: prueba explícita del `PRAGMA` y de la anulación.
- El mensaje de `IntegrityError` de SQLite (`UNIQUE constraint failed: seccion.nombre_normalizado`) es la base de la traducción.

## Preguntas abiertas

- [ ] Ninguna bloqueante.
