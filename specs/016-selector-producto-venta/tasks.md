# Tasks 016 — Selector de Producto por Nombre o Descripción en Venta

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: núcleo (`core_producto.py`)

- [x] **T01 — `matches_venta_search`**
  Agregar la función que decide si un producto coincide con un
  criterio ya normalizado, comparando contra Nombre y Descripción
  (`description` puede ser `None`), con sus tests unitarios.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k matches_venta_search` pasa, cubriendo
  coincidencia por nombre, por descripción, insensible a
  mayúsculas/tildes, un producto sin descripción, y un criterio sin
  ninguna coincidencia.

## Fase 1 — Backend: repositorio

- [x] **T02 — `search_for_venta`: camino feliz**
  Agregar en `repository_producto.py` la función que trae productos
  Activos que coinciden por nombre o descripción, ordenados por
  nombre, con test de integración.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k search_for_venta_coincidencias` pasa,
  cubriendo una coincidencia por nombre y otra por descripción.

- [x] **T03 — `search_for_venta`: excluye Inactivos**
  [Cubre RF-3]
  Hecho cuando: `pytest -q -k search_for_venta_excluye_inactivos` pasa,
  verificando que un producto Inactivo que coincide con el criterio no
  aparece en el resultado.

- [x] **T04 — `search_for_venta`: límite de resultados y sin `query`**
  [Cubre RF-1, RF-6]
  Hecho cuando: `pytest -q -k search_for_venta_limite` pasa, insertando
  más de 20 productos Activos que coinciden y verificando que se
  devuelven como máximo 20; otro test confirma que un `query` vacío
  devuelve una lista vacía sin consultar coincidencias.

## Fase 2 — Backend: endpoint

- [x] **T05 — Endpoint `GET /productos/buscar-venta`: camino feliz**
  Implementar la ruta (declarada antes de `GET /productos/{sku}` en el
  archivo), devolviendo SKU, nombre, precio unitario y stock de cada
  resultado, con test de integración.
  [Cubre RF-1 a RF-5]
  Hecho cuando: `pytest -q -k buscar_venta_endpoint` pasa, verificando
  que la respuesta de cada producto incluye `sku`, `name`,
  `unit_price` y `stock`, y que excluye productos Inactivos.

- [x] **T06 — Endpoint: sin coincidencias**
  [Cubre RF-6]
  Hecho cuando: un test de integración con un `q` sin coincidencias
  devuelve `"products": []`.

- [x] **T07 — `GET /productos/{sku}` sigue funcionando**
  Confirmar que agregar la ruta nueva no rompió la búsqueda puntual
  por SKU ya existente.
  [Soporte - sin RF directo]
  Hecho cuando: `pytest -q -k buscar_producto` (test ya existente)
  sigue pasando sin modificaciones.

## Fase 3 — Frontend: API

- [x] **T08 — `buscarProductosParaVenta` en `productosApi.js`**
  Implementar la función que llama a `GET /productos/buscar-venta` con
  `q` y devuelve `{ products }`, con tests con `fetch` mockeado.
  [Cubre RF-1]
  Hecho cuando: `npm run test -- productosApi` pasa, cubriendo una
  llamada con `q` y una respuesta con `products: []`.

## Fase 4 — Frontend: `VentaForm.jsx`

- [x] **T09 — Reemplazar el campo SKU por el selector de producto: búsqueda**
  Quitar el input de SKU manual; agregar el campo "Producto" con
  búsqueda en vivo (debounce) que llama a `buscarProductosParaVenta` y
  muestra el desplegable de resultados (Nombre y SKU de cada uno).
  [Cubre RF-1, RF-5]
  Hecho cuando: un test de RTL escribe un criterio y ve las opciones
  devueltas por `buscarProductosParaVenta` mockeado, cada una con su
  Nombre y SKU visibles.

- [x] **T10 — Sin coincidencias**
  [Cubre RF-6]
  Hecho cuando: un test de RTL con `buscarProductosParaVenta` mockeado
  devolviendo `products: []` muestra "No se encontraron productos".

- [x] **T11 — Elegir una opción completa el ítem sin `buscarProducto`**
  Al hacer `onMouseDown` sobre una opción, guardar
  sku/nombre/precio/stock en el estado del componente; "Agregar" pasa
  a usar esos datos directamente.
  [Cubre RF-4, RF-8]
  Hecho cuando: un test de RTL elige una opción, agrega el ítem, y
  confirma que `buscarProducto` (búsqueda puntual por SKU) no fue
  invocada en ningún momento del flujo.

- [x] **T12 — Cambiar el texto tras elegir descarta la selección**
  [Cubre RF-7]
  Hecho cuando: un test de RTL elige una opción, modifica el texto del
  campo "Producto" sin elegir una nueva opción, y confirma que el
  botón "Agregar" queda deshabilitado.

- [x] **T13 — El resto del flujo de armado de ítems sigue igual**
  Revisar y adaptar los tests ya existentes de `VentaForm.test.jsx`
  (cantidad inválida, stock insuficiente, consolidación de ítems
  repetidos, producto inactivo) al nuevo mecanismo de selección.
  [Cubre RF-8]
  Hecho cuando: `npm run test -- VentaForm` pasa completo, sin tests
  salteados ni casos de comportamiento perdidos respecto a los ya
  existentes.

## Fase 5 — Frontend: `VentaEdicionForm.jsx`

- [x] **T14 — Repetir T09 a T13 en `VentaEdicionForm.jsx`**
  Mismo reemplazo del campo SKU por el selector de producto, aplicado
  al formulario de "agregar ítem" dentro de la edición del detalle.
  [Cubre RF-1, RF-4 a RF-8]
  Hecho cuando: `npm run test -- VentaEdicionForm` pasa completo,
  cubriendo los mismos casos que T09-T13 (búsqueda con resultados, sin
  resultados, selección sin `buscarProducto`, cambio de texto
  deshabilita "Agregar", y el resto del flujo sin cambios).

## Fase 6 — Verificación final

- [x] **T15 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-8 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-8]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck`
  terminan sin errores ni tests saltados, y cada RF de la spec tiene un
  test correspondiente pasando.
