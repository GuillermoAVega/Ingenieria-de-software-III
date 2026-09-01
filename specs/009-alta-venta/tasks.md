# Tasks 009 — Registrar Alta de Venta

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Modelo de datos

- [x] **T01 — `SaleStatus`, `Sale`, `SaleItem`**
  Agregar a `models.py` el enum `SaleStatus` (solo `Confirmada`) y las
  tablas `sales`/`sale_items` (columnas FK planas, sin `relationship()`).
  [Cubre RF-15]
  Hecho cuando: un test confirma que `Base.metadata.create_all(engine)`
  crea `sales` y `sale_items` sin errores sobre una base SQLite temporal.

## Fase 1 — Backend: repositorio (`repository_venta.py`)

- [x] **T02 — `create_sale`: camino feliz con un ítem**
  Implementar la función que crea la venta, su ítem, calcula el total y
  descuenta el stock del producto, con test de integración.
  [Cubre RF-7, RF-13, RF-15]
  Hecho cuando: `pytest -q -k create_sale_un_item` pasa, verificando
  estado `Confirmada`, total correcto, `unit_price` del ítem persistido
  tal como se pasó, y el stock del producto descontado en la cantidad
  vendida.

- [x] **T03 — `create_sale`: varios ítems**
  Cubrir el caso de una venta con más de un ítem (distintos productos).
  [Cubre RF-13, RF-15]
  Hecho cuando: `pytest -q -k create_sale_multiples_items` pasa,
  verificando que el total sea la suma de cantidad × precio de cada
  ítem y que se descuente el stock de cada producto por separado.

- [x] **T04 — `create_sale`: no consolida duplicados**
  Confirmar (documentar) que si se pasan dos ítems con el mismo
  producto, se crean dos filas `SaleItem` y el stock se descuenta dos
  veces (la consolidación es responsabilidad del Frontend, no del
  backend — Decisión Técnica 3).
  [Cubre RF-16]
  Hecho cuando: `pytest -q -k create_sale_no_consolida` pasa.

## Fase 2 — Backend: endpoint (`routes/ventas.py`)

- [x] **T05 — Endpoint `POST /ventas`: camino feliz**
  Implementar la ruta: resuelve cliente por DNI y productos por SKU
  (reutilizando `repository.find_by_dni`/`repository_producto.find_by_sku`),
  valida cantidad con `core_producto.validate_positive_integer`, llama a
  `create_sale`, con test de integración.
  [Cubre RF-1, RF-4, RF-15]
  Hecho cuando: `pytest -q -k registrar_venta_exitosa` pasa (con uno y
  con varios ítems), devolviendo 201 con el detalle completo de la
  venta.

- [x] **T06 — Endpoint: DNI inexistente**
  [Cubre RF-2]
  Hecho cuando: un test con un DNI que no existe devuelve 422 con la
  advertencia `{"field": "dni", ...}`.

- [x] **T07 — Endpoint: SKU inexistente en un ítem**
  [Cubre RF-5]
  Hecho cuando: un test con un SKU inexistente en el detalle devuelve
  422 con `{"field": "items[0].sku", ...}`.

- [x] **T08 — Endpoint: cantidad inválida por ítem**
  [Cubre RF-8]
  Hecho cuando: tests parametrizados con cantidad `"0"`, `"-1"`, `"5.5"`
  y `"abc"` devuelven 422 con `{"field": "items[0].quantity", ...}`.

- [x] **T09 — Endpoint: detalle vacío**
  [Cubre RF-11]
  Hecho cuando: un test con `"items": []` devuelve 422 con la
  advertencia sobre `items`.

- [x] **T10 — Endpoint: reporte combinado de múltiples errores**
  [Cubre RF-12]
  Hecho cuando: un test con DNI inexistente y un SKU inexistente en otro
  ítem a la vez devuelve ambas advertencias juntas en un mismo 422.

- [x] **T11 — Endpoint: ausencia de re-verificación al confirmar**
  Confirmar que enviar el DNI de un cliente Inactivo, el SKU de un
  producto Inactivo, o una cantidad mayor al stock disponible,
  directamente a `POST /ventas`, registra la venta igual (sin bloquear),
  documentando el riesgo aceptado de RF-16.
  [Cubre RF-16]
  Hecho cuando: tres tests de integración confirman que la venta se
  registra (201) en cada uno de los tres casos.

- [x] **T12 — Registrar el router de ventas en `main.py`**
  [Soporte - sin RF directo]
  Hecho cuando: `pytest -q -k test_main` confirma que `POST /ventas`
  aparece entre las rutas expuestas por la app.

## Fase 3 — Frontend: módulo puro y API

- [x] **T13 — `ventaDetalle.addItem`**
  Crear `ventaDetalle.js` con la función que agrega un ítem nuevo,
  consolida por SKU repetido (RF-10), valida cantidad entera positiva
  (RF-8) y valida contra el stock disponible (RF-9), con tests
  unitarios sin React.
  [Cubre RF-8, RF-9, RF-10]
  Hecho cuando: `npm run test -- ventaDetalle` pasa, cubriendo ítem
  nuevo válido, consolidación de SKU repetido, cantidad inválida y
  cantidad (ya consolidada) que supera el stock.

- [x] **T14 — `ventaDetalle.computeTotal`**
  Agregar la función que calcula el total como la suma de cantidad ×
  precio unitario de todos los ítems, con test unitario.
  [Cubre RF-13]
  Hecho cuando: `npm run test -- ventaDetalle` sigue en verde, cubriendo
  además `computeTotal` con varios ítems.

- [x] **T15 — `registrarVenta` en `ventasApi.js`**
  Implementar la función que llama a `POST /ventas`, con tests con
  `fetch` mockeado.
  [Cubre RF-15]
  Hecho cuando: `npm run test -- ventasApi` pasa, cubriendo una
  respuesta 201 y una 422.

## Fase 4 — Frontend: componente

- [x] **T16 — Esqueleto de `VentaForm.jsx`: búsqueda de cliente**
  Input de DNI + búsqueda (reutiliza `buscarCliente`); mensajes de "no
  encontrado" (RF-2) y "no se pueden emitir ventas a clientes dados de
  baja" (RF-3); solo con un cliente Activo se habilita continuar.
  [Cubre RF-1, RF-2, RF-3]
  Hecho cuando: un test de RTL confirma los tres casos (no encontrado,
  Inactivo, Activo habilita continuar).

- [x] **T17 — Agregar ítems al detalle**
  Input de SKU + cantidad + botón "Agregar" (reutiliza `buscarProducto`
  y `ventaDetalle.addItem`); mensajes de "no encontrado" (RF-5), "no
  está disponible para la venta" (RF-6), cantidad inválida (RF-8) y
  stock insuficiente (RF-9).
  [Cubre RF-4, RF-5, RF-6, RF-8, RF-9, RF-10]
  Hecho cuando: un test de RTL confirma cada mensaje por separado, y que
  agregar el mismo SKU dos veces consolida la línea en vez de duplicarla.

- [x] **T18 — Tabla del detalle y total**
  Renderizar la tabla de ítems agregados (SKU, Nombre, Cantidad, Precio
  unitario, Subtotal) con el Total al pie.
  [Cubre RF-13]
  Hecho cuando: un test de RTL confirma que el Total mostrado coincide
  con `ventaDetalle.computeTotal` sobre los ítems agregados.

- [x] **T19 — Confirmación y registro exitoso**
  Botón "Registrar venta" → diálogo de confirmación (RF-14); Confirmar
  llama a `registrarVenta`, muestra el mensaje de éxito y reinicia el
  formulario a su estado inicial.
  [Cubre RF-14, RF-15]
  Hecho cuando: un test de RTL confirma la aparición del diálogo, y otro
  confirma que "Confirmar" invoca `registrarVenta` y muestra el mensaje
  de éxito.

- [x] **T20 — Cancelar confirmación**
  Conectar "Cancelar" para cerrar el diálogo sin invocar `registrarVenta`
  y sin perder el detalle armado.
  [Cubre RF-17]
  Hecho cuando: un test de RTL confirma que `registrarVenta` NO fue
  invocada tras cancelar y que el detalle sigue visible.

## Fase 5 — Integración de navegación

- [x] **T21 — Pestaña "Registrar Venta" en `App.jsx`**
  Agregar la novena pestaña junto a las ocho existentes.
  [Soporte - sin RF directo]
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar hacia la nueva pestaña.

## Fase 6 — Verificación final

- [x] **T22 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-17 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-17]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada RF de la spec tiene un test
  correspondiente pasando.
