# Diseño: Productos Menú del Día

## Enfoque técnico

Nuevo módulo `Backend/src/productos_menu/` con los seis archivos de la convención (rules.design) y las mismas capas que `secciones`: `router.py` (delgado) → `services.py` (sin FastAPI) → `models.py` (sobre `ModeloBase`). Las reglas de negocio se verifican con consultas previas en el orden de prioridad de la especificación, dentro de la transacción `BEGIN IMMEDIATE` que abre `configurar_sqlite`; el índice UNIQUE sobre `fecha` es la garantía final. Implementa `specs/daily-menu-management`.

```
HTTP ─→ router ─(Pydantic 422)─→ services ─→ ProductoMenu / Producto ─→ SQLite
             ▲                       │ ErrorProductoMenu (rollback previo) / IntegrityError→409
             └─ productos_menu/router.MANEJADORES_EXCEPCIONES (registrados en main.py)
```

## Decisiones de arquitectura

| # | Tema | Opciones | Compromiso | Decisión |
|---|------|----------|------------|----------|
| 1 | Dirección de dependencias | (a) `productos_menu` importa `productos`; (b) a la inversa | (b) obligaría al catálogo a conocer una entidad que no le pertenece | **(a)**. `productos_menu.services` importa `Producto` y `registro`. `productos/models.py` refiere a `"ProductoMenu"` solo por cadena; el único punto de `productos` que importa el módulo nuevo es `registro.py` (igual que con `Seccion`) |
| 2 | Carga de mappers | (a) `registro.py` importa `src.productos_menu.models`; (b) `main.py` lo importa | (b) deja a las pruebas que no importan `main` sin resolver `"ProductoMenu"` | **(a)**. `main.py` y `conftest.py` ya importan `registro` |
| 3 | Modelo | — | — | `producto_id = mapped_column(ForeignKey("producto.id"), nullable=False, index=True)`; `fecha = mapped_column(Date, nullable=False)`; `Index("ux_producto_menu_fecha", "fecha", unique=True)` en `__table_args__` (patrón de `ux_seccion_posicion`). FK e índice por cadena: el modelo no importa `productos` |
| 4 | `ondelete` de la FK | (a) por defecto (NO ACTION); (b) `CASCADE`; (c) `RESTRICT` | Los productos nunca se borran físicamente; (b) borraría historial y (c) no agrega nada | **(a)**, como eligió la propuesta. El índice simple en `producto_id` evita recorridos completos al resolver `Producto.menus_del_dia` y al verificar la FK |
| 5 | Relaciones | — | — | `ProductoMenu.producto = relationship("Producto", back_populates="menus_del_dia")`; `Producto.menus_del_dia = relationship("ProductoMenu", back_populates="producto")`. Cascada por defecto (sin `delete`). Ningún esquema de producto la expone |
| 6 | Parseo de `fecha` | (a) `date` laxo; (b) `Field(strict=True)` | (b) rechaza cadenas ISO en JSON salvo configuración extra y rompe la convención | **(a)**, igual que `ComboCrear.fecha_desde`. `"2026-02-30"` y `"no-es-una-fecha"` dan 422. `producto_id: int` laxo como `seccion_id` (`"abc"` → 422) |
| 7 | Excepciones | (a) reutilizar `productos.ErrorDominio`/`ErrorConflicto`; (b) jerarquía propia | (a) Starlette despacha por MRO: una subclase de `ErrorConflicto` caería en `productos.router.manejar_conflicto`, acoplando ambos módulos | **(b)**. `ErrorProductoMenu(Exception)` en `productos_menu/exceptions.py`, disjunta de `ErrorDominio` y `ErrorSeccion` |
| 8 | Carga del producto | (a) `productos.services.obtener`; (b) `sesion.get(Producto, id)` | (a) exige un subtipo y lanza `ProductoNoEncontrado` (404), que habría que capturar y traducir | **(b)**. La raíz polimórfica abstracta puede consultarse; devuelve la instancia del subtipo concreto (los cinco mappers están cargados por `registro`) |
| 9 | Prioridad y concurrencia | (a) verificaciones previas ordenadas + índice; (b) solo índice | (b) no distingue "dado de baja" de "fecha ocupada" | **(a)**, precedente de `secciones-posicion`. `_confirmar` traduce `IntegrityError` cuyo `orig` contiene `producto_menu.fecha` a `FechaMenuOcupada`; otro se propaga. Es respaldo ante bugs, no fuente de la prioridad |
| 10 | Rollback | — | — | Toda salida con error revierte antes de lanzar, incluido el 404 (como `obtener_seccion`) |
| 11 | Helper del 422 | (a) importar `productos.router._error_de_campo`; (b) duplicarlo | (a) depende de un nombre privado y carga todo el router de productos | **(b)**. Tres líneas en `productos_menu/router.py` |
| 12 | Fábricas de prueba | (a) mover las cinco fábricas de producto a `tests/conftest.py`; (b) redefinirlas | (b) duplica | **(a)**, precedente de `persistir`. `tests/productos/conftest.py` queda vacío o se elimina |

### Contrato de errores

| Excepción | HTTP | Cuerpo |
|---|---|---|
| `ProductoInexistente(producto_id)` | 422 | `{"detail": [{"loc": ["body","producto_id"], "msg": msg, "type": "producto_inexistente", "ids": [id]}]}` |
| `ProductoDadoDeBaja` | 409 | `{"detail": "El producto está dado de baja"}` |
| `FechaMenuOcupada` | 409 | `{"detail": "Ya existe un menú del día en esa fecha"}` |
| `ProductoMenuNoEncontrado` | 404 | `{"detail": "Menú del día no encontrado"}` |

Los mensajes distintos satisfacen PMD-18 y PMD-30.

## Interfaces / contratos

```python
# schemas.py
class ProductoMenuCrear(BaseModel): producto_id: int; fecha: date
class ProductoMenuActualizar(BaseModel): fecha: date   # extra ignorado (PMD-26)
class ProductoMenuRespuesta(BaseModel):                  # from_attributes=True
    id: int; producto_id: int; fecha: date

# services.py
def obtener_producto_menu(sesion, producto_menu_id) -> ProductoMenu          # 404
def crear_producto_menu(sesion, datos: ProductoMenuCrear) -> ProductoMenu
def actualizar_fecha_producto_menu(sesion, producto_menu_id, datos) -> ProductoMenu
def eliminar_producto_menu(sesion, producto_menu_id) -> None
```

- Alta: `get(Producto)` (`None` → 422) → `_verificar_producto_activo` (409) → `_verificar_fecha_libre(fecha)` (409) → `add` → `_confirmar`.
- PUT: `obtener` (404) → `_verificar_producto_activo(registro.producto)` (409) → `_verificar_fecha_libre(fecha, excluir_id=id)` (409) → asignar `fecha` → `_confirmar`. Verificar antes de asignar (`autoflush=False`).
- DELETE: `obtener` (404) → `sesion.delete` → `_confirmar`; no mira el producto (PMD-35).

Router: `APIRouter(prefix=PREFIJO)` con `PREFIJO = "/productos-menu"` en `constants.py`; `POST ""` 201, `PUT "/{producto_menu_id:int}"` 200, `DELETE "/{producto_menu_id:int}"` 204 (`producto_menu_id` evita sombrear `id`). `main.py` incluye el router y agrega su diccionario a la tupla de manejadores.

## Grafo de importaciones

`main.py` → `productos.registro` → `productos_menu.models` → `src.models`, `productos_menu.constants`. `productos_menu.services` → `productos.models`, `productos.registro`, `productos_menu.{models,schemas,exceptions}`. `productos_menu.models` no importa `productos`, por lo que importar `registro` primero o `productos_menu.services` primero no genera ciclos.

## Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `Backend/src/productos_menu/{__init__,models,schemas,exceptions,constants,services,router}.py` | Crear | Módulo de la entidad |
| `Backend/src/productos/models.py` | Modificar | `menus_del_dia` por cadena |
| `Backend/src/productos/registro.py` | Modificar | Importa `ProductoMenu` (y lo agrega a `__all__`); `RESTRICT_POR_TIPO` sin cambios |
| `Backend/src/main.py` | Modificar | Router y manejadores |
| `Backend/tests/conftest.py`, `tests/productos/conftest.py` | Modificar | Fábricas de producto movidas; nueva `crear_producto_menu` |
| `Backend/tests/productos_menu/**` | Crear | Pruebas (con `__init__.py`) |

## Estrategia de pruebas

TDD estricto. Fábrica `crear_producto_menu(producto, fecha=None)`: sin fecha, toma `date(2100, 1, 1) + timedelta(days=next(contador))` (contador por prueba), lejos de las fechas explícitas.

| Capa | Qué prueba |
|---|---|
| Unidad | `configure_mappers()`; relación bidireccional; índice único (`IntegrityError` directo); columnas NOT NULL; esquemas (fecha inválida, `"2026-02-30"`, `producto_id` extra ignorado); jerarquía disjunta de `ErrorDominio`; manejadores y cuerpos |
| Servicio | Las tres operaciones; doble condición (inexistente + fecha ocupada → 422; baja + fecha ocupada → `ProductoDadoDeBaja`; 404 + fecha ocupada → 404); propia fecha conservada; `sesion.in_transaction()` falso tras cada error; respaldo con `_verificar_fecha_libre` anulado por `monkeypatch` (PMD-20) y con mensaje sintético |
| HTTP | PMD-01..40: los cinco subtipos (fechas distintas); petición rechazada no cambia nada (comparar `select(id, producto_id, fecha)` antes y después, sesión cerrada durante la petición); DELETE libera la fecha y repetido da 404; baja lógica de un plato con menús → mismo código y registros intactos; respuesta de producto sin `menus_del_dia` |

## Matriz de amenazas

N/A — sin enrutamiento de shell, subprocesos, automatización VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

Sin migraciones: `create_all` crea `producto_menu`; `producto` no gana columnas. Recrear `Backend/app.db` solo por el cambio previo de `posicion`. Las pruebas usan SQLite en memoria.

## Riesgos

- Un registro histórico de un producto dado de baja no puede cambiar de fecha (consecuencia aceptada; PMD-25).
- La traducción depende del texto `UNIQUE constraint failed: producto_menu.fecha` de SQLite.
- Con la cascada por defecto, un `sesion.delete(producto)` hipotético intentaría anular `producto_id` y fallaría por NOT NULL; hoy no existe borrado físico de productos.

## Preguntas abiertas

- [x] ¿Se acepta mover las cinco fábricas de producto de `tests/productos/conftest.py` a `tests/conftest.py` (decisión 12), en lugar de duplicarlas en `tests/productos_menu/`? — Resuelta: aprobada por el usuario.
