# Tasks 011 — Modificación de Venta

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Modelo de datos

- [x] **T01 — `SaleStatus.DRAFT`**
  Agregar el valor `DRAFT = "Borrador"` al enum `SaleStatus` en
  `models.py`.
  [Cubre RF-1]
  Hecho cuando: un test confirma que se puede persistir una `Sale` con
  `status=SaleStatus.DRAFT` sin errores.

## Fase 1 — Backend: repositorio (`repository_venta.py`)

- [x] **T02 — `create_sale` deja de confirmar y descontar stock**
  Modificar `create_sale` para que la venta se cree con
  `status=SaleStatus.DRAFT` y sin restar `product.stock` de ningún
  ítem.
  [Cubre RF-1]
  Hecho cuando: `pytest -q -k create_sale` pasa, confirmando que la
  venta creada queda en "Borrador" y que el stock de cada producto del
  detalle es igual antes y después de crearla.

- [x] **T03 — Actualizar tests existentes de alta de venta ([[009-alta-venta]])**
  Ajustar los tests de `test_main.py`/`test_database.py` que asumían
  que registrar una venta la deja "Confirmada" y descuenta stock de
  inmediato, para que reflejen el nuevo comportamiento (Borrador, sin
  descuento).
  [Soporte - sin RF directo]
  Hecho cuando: `pytest -q` no tiene tests en rojo relacionados al alta
  de venta.

- [x] **T04 — `replace_sale_items`: camino feliz**
  Implementar la función que re-consulta el estado de la venta, y si
  sigue "Borrador", reemplaza sus `SaleItem` por la nueva lista y
  recalcula `Sale.total`, devolviendo `(sale, None)`.
  [Cubre RF-5, RF-10, RF-15]
  Hecho cuando: `pytest -q -k replace_sale_items_exitoso` pasa,
  cubriendo agregar, quitar y ajustar cantidades de ítems, verificando
  que el total se recalcula correctamente.

- [x] **T05 — `replace_sale_items`: venta inexistente**
  [Cubre RF-3]
  Hecho cuando: `pytest -q -k replace_sale_items_inexistente` pasa,
  devolviendo `(None, "NOT_FOUND")` para un `sale_id` que no existe.

- [x] **T06 — `replace_sale_items`: venta no está en "Borrador"**
  [Cubre RF-4]
  Hecho cuando: `pytest -q -k replace_sale_items_no_borrador` pasa,
  devolviendo `(sale, "NOT_DRAFT")` sobre una venta "Confirmada" o
  "Anulada", sin modificar su detalle.

- [x] **T07 — `replace_sale_items`: admite lista vacía**
  [Cubre RF-11]
  Hecho cuando: un test confirma que reemplazar el detalle por una
  lista vacía deja la venta en "Borrador" sin ítems y con `total == 0`.

- [x] **T08 — `close_sale`: camino feliz**
  Implementar la función que re-consulta el estado, valida que haya al
  menos un ítem y que el stock de cada producto alcance, y solo si todo
  es válido descuenta el stock de cada ítem y cambia el estado a
  "Confirmada".
  [Cubre RF-12]
  Hecho cuando: `pytest -q -k close_sale_exitoso` pasa, verificando el
  cambio de estado y el descuento de stock de cada producto del
  detalle.

- [x] **T09 — `close_sale`: venta inexistente**
  [Cubre RF-3]
  Hecho cuando: `pytest -q -k close_sale_inexistente` pasa, devolviendo
  el código de error correspondiente sin lanzar excepciones.

- [x] **T10 — `close_sale`: venta no está en "Borrador"**
  [Cubre RF-14]
  Hecho cuando: un test que invoca `close_sale` sobre una venta ya
  "Confirmada" o "Anulada" confirma que no se modifica el stock de
  ningún producto ni se duplica el descuento.

- [x] **T11 — `close_sale`: detalle vacío**
  [Cubre RF-13]
  Hecho cuando: un test sobre una venta "Borrador" sin ítems confirma
  que `close_sale` no cambia su estado y devuelve el código de error de
  detalle vacío.

- [x] **T12 — `close_sale`: stock insuficiente en algún ítem (todo o nada)**
  [Cubre RF-16]
  Hecho cuando: un test con una venta de dos ítems, donde el stock de
  uno de los productos bajó por debajo de la cantidad requerida,
  confirma que la venta permanece en "Borrador" y que el stock de
  **ambos** productos (incluido el que sí alcanzaba) queda igual que
  antes de intentar el cierre.

- [x] **T13 — `cancel_sale`: no opera sobre ventas en "Borrador"**
  Modificar `cancel_sale` para que solo reponga stock y cambie a
  "Anulada" si la venta está "Confirmada"; si está en "Borrador",
  devuelve un nuevo código de error sin tocar stock ni estado.
  [Corrige interacción con [[010-anular-venta]]]
  Hecho cuando: `pytest -q -k cancel_sale_borrador` pasa, confirmando
  que el stock de los productos del detalle no cambia y que la venta
  sigue en "Borrador" tras el intento.

## Fase 2 — Backend: endpoints (`routes/ventas.py`)

- [x] **T14 — Endpoint `PUT /ventas/{sale_id}/detalle`: camino feliz**
  Implementar la ruta: valida producto activo, stock y cantidad
  positiva por ítem, y llama a `replace_sale_items`.
  [Cubre RF-5, RF-10]
  Hecho cuando: `pytest -q -k reemplazar_detalle_exitoso` pasa,
  verificando 200, el nuevo detalle y el total recalculado.

- [x] **T15 — Endpoint: venta inexistente (404)**
  [Cubre RF-3]
  Hecho cuando: un test con un `sale_id` inexistente devuelve 404 con
  "Venta no encontrada".

- [x] **T16 — Endpoint: venta no editable (422)**
  [Cubre RF-4]
  Hecho cuando: un test sobre una venta "Confirmada" o "Anulada"
  devuelve 422 con "La venta ya no admite modificaciones" y no
  modifica el detalle.

- [x] **T17 — Endpoint: validaciones combinadas de ítems (RF-9)**
  Validar producto inactivo, stock insuficiente y cantidad no positiva
  a nivel de ruta, reportando todos los errores del intento juntos.
  [Cubre RF-6, RF-7, RF-8, RF-9]
  Hecho cuando: `pytest -q -k reemplazar_detalle_validaciones` pasa,
  enviando un payload con los tres problemas a la vez y verificando que
  la respuesta 422 incluye las tres advertencias y que el detalle
  anterior no cambió.

- [x] **T18 — Endpoint: detalle vacío permitido**
  [Cubre RF-11]
  Hecho cuando: un test que envía `items: []` a una venta "Borrador"
  devuelve 200 con el detalle vacío y `total == 0`.

- [x] **T19 — Endpoint `PATCH /ventas/{sale_id}/cerrar`: camino feliz**
  Implementar la ruta usando `close_sale`.
  [Cubre RF-12]
  Hecho cuando: `pytest -q -k cerrar_venta_exitoso` pasa, verificando
  200, estado "Confirmada" y stock descontado de cada producto.

- [x] **T20 — Endpoint cerrar: venta inexistente, no editable y detalle vacío**
  [Cubre RF-3, RF-14, RF-13]
  Hecho cuando: tres tests confirman 404 (inexistente), 422 "La venta
  ya no se encuentra en Borrador" (no editable) y 422 "La venta debe
  tener al menos un ítem" (detalle vacío), respectivamente.

- [x] **T21 — Endpoint cerrar: stock insuficiente**
  [Cubre RF-16]
  Hecho cuando: `pytest -q -k cerrar_venta_stock_insuficiente` pasa,
  verificando 422 con "No hay stock suficiente para completar la
  operación" y que el stock de los productos involucrados no cambió.

- [x] **T22 — Endpoint `PATCH /ventas/{sale_id}/anular` sobre "Borrador"**
  [Corrige interacción con [[010-anular-venta]]]
  Hecho cuando: un test que invoca `anular` sobre una venta "Borrador"
  devuelve 422 con "No se puede anular una venta en Borrador" y el
  stock de sus productos no cambia.

## Fase 3 — Frontend: módulos puros y API

- [x] **T23 — `removeItem` en `ventaDetalle.js`**
  Función pura que quita un ítem de la lista por SKU.
  [Cubre RF-5]
  Hecho cuando: `npm run test -- ventaDetalle` pasa, cubriendo quitar
  un ítem existente y un SKU no presente en la lista.

- [x] **T24 — `ventaEdicion.js`**
  Crear el módulo puro que interpreta el resultado de la búsqueda de
  una venta para editar su detalle (`NOT_FOUND` / `NOT_DRAFT` /
  `EDITABLE`), sin depender de React.
  [Cubre RF-2, RF-3, RF-4]
  Hecho cuando: `npm run test -- ventaEdicion` pasa, cubriendo los tres
  estados.

- [x] **T25 — `reemplazarDetalleVenta` y `cerrarVenta` en `ventasApi.js`**
  Implementar ambas funciones, con tests con `fetch` mockeado.
  [Cubre RF-2, RF-5, RF-12, RF-14, RF-16]
  Hecho cuando: `npm run test -- ventasApi` pasa, cubriendo respuestas
  200, 404 y 422 para ambas funciones.

## Fase 4 — Frontend: componente

- [x] **T26 — Esqueleto de `VentaEdicionForm.jsx`: búsqueda y "no encontrada"**
  Input de ID + botón de búsqueda, llamada a `buscarVenta`, mensaje de
  "no encontrada" usando `ventaEdicion.js`.
  [Cubre RF-2, RF-3]
  Hecho cuando: un test de RTL con `buscarVenta` mockeado devolviendo
  "no encontrada" muestra el mensaje y no renderiza el editor.

- [x] **T27 — Render de "venta no editable"**
  Mostrar el mensaje correspondiente y el detalle en solo lectura
  cuando la venta encontrada no está en "Borrador".
  [Cubre RF-4]
  Hecho cuando: un test de RTL con una venta "Confirmada" mockeada
  muestra el mensaje de no editable y ningún control de edición.

- [x] **T28 — Render del detalle editable y agregar producto**
  Mostrar el detalle de una venta "Borrador" como editable, reutilizando
  el patrón de búsqueda de producto por SKU de `VentaForm.jsx`.
  [Cubre RF-5, RF-10]
  Hecho cuando: un test de RTL agrega un producto al detalle y verifica
  que la tabla y el total se actualizan.

- [x] **T29 — Quitar producto del detalle**
  Conectar el botón "Quitar" de cada fila a `removeItem`.
  [Cubre RF-5]
  Hecho cuando: un test de RTL quita un ítem y verifica que desaparece
  de la tabla y que el total se recalcula.

- [x] **T30 — Guardar cambios del detalle**
  Conectar "Guardar cambios" a `reemplazarDetalleVenta`, mostrando
  éxito o todas las advertencias del backend juntas.
  [Cubre RF-6, RF-7, RF-8, RF-9]
  Hecho cuando: un test de RTL con `reemplazarDetalleVenta` mockeado
  devolviendo múltiples errores 422 muestra todas las advertencias a la
  vez.

- [x] **T31 — Cerrar venta con confirmación (éxito)**
  Diálogo de confirmación para "Cerrar venta", conectado a
  `cerrarVenta`, mostrando el mensaje de éxito y reflejando el nuevo
  estado "Confirmada".
  [Cubre RF-12, RF-13]
  Hecho cuando: un test de RTL confirma la invocación de `cerrarVenta`
  y el mensaje de éxito.

- [x] **T32 — Manejo del rechazo al cerrar (condición de carrera)**
  Si `cerrarVenta` devuelve error (422 de stock insuficiente o estado
  inválido), mostrar ese mensaje en vez de asumir éxito.
  [Cubre RF-14, RF-16]
  Hecho cuando: un test de RTL con `cerrarVenta` mockeado devolviendo
  un error 422 de stock insuficiente muestra el mensaje de rechazo del
  backend, no un mensaje de éxito.

## Fase 5 — Integración de navegación

- [x] **T33 — Pestaña "Modificar Venta" en `App.jsx`**
  Agregar la undécima pestaña junto a las diez existentes.
  [Soporte - sin RF directo]
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar hacia la nueva pestaña.

## Fase 6 — Verificación final

- [x] **T34 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-16 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-16]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck`
  terminan sin errores ni tests saltados, y cada RF de la spec tiene un
  test correspondiente pasando.
