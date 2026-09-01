# Tasks 006 — Baja de Producto

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Esquema: estado del producto y relajación del SKU

- [x] **T01 — Agregar `status` a `Product`**
  Crear `ProductStatus` (enum `Activo`/`Inactivo`) en `models.py`, agregar
  la columna `status` a `Product`, agregar `core_producto.initial_status()`
  y actualizar `repository_producto.create_product` para asignarlo
  explícitamente al crear.
  [Cubre RF-4]
  Hecho cuando: `pytest -q -k initial_status` pasa, y un test de
  integración confirma que un producto recién creado tiene
  `status == ProductStatus.ACTIVE`.

- [x] **T02 — Quitar `unique=True` de `sku`**
  Actualizar `models.py`; actualizar `test_database.py` (el test que hoy
  espera `IntegrityError` ante un SKU duplicado deja de aplicar; agregar
  uno que confirme que ya no es único a nivel de base).
  [Cubre RF-10]
  Hecho cuando: `pytest -q tests/backend/test_database.py` pasa con el
  test nuevo y sin el viejo.

## Fase 1 — Backend: repositorio

- [x] **T03 — `sku_exists` compara solo contra Activos**
  Modificar la función existente para filtrar `status == ACTIVE`, con
  tests de integración.
  [Cubre RF-10]
  Hecho cuando: `pytest -q -k sku_exists` pasa, cubriendo un SKU cuyo
  único dueño está Inactivo (`False`) y un SKU con un dueño Activo
  (`True`), aunque también exista un Inactivo con el mismo SKU.

- [x] **T04 — `find_by_sku` prioriza el producto Activo**
  Implementar la búsqueda de solo lectura por SKU (insensible a
  mayúsculas), con test de integración cubriendo un SKU compartido entre
  un Activo y un Inactivo.
  [Cubre RF-1, RF-10]
  Hecho cuando: `pytest -q -k find_by_sku` pasa.

- [x] **T05 — `deactivate_by_sku`**
  Implementar el cambio de estado a Inactivo sin re-verificar el estado
  previo, sin tocar `unit_price`/`stock`, con tests de integración.
  [Cubre RF-4, RF-6, RF-7, RF-8]
  Hecho cuando: `pytest -q -k deactivate_by_sku` pasa, cubriendo
  Activo→Inactivo persistido con `stock` intacto, SKU inexistente
  (`None`) y un producto ya Inactivo (no lanza error).

## Fase 2 — Backend: endpoints

- [x] **T06 — Endpoint `GET /productos/{sku}` (búsqueda)**
  Implementar la ruta usando `find_by_sku`, con tests de integración.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k buscar_producto_endpoint` pasa, cubriendo
  producto Activo, Inactivo y SKU inexistente (404).

- [x] **T07 — Endpoint `PATCH /productos/{sku}/baja`**
  Implementar la ruta usando `deactivate_by_sku`, con tests de
  integración.
  [Cubre RF-4, RF-6, RF-7, RF-8, RF-9, RF-10]
  Hecho cuando: `pytest -q -k baja_producto_endpoint` pasa, cubriendo baja
  exitosa (con stock alto, sin modificarlo), SKU inexistente (404),
  invocación directa sobre uno ya Inactivo (200 idempotente), y que un
  alta nueva con ese SKU (ahora Inactivo) se acepte mientras que con el
  SKU de un producto Activo se siga rechazando.

## Fase 3 — Frontend: módulo puro y API

- [x] **T08 — `productoBaja.js`**
  Implementar el módulo puro que interpreta el resultado de la búsqueda
  (no encontrado / ya inactivo / requiere confirmación), con tests
  unitarios sin React.
  [Cubre RF-2, RF-3, RF-6]
  Hecho cuando: `npm run test -- productoBaja` pasa, cubriendo los tres
  estados.

- [x] **T09 — `buscarProducto` y `darDeBajaProducto` en `productosApi.js`**
  Implementar ambas funciones, con tests con `fetch` mockeado.
  [Cubre RF-1, RF-2, RF-4]
  Hecho cuando: `npm run test -- productosApi` pasa, cubriendo respuestas
  de éxito y de error (404) para ambas.

## Fase 4 — Frontend: componente

- [x] **T10 — Esqueleto de `ProductoBajaForm.jsx`: búsqueda y "no encontrado"**
  Input de SKU + botón de búsqueda, llamada a `buscarProducto`, mensaje de
  "no encontrado" usando `productoBaja.js`.
  [Cubre RF-1, RF-2]
  Hecho cuando: un test de RTL con `buscarProducto` mockeado devolviendo
  "no encontrado" muestra el mensaje y no renderiza botón de confirmación.

- [x] **T11 — Render de "producto ya inactivo"**
  Mostrar el mensaje correspondiente cuando el producto encontrado ya
  está Inactivo, sin botón de confirmación.
  [Cubre RF-6]
  Hecho cuando: un test de RTL con un producto Inactivo mockeado muestra
  el mensaje y `darDeBajaProducto` no se invoca.

- [x] **T12 — Diálogo de confirmación para producto Activo**
  Mostrar los datos del producto y los botones Confirmar/Cancelar cuando
  el producto encontrado está Activo.
  [Cubre RF-3]
  Hecho cuando: un test de RTL con un producto Activo mockeado muestra sus
  datos junto a ambos botones.

- [x] **T13 — Confirmar baja**
  Conectar "Confirmar" a `darDeBajaProducto`, mostrar "Producto dado de
  baja exitosamente" al recibir éxito.
  [Cubre RF-4]
  Hecho cuando: un test de RTL confirma la invocación y el mensaje.

- [x] **T14 — Cancelar confirmación**
  Conectar "Cancelar" para cerrar el diálogo sin invocar ninguna API.
  [Cubre RF-5]
  Hecho cuando: un test de RTL confirma que `darDeBajaProducto` NO fue
  invocada tras cancelar.

## Fase 5 — Integración de navegación

- [x] **T15 — Pestaña "Baja de Producto" en `App.jsx`**
  Agregar la sexta pestaña junto a las cinco existentes.
  [Soporte - sin RF directo]
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar hacia la nueva pestaña.

## Fase 6 — Verificación final

- [x] **T16 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-10 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-10]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada RF de la spec tiene un test
  correspondiente pasando.
