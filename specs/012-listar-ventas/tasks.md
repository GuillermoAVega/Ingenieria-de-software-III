# Tasks 012 — Listar Ventas

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: núcleo de reglas (`core_venta.py`)

- [x] **T01 — `is_valid_date_range`**
  Crear `core_venta.py` con la función que decide si un rango de fechas
  es válido (sin extremos, con un solo extremo, o "desde" ≤ "hasta"),
  con sus tests unitarios.
  [Cubre RF-6]
  Hecho cuando: `pytest -q -k is_valid_date_range` pasa, cubriendo
  ambos extremos ausentes, un solo extremo, un rango válido y un rango
  con "desde" posterior a "hasta".

- [x] **T02 — `matches_dni`**
  Agregar en `core_venta.py` la función que decide si el DNI de un
  cliente contiene, como texto, el criterio de búsqueda ingresado, con
  sus tests unitarios.
  [Cubre RF-4]
  Hecho cuando: `pytest -q -k matches_dni` pasa, cubriendo una
  coincidencia parcial, un criterio sin coincidencia y un criterio
  vacío (coincide siempre).

## Fase 1 — Backend: repositorio (`repository_venta.py`)

- [x] **T03 — `list_sales`: listado completo sin filtro**
  Agregar la función que trae, con un único `JOIN` a `customers`, todas
  las ventas "Confirmada" ordenadas por fecha descendente, excluyendo
  Borrador y Anulada, con test de integración.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k list_sales_sin_filtro` pasa, verificando
  que una venta "Borrador" y otra "Anulada" quedan excluidas y que el
  orden es por fecha descendente.

- [x] **T04 — `list_sales`: filtro por rango de fechas**
  Integrar la comparación de fechas (sin hora, extremos inclusivos),
  soportando un solo extremo o ambos.
  [Cubre RF-3]
  Hecho cuando: `pytest -q -k list_sales_fechas` pasa, cubriendo una
  venta justo en el límite "desde", otra justo en el límite "hasta", y
  un filtro con un solo extremo cargado.

- [x] **T05 — `list_sales`: filtro por DNI**
  Integrar `core_venta.matches_dni` sobre el cliente de cada venta
  (resuelto por el `JOIN` de T03).
  [Cubre RF-4]
  Hecho cuando: `pytest -q -k list_sales_dni` pasa, cubriendo un DNI
  parcial que coincide con un cliente y no con otro.

- [x] **T06 — `list_sales`: combinación de filtros y sin resultados**
  Verificar que fecha y DNI se aplican con AND, y que sin coincidencias
  devuelve una lista vacía.
  [Cubre RF-5, RF-7]
  Hecho cuando: `pytest -q -k list_sales_combinado` pasa, cubriendo una
  venta que cumple ambos filtros, otra que solo cumple uno (excluida), y
  un filtro sin ninguna coincidencia.

- [x] **T07 — `list_sales`: paginación**
  Agregar los parámetros `page`/`page_size` (default 20), devolviendo
  la porción correspondiente y si existe una página siguiente
  (`has_next`).
  [Cubre RF-9]
  Hecho cuando: `pytest -q -k list_sales_pagina` pasa, insertando 25
  ventas "Confirmada" y verificando que la página 1 trae 20 con
  `has_next=True` y la página 2 trae 5 con `has_next=False`.

## Fase 2 — Backend: endpoint (`routes/ventas.py`)

- [x] **T08 — Endpoint `GET /ventas`: camino feliz**
  Implementar la ruta con `_serialize_sale_summary` (id, fecha,
  cliente, total; sin items ni estado), sin filtros ni `page`
  explícitos (defaults), con test de integración.
  [Cubre RF-1, RF-2, RF-10]
  Hecho cuando: `pytest -q -k listar_ventas_endpoint` pasa, verificando
  que la respuesta de cada venta no incluye `items` ni `status`.

- [x] **T09 — Endpoint: filtro por rango de fechas**
  Integrar `date_from`/`date_to` en la ruta.
  [Cubre RF-3]
  Hecho cuando: un test de integración con `date_from`/`date_to`
  devuelve solo las ventas dentro del rango.

- [x] **T10 — Endpoint: rango de fechas inválido**
  Validar con `core_venta.is_valid_date_range` antes de consultar,
  devolviendo 422 si "desde" es posterior a "hasta".
  [Cubre RF-6]
  Hecho cuando: `pytest -q -k rango_fechas_invalido` pasa, verificando
  422 con el mensaje "El rango de fechas es inválido".

- [x] **T11 — Endpoint: filtro por DNI y combinación**
  Integrar el parámetro `dni` en la ruta, combinable con las fechas.
  [Cubre RF-4, RF-5, RF-7]
  Hecho cuando: un test de integración con `dni` parcial devuelve solo
  las ventas del cliente esperado, otro combinando `dni` y fechas
  devuelve la intersección, y otro sin coincidencias devuelve
  `"sales": []`.

- [x] **T12 — Endpoint: paginación por `page`**
  Integrar el parámetro `page` en la ruta.
  [Cubre RF-9]
  Hecho cuando: un test de integración con más de 20 ventas confirma
  que `page=2` devuelve el resto y `has_next=False`.

## Fase 3 — Frontend: API

- [x] **T13 — `listarVentas` en `ventasApi.js`**
  Implementar la función que llama a `GET /ventas` con
  `dni`/`dateFrom`/`dateTo`/`page` y devuelve `{ sales, page, hasNext }`
  o `{ success: false, errors }` ante un 422, con tests con `fetch`
  mockeado.
  [Cubre RF-1, RF-3, RF-4, RF-6, RF-9]
  Hecho cuando: `npm run test -- ventasApi` pasa, cubriendo una llamada
  sin parámetros, una con todos los filtros, y una respuesta 422.

## Fase 4 — Frontend: componente

- [x] **T14 — Esqueleto de `VentasListado.jsx`: carga inicial**
  Al montarse, pedir la página 1 sin filtros y renderizar la tabla (ID,
  Fecha, Cliente, Total) con las ventas devueltas.
  [Cubre RF-1, RF-10]
  Hecho cuando: un test de RTL con `listarVentas` mockeado confirma que
  se llama sin filtros al montar y que la tabla muestra las filas
  devueltas.

- [x] **T15 — Campos de filtro (fechas y DNI)**
  Agregar los inputs "Desde", "Hasta" y "DNI del cliente" con
  botón/submit que llama a `listarVentas` con los valores ingresados.
  [Cubre RF-3, RF-4, RF-5, RF-8]
  Hecho cuando: un test de RTL confirma que filtrar con fecha y DNI
  llama a `listarVentas` con ambos valores, y que borrar los filtros y
  volver a buscar llama sin ellos.

- [x] **T16 — Mensaje de "sin resultados"**
  Mostrar el mensaje correspondiente cuando `sales` viene vacío, en vez
  de una tabla vacía.
  [Cubre RF-7]
  Hecho cuando: un test de RTL con `listarVentas` mockeado devolviendo
  `sales: []` muestra el mensaje de "no se encontraron resultados" y no
  renderiza la tabla.

- [x] **T17 — Mensaje de rango de fechas inválido**
  Mostrar el mensaje de error del backend cuando `listarVentas` devuelve
  `success: false`.
  [Cubre RF-6]
  Hecho cuando: un test de RTL con `listarVentas` mockeado devolviendo
  el error 422 muestra "El rango de fechas es inválido".

- [x] **T18 — Paginación: Anterior/Siguiente**
  Agregar los controles de paginación: habilitados/deshabilitados según
  `hasNext`/página actual, y reinicio a la página 1 al cambiar
  cualquier filtro.
  [Cubre RF-9]
  Hecho cuando: un test de RTL confirma que con `hasNext: true` el
  botón "Siguiente" pide la página 2, que con `hasNext: false` el botón
  está deshabilitado, y que cambiar un filtro estando en la página 2
  vuelve a pedir la página 1.

## Fase 5 — Integración de navegación

- [x] **T19 — Pestaña "Listar Ventas" en `App.jsx`**
  Agregar la duodécima pestaña junto a las once existentes.
  [Soporte - sin RF directo]
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar hacia la nueva pestaña.

## Fase 6 — Verificación final

- [x] **T20 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-10 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-10]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck`
  terminan sin errores ni tests saltados, y cada RF de la spec tiene un
  test correspondiente pasando.
