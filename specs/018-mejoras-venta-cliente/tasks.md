# Tasks 018 — Mejoras sobre Venta y Cliente

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: repositorio (`repository_venta.py`)

- [x] **T01 — `create_confirmed_sale`: camino feliz**
  Implementar `create_confirmed_sale(session, customer, items)`: crea la
  `Sale` directamente con `status=SaleStatus.CONFIRMED`, sus `SaleItem`,
  descuenta `product.stock` de cada ítem, y hace un único `commit`
  (sin pasar por `create_sale` + `close_sale`).
  [Cubre RF-4]
  Hecho cuando: `pytest -q -k create_confirmed_sale` pasa, verificando
  que la venta queda "Confirmada", su total calculado es correcto, y el
  stock de cada producto del detalle queda descontado en la misma
  cantidad que su ítem.

## Fase 1 — Backend: endpoint (`routes/ventas.py`)

- [x] **T02 — `POST /ventas/confirmar`: camino feliz**
  Agregar el endpoint: resuelve los ítems con `_resolve_items` usando
  `require_non_empty=True, check_product_active=True, check_stock=True`
  (mismo criterio que `PUT /ventas/{id}/detalle`), busca al cliente por
  DNI, y si no hay errores llama a `create_confirmed_sale` (T01).
  [Cubre RF-2, RF-4]
  Hecho cuando: `pytest -q -k confirmar_venta_exitosa` pasa, devolviendo
  `201` con `sale.status == "Confirmada"` y confirmando (con un
  `GET /productos` o consultando el producto) que su stock quedó
  descontado.

- [x] **T03 — `POST /ventas/confirmar`: cliente no encontrado e ítems vacíos**
  [Cubre RF-2]
  Hecho cuando: `pytest -q -k confirmar_venta_cliente_no_encontrado` y
  `pytest -q -k confirmar_venta_items_vacios` pasan, ambos devolviendo
  `422` sin crear ninguna `Sale`.

- [x] **T04 — `POST /ventas/confirmar`: producto inactivo bloquea la creación**
  [Cubre RF-6]
  Hecho cuando: `pytest -q -k confirmar_venta_producto_inactivo` pasa,
  devolviendo `422` y verificando que no se creó ninguna venta ni se
  modificó el stock de ningún producto.

- [x] **T05 — `POST /ventas/confirmar`: stock insuficiente bloquea la creación**
  [Cubre RF-5]
  Hecho cuando: `pytest -q -k confirmar_venta_stock_insuficiente` pasa,
  devolviendo `422` sin crear ninguna venta ni descontar stock.

- [x] **T06 — `POST /ventas/confirmar`: reporta varios errores a la vez**
  [Cubre caso límite de errores combinados]
  Hecho cuando: `pytest -q -k confirmar_venta_multiples_errores` pasa,
  con un detalle que tiene un ítem sin stock suficiente y otro con
  producto inactivo, devolviendo ambos errores en la misma respuesta y
  sin crear la venta.

## Fase 2 — Frontend: lógica pura nueva

- [x] **T07 — `dateFormat.js`: `toDateOnly`**
  Crear el módulo con `toDateOnly(isoDateTime)` (recorta un datetime ISO
  a `"YYYY-MM-DD"`) y su test.
  [Cubre RF-12]
  Hecho cuando: `npm run test -- dateFormat` pasa, cubriendo un ISO con
  microsegundos, uno sin ellos, y uno con offset `+00:00` y con `Z`.

- [x] **T08 — `ventaListado.js`: `evaluateDetalleVenta`**
  Crear el módulo, análogo a `ventaEdicion.js`/`ventaAnulacion.js`, con
  `evaluateDetalleVenta(searchResult)` que devuelve `FOUND` con la venta
  o `NOT_FOUND` con el mensaje "Venta no encontrada".
  [Cubre RF-9, RF-10, caso límite de venta ya inexistente]
  Hecho cuando: `npm run test -- ventaListado` pasa, cubriendo ambos
  estados.

## Fase 3 — Frontend: API client

- [x] **T09 — `confirmarVenta` en `ventasApi.js`**
  Agregar `confirmarVenta(input)` (mismo shape de entrada que
  `registrarVenta`) que hace `POST /ventas/confirmar`.
  [Cubre RF-4, wiring]
  Hecho cuando: `npm run test -- ventasApi` pasa, incluyendo un caso de
  éxito y uno de error para `confirmarVenta`.

## Fase 4 — Frontend: `VentaForm.jsx` (Registrar Venta)

- [x] **T10 — Botón "Quitar" en el detalle**
  Agregar una columna de acción a la tabla de ítems con un botón que
  llama a `removeItem` (ya existente en `ventaDetalle.js`) y recalcula
  el total.
  [Cubre RF-1]
  Hecho cuando: un test de `VentaForm.test.jsx` arma el detalle con dos
  ítems, quita uno, y verifica que desaparece de la tabla y que el
  total mostrado baja al del ítem restante.

- [x] **T11 — Dos acciones separadas con su propia confirmación**
  Reemplazar el botón único "Registrar venta" (con su modal genérico)
  por dos botones — "Registrar venta" y "Confirmar venta" — cada uno
  con su propio modal "¿Confirmás…?" y su propio estado de carga.
  [Cubre RF-2, RF-7, RF-8]
  Hecho cuando: un test de `VentaForm.test.jsx` confirma que cancelar la
  confirmación de "Registrar venta" no llama a `registrarVenta` ni a
  `confirmarVenta`, y que cancelar la de "Confirmar venta" tampoco
  llama a ninguna de las dos.

- [x] **T12 — "Registrar venta" sin cambios de comportamiento**
  Verificar/ajustar que el botón "Registrar venta" siga invocando
  `registrarVenta` y mostrando el mismo mensaje de éxito de siempre.
  [Cubre RF-3]
  Hecho cuando: el test existente de registro exitoso en
  `VentaForm.test.jsx` sigue pasando sin modificaciones de aserciones.

- [x] **T13 — "Confirmar venta" llama a `confirmarVenta`**
  Conectar el botón "Confirmar venta" a `confirmarVenta` (T09) y mostrar
  el mensaje de éxito devuelto, limpiando el formulario igual que hace
  hoy "Registrar venta".
  [Cubre RF-4]
  Hecho cuando: un test de `VentaForm.test.jsx` confirma que, tras
  confirmar, se llama a `confirmarVenta` con el DNI y los ítems armados,
  y se muestra el mensaje de éxito.

- [x] **T14 — "Confirmar venta": errores de stock y de producto inactivo**
  Mostrar el mensaje de error correspondiente cuando `confirmarVenta`
  devuelve un error de stock insuficiente o de producto inactivo, sin
  limpiar el detalle armado.
  [Cubre RF-5, RF-6]
  Hecho cuando: dos tests de `VentaForm.test.jsx` (uno por tipo de
  error) confirman que se muestra el mensaje de error devuelto por la
  API y que el detalle armado sigue visible para corregir o reintentar.

## Fase 5 — Frontend: `VentasListado.jsx` (Listar Ventas)

- [x] **T15 — Ícono de ver detalle por fila**
  Agregar una columna de acción con el ícono de ojo en cada fila de la
  tabla de ventas.
  [Cubre RF-9]
  Hecho cuando: un test de `VentasListado.test.jsx` confirma que cada
  fila renderizada tiene un botón/ícono de "ver detalle".

- [x] **T16 — Modal de detalle**
  Al presionar el ícono, llamar a `buscarVenta(id)`, interpretar el
  resultado con `evaluateDetalleVenta` (T08), y mostrar en un modal la
  tabla de ítems (producto, cantidad, precio unitario, subtotal), el
  total, la fecha, el cliente y el estado.
  [Cubre RF-10]
  Hecho cuando: un test de `VentasListado.test.jsx` confirma que, tras
  el click, el modal muestra los ítems devueltos por `buscarVenta`; otro
  test cubre el caso en que `buscarVenta` falla y el modal muestra "Venta
  no encontrada".

- [x] **T17 — Cerrar el modal conserva el listado de fondo**
  Implementar el cierre del modal sin disparar ningún nuevo pedido de
  listado.
  [Cubre RF-11]
  Hecho cuando: un test de `VentasListado.test.jsx` aplica un filtro y
  una página, abre y cierra el modal, y confirma que el listado
  mostrado y `listarVentas` no se volvieron a invocar con otros
  parámetros.

- [x] **T18 — Formato de fecha en el listado**
  Aplicar `toDateOnly` (T07) a la columna Fecha de la tabla principal.
  [Cubre RF-12]
  Hecho cuando: un test de `VentasListado.test.jsx` confirma que la
  columna Fecha muestra `"YYYY-MM-DD"` a partir de un `sale_date` ISO
  completo devuelto por el mock de `listarVentas`.

## Fase 6 — Frontend: formato de fecha en el resto de las pantallas de Venta

- [x] **T19 — Formato de fecha en `VentaAnulacionForm.jsx`**
  Aplicar `toDateOnly` a la columna Fecha de la tabla de ventas del
  cliente.
  [Cubre RF-12]
  Hecho cuando: un test de `VentaAnulacionForm.test.jsx` confirma el
  formato `"YYYY-MM-DD"` en esa columna.

- [x] **T20 — Formato de fecha en `VentaEdicionForm.jsx`**
  Aplicar `toDateOnly` a la columna Fecha de la tabla de ventas del
  cliente.
  [Cubre RF-12]
  Hecho cuando: un test de `VentaEdicionForm.test.jsx` confirma el
  formato `"YYYY-MM-DD"` en esa columna.

## Fase 7 — Frontend: `ClienteEdicionForm.jsx` (Modificar Cliente)

- [x] **T21 — Eliminar el modal de confirmación**
  Quitar el estado `showConfirm` y el bloque de confirmación; mover la
  lógica de `handleConfirm` (llamar a `editarCliente` y procesar la
  respuesta) directamente a `handleSubmit`, ejecutándose apenas
  `validateClienteForm` no devuelve errores.
  [Cubre RF-13]
  Hecho cuando: un test de `ClienteEdicionForm.test.jsx` confirma que,
  con datos válidos, tocar "Guardar cambios" llama a `editarCliente` sin
  que aparezca ningún modal ni botón "Confirmar" intermedio.

- [x] **T22 — Formulario inválido sigue bloqueando el guardado**
  [Cubre RF-14]
  Hecho cuando: un test de `ClienteEdicionForm.test.jsx` confirma que,
  con un campo inválido, "Guardar cambios" muestra los errores
  correspondientes y no llama a `editarCliente`.

## Fase 8 — Verificación final

- [x] **T23 — Suite completa en verde**
  [Soporte - sin RF directo]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck`
  terminan sin fallos.
