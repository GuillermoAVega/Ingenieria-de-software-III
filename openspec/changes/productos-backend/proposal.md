# Propuesta: Productos Backend

## Intención

El sistema del restaurante no tiene un catálogo de productos. Se agrega la jerarquía `Producto` (Plato, Bebida, Postre, MenuEjecutivo, ComboPromocion) con CRUD, baja lógica y reglas de integridad referencial, de modo que las funcionalidades posteriores (Seccion, pedidos) cuenten con un catálogo confiable.

## Alcance

### Dentro del alcance
- `Backend/src/productos/` siguiendo la convención de una carpeta por entidad (models, schemas, exceptions, constants, services, router). Por tratarse de una jerarquía, cada subtipo concreto tiene su propio subpaquete anidado con los mismos seis archivos (`productos/platos/`, `productos/bebidas/`, `productos/postres/`, `productos/menus_ejecutivos/`, `productos/combos/`); `productos/` conserva el `Producto` abstracto y la lógica compartida.
- `Producto` abstracto con herencia de tablas unidas (joined-table inheritance), discriminador `tipo`; tablas de subtipos más `combo_plato`, `combo_bebida`, `combo_postre`.
- `relationship()` bidireccional con `back_populates` en todos los vínculos.
- `GET /productos`, `GET /productos/{id}` (polimórficos, solo lectura); CRUD completo para `platos`, `bebidas`, `postres`, `menus-ejecutivos`, `combos`.
- Los listados ocultan los productos inactivos; `?incluir_bajas=true` los incluye.
- DELETE lógico con 409 RESTRICT (lista los ids compuestos que bloquean) cuando el producto está en un menú activo o en un combo activo no vencido (`fecha_hasta >= today`).
- Validación de componentes (existe, tipo correcto, activo) al crear, actualizar y reactivar menús/combos; verificación y escritura en una sola transacción.
- Validaciones de campos confirmadas (nombre 1-100, único entre activos; precio > 0 `Numeric(10,2)`; etc.).
- Registrar el router en `Backend/src/main.py`.
- Prerrequisito: agregar `pytest` y una configuración de pruebas (`TestClient` de FastAPI, httpx presente); definir un comando de pruebas para el Backend.

### Fuera del alcance
- Entidad Seccion, Frontend, carga binaria de imágenes, borrado físico, autenticación.

## Capacidades

### Capacidades nuevas
- `product-catalog`: jerarquía Producto, lecturas polimórficas, CRUD por subtipo, validaciones de campos.
- `product-logical-delete`: baja, reglas RESTRICT, invariante de componentes activos, filtrado con `incluir_bajas`.

### Capacidades modificadas
- Ninguna

## Enfoque

Herencia unida de SQLAlchemy 2 sobre `ModeloBase`. `menu_ejecutivo` contiene tres FK hacia la jerarquía, por lo que su mapper define un `inherit_condition` explícito y cada relationship define `foreign_keys`. Las reglas de negocio residen en `services.py`; los routers se mantienen delgados y traducen las excepciones de dominio a códigos HTTP. Las pruebas ejercitan el comportamiento mediante `TestClient` contra una base de datos SQLite aislada.

## Decisiones resueltas

Todas las preguntas abiertas previas fueron resueltas por el usuario:

1. **Cambio de estado vía PUT**: no hay un endpoint de estado dedicado. El PUT de cada subtipo acepta `dado_de_baja`; la reactivación es un PUT con `dado_de_baja=false`. Dar de baja un componente mediante PUT aplica el mismo RESTRICT que DELETE (409 con los ids compuestos bloqueantes). Reactivar un MenuEjecutivo/ComboPromocion valida que todos los componentes existan y estén activos (de lo contrario, 409). La reactivación vuelve a verificar la unicidad de `nombre` entre los productos activos (409). La lógica se comparte en una única función de servicio.
2. **Los compuestos se dan de baja libremente**: MenuEjecutivo y ComboPromocion siempre pueden darse de baja (DELETE o PUT); no se les aplica RESTRICT.
3. **Los combos vencidos son inmutables**: cualquier PUT sobre un combo con `fecha_hasta < today` (edición o reactivación) devuelve 409. Se permite la baja lógica de un combo vencido que sigue activo, por DELETE o por PUT con `dado_de_baja = true` sin otros cambios. Crear un combo requiere `fecha_hasta >= today` (de lo contrario, 422).
4. **Los precios de los compuestos son manuales**: el `precio` de MenuEjecutivo/ComboPromocion lo proporciona el cliente y es independiente de los precios de los componentes; los cambios de precio de un componente nunca alteran los precios de los compuestos.
5. **GET por id siempre devuelve el producto**, incluidos los dados de baja (`dado_de_baja` visible), tanto en `/productos/{id}` como en `/productos/<subtype>/{id}`. `?incluir_bajas=true` se aplica solo a los listados (por defecto excluye los dados de baja). `/productos/<subtype>/{id}` con un id de otro subtipo devuelve 404.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `Backend/src/productos/` | Nuevo | Módulo de la entidad: raíz abstracta, lógica compartida y router agregador |
| `Backend/src/productos/<subtipo>/` | Nuevo | Un subpaquete por subtipo (`platos`, `bebidas`, `postres`, `menus_ejecutivos`, `combos`) con models, schemas, exceptions, constants, services y router |
| `Backend/src/main.py` | Modificado | Registro del router |
| `Backend/requirements.txt` | Modificado | Agregar pytest |
| `Backend/tests/` | Nuevo | Suite de pruebas y fixtures; `Backend/tests/productos/` replica la estructura de subpaquetes |
| `openspec/config.yaml` | Modificado | Comando de pruebas; habilitar TDD estricto; convención de subpaquetes anidados |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| `AmbiguousForeignKeysError` en `menu_ejecutivo` | Alta | `inherit_condition` / `foreign_keys` explícitos; prueba de configuración de mappers |
| Condición de carrera check-then-act al dar de baja/componer | Media | Una sola transacción; evaluar en el diseño un bloqueo más estricto de SQLite |
| La unicidad solo entre activos no se puede expresar como un UNIQUE simple | Media | Verificación en el servicio (opcionalmente un índice parcial) |
| `main.py` requiere las variables de entorno `DB_URL`/`ENV`, lo que dificulta las pruebas | Media | Los fixtures de prueba sobrescriben el entorno y `get_db` |

## Plan de reversión

Eliminar `Backend/src/productos/`, la línea del router en `main.py` y las nuevas tablas (`producto`, subtipos, tablas de asociación) del archivo SQLite. Ningún dato ni comportamiento existente depende de ellas.

## Dependencias

- `pytest` instalado y un comando de pruebas del Backend definido antes del apply con pruebas primero (`strict_tdd` actualmente en false).

## Criterios de éxito

- [ ] Todos los endpoints se comportan según la especificación, incluidas las respuestas 409 RESTRICT.
- [ ] `Producto` no puede instanciarse ni crearse directamente.
- [ ] Ningún compuesto activo referencia un componente inactivo después de cualquier operación.
- [ ] Los mappers se configuran sin errores; la suite de pytest pasa.
