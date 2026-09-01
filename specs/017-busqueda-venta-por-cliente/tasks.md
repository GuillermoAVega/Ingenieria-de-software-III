# Tasks 017 — Búsqueda de Venta por Cliente en Anular y Modificar Venta

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: repositorio

- [x] **T01 — `find_sales_by_customer_dni`: camino feliz**
  Agregar en `repository_venta.py` la función que busca las ventas de
  todos los clientes con ese DNI, ordenadas por fecha descendente, con
  test de integración.
  [Cubre RF-1, RF-6, RF-11]
  Hecho cuando: `pytest -q -k find_sales_by_customer_dni_ventas` pasa,
  cubriendo un cliente con ventas en Borrador, Confirmada y Anulada,
  verificando el orden por fecha descendente.

- [x] **T02 — `find_sales_by_customer_dni`: cliente no encontrado**
  [Cubre RF-2]
  Hecho cuando: `pytest -q -k find_sales_by_customer_dni_inexistente`
  pasa, devolviendo `(False, [])` para un DNI sin ningún cliente.

- [x] **T03 — `find_sales_by_customer_dni`: cliente sin ventas**
  [Cubre RF-4, RF-7]
  Hecho cuando: `pytest -q -k find_sales_by_customer_dni_sin_ventas`
  pasa, devolviendo `(True, [])` para un cliente registrado sin
  ninguna venta.

- [x] **T04 — `find_sales_by_customer_dni`: DNI compartido por varios clientes**
  Verificar que se traen las ventas de todos los `Customer` con ese
  DNI, no solo del Activo.
  [Cubre RF-1]
  Hecho cuando: un test crea un cliente Activo y uno Inactivo con el
  mismo DNI (vía [[014-correcciones-cliente]]), cada uno con al menos
  una venta, y confirma que `find_sales_by_customer_dni` devuelve las
  ventas de ambos.

## Fase 1 — Backend: endpoint

- [x] **T05 — Endpoint `GET /ventas/cliente/{dni}`: camino feliz**
  Implementar la ruta, devolviendo id, fecha, estado y total de cada
  venta, con test de integración.
  [Cubre RF-1, RF-6, RF-11]
  Hecho cuando: `pytest -q -k ventas_cliente_endpoint` pasa,
  verificando que la respuesta incluye `status` por cada venta y el
  orden por fecha descendente.

- [x] **T06 — Endpoint: cliente no encontrado**
  [Cubre RF-2]
  Hecho cuando: un test de integración con un DNI sin cliente devuelve
  404 con "Cliente no encontrado".

- [x] **T07 — Endpoint: cliente sin ventas**
  [Cubre RF-4, RF-7]
  Hecho cuando: un test de integración con un cliente sin ventas
  devuelve `"sales": []`.

## Fase 2 — Frontend: API

- [x] **T08 — `buscarVentasDeCliente` en `ventasApi.js`**
  Implementar la función que llama a `GET /ventas/cliente/{dni}` y
  devuelve `{ success, sales }` o `{ success: false, errors }`, con
  tests con `fetch` mockeado.
  [Cubre RF-1, RF-2]
  Hecho cuando: `npm run test -- ventasApi` pasa, cubriendo una
  respuesta 200 (con y sin ventas) y una 404.

## Fase 3 — Frontend: módulos puros

- [x] **T09 — `evaluateClienteSalesParaAnular` en `ventaAnulacion.js`**
  Agregar la función que interpreta el resultado de
  `buscarVentasDeCliente` filtrando a las ventas Confirmada
  (`CLIENT_NOT_FOUND` / `NO_CONFIRMED_SALES` / `SALES_LIST`),
  eliminando `evaluateAnulacionResult` (ya no se busca por ID), con
  sus tests unitarios.
  [Cubre RF-2, RF-3, RF-4]
  Hecho cuando: `npm run test -- ventaAnulacion` pasa, cubriendo los
  tres estados, incluyendo un cliente con ventas en otros estados pero
  ninguna Confirmada.

- [x] **T10 — `evaluateClienteSalesParaModificar` en `ventaEdicion.js`**
  Agregar la función que interpreta el mismo resultado sin filtrar por
  estado (`CLIENT_NOT_FOUND` / `NO_SALES` / `SALES_LIST`, conservando
  el `status` de cada venta), con sus tests unitarios.
  [Cubre RF-2, RF-6, RF-7]
  Hecho cuando: `npm run test -- ventaEdicion` pasa, cubriendo los tres
  estados, verificando que las ventas de la lista conservan su
  `status`.

## Fase 4 — Frontend: `VentaAnulacionForm.jsx`

- [x] **T11 — Reemplazar la búsqueda por ID por búsqueda por DNI**
  Cambiar el campo "ID de la venta" por "DNI del cliente", conectado a
  `buscarVentasDeCliente` y `evaluateClienteSalesParaAnular`.
  [Cubre RF-1, RF-2]
  Hecho cuando: un test de RTL busca un DNI sin cliente y muestra
  "Cliente no encontrado".

- [x] **T12 — Sin ventas Confirmada**
  [Cubre RF-4]
  Hecho cuando: un test de RTL con un cliente sin ventas Confirmada
  (mockeado con ventas en otro estado) muestra el mensaje
  correspondiente.

- [x] **T13 — Lista de ventas Confirmada y confirmación de anulación**
  Mostrar la lista (ID, fecha, total) con un botón "Anular" por fila
  que abre el diálogo de confirmación ya existente sobre esa venta.
  [Cubre RF-3, RF-5, RF-11]
  Hecho cuando: un test de RTL con varias ventas Confirmada las lista
  todas, y presionar "Anular" en una fila muestra el diálogo con los
  datos de esa venta específica.

- [x] **T14 — Cancelar vuelve a la lista, no a la búsqueda vacía**
  [Soporte - sin RF directo]
  Hecho cuando: un test de RTL presiona "Anular" en una fila, presiona
  "Cancelar", y confirma que la lista de ventas del cliente sigue
  visible (no se limpió el campo de DNI).

- [x] **T15 — Anular exitoso vuelve a listar las ventas restantes**
  [Soporte - sin RF directo]
  Hecho cuando: un test de RTL confirma una anulación exitosa y
  verifica que `buscarVentasDeCliente` se llama de nuevo con el mismo
  DNI (la lista se refresca).

## Fase 5 — Frontend: `VentaEdicionForm.jsx`

- [x] **T16 — Reemplazar la búsqueda por ID por búsqueda por DNI**
  Cambiar el campo "ID de la venta" por "DNI del cliente", conectado a
  `buscarVentasDeCliente` y `evaluateClienteSalesParaModificar`.
  [Cubre RF-1, RF-2]
  Hecho cuando: un test de RTL busca un DNI sin cliente y muestra
  "Cliente no encontrado".

- [x] **T17 — Sin ventas registradas**
  [Cubre RF-7]
  Hecho cuando: un test de RTL con un cliente sin ninguna venta
  muestra el mensaje correspondiente.

- [x] **T18 — Lista de ventas con ícono de editar solo en Borrador**
  Mostrar la lista (ID, fecha, estado, total) con el ícono de editar
  habilitado únicamente en las filas con `status === "Borrador"`.
  [Cubre RF-6, RF-8, RF-11]
  Hecho cuando: un test de RTL con ventas en los tres estados confirma
  que el ícono de editar está deshabilitado (o ausente) en las que no
  están en Borrador.

- [x] **T19 — Presionar el ícono en Borrador abre la edición existente**
  Al presionar el ícono, llamar a `buscarVenta(id)` +
  `evaluateEdicionResult` antes de mostrar la vista de edición ya
  construida.
  [Cubre RF-9]
  Hecho cuando: un test de RTL presiona el ícono sobre una fila en
  Borrador y ve la vista de edición (selector de producto, cantidad,
  etc.) con el detalle cargado.

- [x] **T20 — Verificación de estado al presionar el ícono (condición de carrera)**
  [Cubre RF-10]
  Hecho cuando: un test de RTL con `buscarVenta` mockeado devolviendo
  una venta que ya no está en Borrador (aunque la lista la mostraba
  como tal) confirma que se advierte "La venta ya no admite
  modificaciones" y no se abre la vista de edición.

- [x] **T21 — Volver de la edición regresa a la lista del cliente**
  [Soporte - sin RF directo]
  Hecho cuando: un test de RTL sale de la vista de edición (tras
  guardar o cerrar) y confirma que vuelve a mostrarse la lista de
  ventas del mismo cliente, no un campo de DNI vacío.

## Fase 6 — Verificación final

- [x] **T22 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-11 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-11]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck`
  terminan sin errores ni tests saltados, y cada RF de la spec tiene un
  test correspondiente pasando.
