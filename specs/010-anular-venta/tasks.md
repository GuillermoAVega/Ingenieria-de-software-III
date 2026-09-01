# Tasks 010 — Anular Venta

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Modelo de datos

- [x] **T01 — `SaleStatus.CANCELLED`**
  Agregar el valor `CANCELLED = "Anulada"` al enum `SaleStatus` en
  `models.py`.
  [Cubre RF-4, RF-6]
  Hecho cuando: un test confirma que se puede persistir una `Sale` con
  `status=SaleStatus.CANCELLED` sin errores.

## Fase 1 — Backend: repositorio (`repository_venta.py`)

- [x] **T02 — `find_by_id`**
  Implementar la búsqueda de solo lectura por ID de venta, con tests de
  integración.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k find_by_id_venta` pasa, cubriendo una
  venta existente y un ID inexistente (`None`).

- [x] **T03 — `cancel_sale`: camino feliz**
  Implementar la función que re-consulta el estado actual de la venta,
  y si sigue "Confirmada", repone el stock de cada ítem y cambia su
  estado a "Anulada", devolviendo `(sale, False)`.
  [Cubre RF-4, RF-8]
  Hecho cuando: `pytest -q -k cancel_sale_exitoso` pasa, cubriendo una
  venta con varios ítems de distintos productos, verificando que el
  stock de cada uno se repone según su propia cantidad.

- [x] **T04 — `cancel_sale`: venta inexistente**
  [Cubre RF-2]
  Hecho cuando: `pytest -q -k cancel_sale_inexistente` pasa, devolviendo
  `(None, False)` para un `sale_id` que no existe.

- [x] **T05 — `cancel_sale`: venta ya anulada no duplica la reposición**
  [Cubre RF-7]
  Hecho cuando: un test que invoca `cancel_sale` dos veces seguidas
  sobre la misma venta confirma que la segunda vez devuelve
  `already_cancelled=True` y que el stock del producto es igual después
  de la segunda llamada que después de la primera (no se repuso dos
  veces).

## Fase 2 — Backend: endpoints (`routes/ventas.py`)

- [x] **T06 — Endpoint `GET /ventas/{sale_id}`**
  Implementar la ruta reutilizando `_serialize_sale`, con tests de
  integración.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k buscar_venta_endpoint` pasa, cubriendo una
  venta "Confirmada", una "Anulada" y un ID inexistente (404).

- [x] **T07 — Endpoint `PATCH /ventas/{sale_id}/anular`: camino feliz**
  Implementar la ruta usando `cancel_sale`, con test de integración.
  [Cubre RF-4]
  Hecho cuando: `pytest -q -k anular_venta_exitosa` pasa, verificando
  200, mensaje de éxito, estado "Anulada" y stock repuesto de cada
  producto del detalle.

- [x] **T08 — Endpoint: venta inexistente**
  [Cubre RF-2]
  Hecho cuando: un test con un `sale_id` inexistente devuelve 404.

- [x] **T09 — Endpoint: venta ya anulada al confirmar**
  [Cubre RF-6, RF-7]
  Hecho cuando: un test que llama al endpoint dos veces seguidas sobre
  la misma venta confirma que la primera responde 200 y la segunda 422
  con "La venta ya se encuentra anulada", y que el stock del producto
  queda igual después de la segunda llamada que después de la primera.

## Fase 3 — Frontend: módulo puro y API

- [x] **T10 — `ventaAnulacion.js`**
  Crear el módulo puro que interpreta el resultado de la búsqueda de una
  venta (no encontrada / ya anulada / requiere confirmación), con tests
  unitarios sin React.
  [Cubre RF-2, RF-3, RF-6]
  Hecho cuando: `npm run test -- ventaAnulacion` pasa, cubriendo los
  tres estados.

- [x] **T11 — `buscarVenta` y `anularVenta` en `ventasApi.js`**
  Implementar ambas funciones, con tests con `fetch` mockeado.
  [Cubre RF-1, RF-2, RF-4, RF-7]
  Hecho cuando: `npm run test -- ventasApi` pasa, cubriendo respuestas
  200, 404 y 422 para ambas funciones.

## Fase 4 — Frontend: componente

- [x] **T12 — Esqueleto de `VentaAnulacionForm.jsx`: búsqueda y "no encontrada"**
  Input de ID + botón de búsqueda, llamada a `buscarVenta`, mensaje de
  "no encontrada" usando `ventaAnulacion.js`.
  [Cubre RF-1, RF-2]
  Hecho cuando: un test de RTL con `buscarVenta` mockeado devolviendo
  "no encontrada" muestra el mensaje y no renderiza botón de
  confirmación.

- [x] **T13 — Render de "venta ya anulada"**
  Mostrar el mensaje correspondiente cuando la venta encontrada ya está
  "Anulada", sin botón de confirmación.
  [Cubre RF-6]
  Hecho cuando: un test de RTL con una venta "Anulada" mockeada muestra
  el mensaje y `anularVenta` no se invoca.

- [x] **T14 — Diálogo de confirmación para venta "Confirmada"**
  Mostrar el detalle de la venta y los botones Confirmar/Cancelar
  cuando la venta encontrada está "Confirmada".
  [Cubre RF-3]
  Hecho cuando: un test de RTL con una venta "Confirmada" mockeada
  muestra su detalle junto a ambos botones.

- [x] **T15 — Confirmar anulación exitosa**
  Conectar "Confirmar" a `anularVenta`, mostrar "Venta anulada
  exitosamente" al recibir éxito.
  [Cubre RF-4]
  Hecho cuando: un test de RTL confirma la invocación y el mensaje.

- [x] **T16 — Cancelar confirmación**
  Conectar "Cancelar" para cerrar el diálogo sin invocar ninguna API.
  [Cubre RF-5]
  Hecho cuando: un test de RTL confirma que `anularVenta` NO fue
  invocada tras cancelar.

- [x] **T17 — Manejo del rechazo al confirmar (condición de carrera)**
  Si `anularVenta` devuelve error (422 "ya anulada"), mostrar ese
  mensaje en vez de asumir éxito.
  [Cubre RF-7]
  Hecho cuando: un test de RTL con `anularVenta` mockeado devolviendo un
  error 422 muestra el mensaje de rechazo del backend, no un mensaje de
  éxito.

## Fase 5 — Integración de navegación

- [x] **T18 — Pestaña "Anular Venta" en `App.jsx`**
  Agregar la décima pestaña junto a las nueve existentes.
  [Soporte - sin RF directo]
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar hacia la nueva pestaña.

## Fase 6 — Verificación final

- [x] **T19 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-8 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-8]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada RF de la spec tiene un test
  correspondiente pasando.
