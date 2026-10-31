```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:d1dab50b6f7f58b9c02b7a1b1d02957969946c094e8c03d8ddbad92b61d1c1ce
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 8/8
scenarios: 40/40
test_command: cd Backend && venv/bin/python -m pytest -q
test_exit_code: 0
test_output_hash: sha256:f0dd170e587ebbbb7d065d915e626db227004abf696ceccc5375e5c2faff2cf8
build_command: cd Backend && ENV=test DB_URL=sqlite:// venv/bin/python -c "import src.main"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Informe de verificación

**Cambio**: productos-menu
**Versión**: N/A (capacidad nueva `daily-menu-management`)
**Modo**: TDD estricto (`strict_tdd: true`)
**Revisión evaluada**: `0b6594e` (rama `Gonza-Guille`)

### Completitud
| Métrica | Valor |
|---------|-------|
| Tareas totales | 20 |
| Tareas completas | 20 |
| Tareas incompletas | 0 |

Las 20 tareas figuran marcadas `[x]` y coinciden con el estado del código: existen los siete archivos de `Backend/src/productos_menu/`, las pruebas de `Backend/tests/productos_menu/`, `Backend/tests/test_fabricas_producto.py`, y `Backend/tests/productos/conftest.py` fue eliminado (las cinco fábricas se definen solo en `Backend/tests/conftest.py`).

### Ejecución de build y pruebas
**Build** (importación de la aplicación con base en memoria; no se usó `ENV=dev`, `Backend/app.db` no se tocó): correcto, salida vacía, código de salida 0.

```text
cd Backend && ENV=test DB_URL=sqlite:// venv/bin/python -c "import src.main"  -> exit 0
```

**Pruebas**: 828 pasaron, 0 fallaron, 0 omitidas (1 advertencia de depreciación de `httpx` en Starlette, ajena al cambio).

```text
cd Backend && venv/bin/python -m pytest -q  -> 828 passed, 1 warning in 9.44s (exit 0)
```

**Cobertura**: no disponible (`coverage: null` en la configuración del proyecto).

### Matriz de cumplimiento de la especificación
Cada escenario tiene al menos una prueba `test_pmd_NN_*` que pasó en la ejecución anterior. Se comprobó por búsqueda que los 40 identificadores tienen prueba. Se leyeron en detalle las pruebas de alta, modificación, borrado, integración y varias de servicio: aseveran códigos de estado y cuerpos exactos (p. ej. PMD-18, PMD-23, PMD-24, PMD-30 comparan el `detail` completo; PMD-21 compara el cuerpo `{id, producto_id, fecha}`; PMD-03 compara el conjunto de claves; PMD-15, 19, 22, 23, 25..27, 31 comparan el conjunto persistido `(id, producto_id, fecha)` antes y después).

| Requisito | Escenarios | Pruebas (nivel) | Resultado |
|-----------|-----------|-----------------|-----------|
| Entidad ProductoMenu y relación | PMD-01..03 | test_modelos (BD), test_schemas, test_router_alta | COMPLIANT |
| Alta de un menú del día | PMD-04..08 | test_router_alta (H), test_servicios (S) | COMPLIANT |
| Validación del alta | PMD-09..20 | test_router_alta (H), test_schemas (E), test_servicios (S), test_manejadores | COMPLIANT |
| Modificación de la fecha | PMD-21..31 | test_router_modificacion (H), test_servicios (S), test_schemas | COMPLIANT |
| Borrado físico | PMD-32..36 | test_router_borrado (H), test_servicios (S) | COMPLIANT |
| Baja de productos con menú del día | PMD-37..38 | test_integracion_productos (H) | COMPLIANT |
| Respuestas de producto sin cambios | PMD-39 | test_integracion_productos (H), productos/test_schemas (E) | COMPLIANT |
| Varios registros por producto | PMD-40 | test_integracion_productos, test_router_alta, test_servicios, test_modelos | COMPLIANT |

**Resumen de cumplimiento**: 40/40 escenarios conformes; 8/8 requisitos.

### Correctitud (evidencia estática)
| Requisito | Estado | Notas |
|-----------|--------|-------|
| Entidad y relación | Implementado | `ProductoMenu` con `id`, `producto_id` (NOT NULL, índice), `fecha` (Date, NOT NULL); `Producto.menus_del_dia` / `ProductoMenu.producto` con `back_populates`. Respuesta con solo `id`, `producto_id`, `fecha` |
| Alta | Implementado | `POST ""` 201, fecha laxa, cinco subtipos vía `sesion.get(Producto, id)` |
| Validación del alta | Implementado | Orden: esquema 422, inexistente 422, baja 409, fecha ocupada 409; `_confirmar` traduce `IntegrityError` con `producto_menu.fecha` a 409 |
| Modificación | Implementado | `ProductoMenuActualizar` solo con `fecha` (extra ignorado); orden 404, baja 409, fecha ocupada excluyendo el propio id; verificación antes de asignar |
| Borrado | Implementado | 204 sin cuerpo, no consulta `dado_de_baja`, 404 en repetido |
| Baja de productos | Implementado | `RESTRICT_POR_TIPO` sin cambios; sin RESTRICT por menú del día; sin cascada `delete` |
| Respuestas de producto | Implementado | Ningún esquema de producto expone `menus_del_dia` |
| Varios por producto | Implementado | El índice UNIQUE es solo sobre `fecha` |

### Coherencia (diseño)
| Decisión | ¿Se siguió? | Notas |
|----------|------------|-------|
| 1 Dirección de importaciones | Sí | `productos_menu.services` importa `productos`; en `src/productos` solo `registro.py` importa `productos_menu` (más la cadena `"ProductoMenu"` en `models.py`) |
| 2 Carga de mappers vía `registro` | Sí | `registro.py` importa `ProductoMenu` y lo agrega a `__all__` |
| 3 Modelo, FK, índice UNIQUE `ux_producto_menu_fecha` | Sí | FK por cadena, `models.py` no importa `productos` (verificado por prueba AST) |
| 4 FK sin `ondelete` | Sí | Verificado por prueba con el inspector |
| 5 Relación bidireccional sin cascada | Sí | |
| 6 Parseo laxo de `fecha` y `producto_id` | Sí | `"2026-02-30"` y `"abc"` dan 422 |
| 7 Jerarquía de excepciones propia | Sí | `ErrorProductoMenu(Exception)`, disjunta de `ErrorDominio` y `ErrorSeccion` (probado); Python puro |
| 8 `sesion.get(Producto, id)` | Sí | |
| 9 Prioridad y respaldo de `IntegrityError` | Sí | Probado con `_verificar_fecha_libre` anulado (servicio y HTTP); error ajeno se propaga |
| 10 Rollback antes de lanzar, incluido el 404 | Sí | `obtener_producto_menu` y los verificadores hacen `rollback()`; pruebas con `sesion.in_transaction()` falso |
| 11 Helper `_error_de_campo` propio | Sí | Duplicado en `productos_menu/router.py` |
| 12 Fábricas en `tests/conftest.py` | Sí | |
| Contrato de errores (cuerpos y códigos) | Sí | Coinciden con la tabla del diseño |
| Router delgado, registro en `main.py` | Sí | `PREFIJO` en `constants.py`; `PUT/DELETE "/{producto_menu_id:int}"`; manejadores agregados a la tupla |

### Convenciones
Identificadores y comentarios en español; routers delgados (solo delegan en `services`); `exceptions.py` sin FastAPI (verificado por prueba AST); seis archivos de la convención presentes.

### Problemas encontrados
**CRITICAL**: Ninguno.

**WARNING**:
1. Recordatorio operativo: la tarea 6.3 se ejecutó contra una base temporal y no contra `Backend/app.db`. La base local del usuario debe recrearse (por el cambio previo de `posicion` y para crear `producto_menu`); sin ello el endpoint fallará contra ese archivo. No es un defecto del código.
2. Dependencia del texto de SQLite: `_confirmar` traduce el `IntegrityError` buscando `producto_menu.fecha` en el mensaje (riesgo ya registrado en el diseño). Un cambio de motor o de versión podría convertir la carrera en 500.
3. PMD-39 (`test_integracion_productos`) detecta la ausencia de `menus_del_dia` con una heurística de subcadena (`"menu" in clave`) más la igualdad de claves con un producto sin menú; es suficiente, pero frágil si un esquema de producto agregara legítimamente un campo con "menu" en el nombre (existe el subtipo `MenuEjecutivo`).

**SUGGESTION**:
1. Las pruebas HTTP de PMD-13 verifican el `type` del primer error pero no el cuerpo completo (el diseño define `loc`, `msg`, `ids`); el cuerpo completo sí se cubre en `test_manejadores.py`.
2. PMD-37 compara los códigos de dos bajas (204 y 204); podría añadirse una aserción explícita de que el producto sin menú y el con menú quedan con el mismo cuerpo de respuesta.
3. Un `producto_id` entero que viole la FK con SQLite sin `PRAGMA foreign_keys` no se detecta en la base; el servicio ya lo previene con `sesion.get`, por lo que no hay impacto actual.

### Veredicto
PASS WITH WARNINGS
Los 40 escenarios y 8 requisitos están implementados y probados con 828 pruebas en verde; el diseño se respeta; los avisos son operativos o de fragilidad menor, sin bloquear el archivado.

### Resolución posterior

- **WARNING 1 aceptado.** Es operativo: el usuario debe recrear su `Backend/app.db` (cambios de `posicion` y `producto_menu`). No es un defecto de código.
- **WARNING 2 aceptado.** El proyecto usa SQLite; la traducción por mensaje es la red de seguridad documentada en el diseño y, con `BEGIN IMMEDIATE`, la verificación previa cubre el caso normal.
- **WARNING 3 resuelto.** `test_pmd_39` ahora comprueba la ausencia exacta de la clave `menus_del_dia`, en lugar de buscar la subcadena `menu`. La suite pasa con 828 pruebas.
- **Veredicto final: PASS.**
