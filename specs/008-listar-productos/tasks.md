# Tasks 008 — Listar Productos

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: núcleo de búsqueda (`core_producto.py`)

- [x] **T01 — `matches_search`**
  Agregar en `core_producto.py` la función que decide si un producto
  coincide con un criterio ya normalizado (Nombre o SKU, coincidencia
  parcial), reutilizando `core.normalize_search_text`, con sus tests
  unitarios.
  [Cubre RF-2, RF-3, RF-4]
  Hecho cuando: `pytest -q -k matches_search` pasa, cubriendo coincidencia
  por nombre, por SKU parcial (ej. `"abc"` contra `"ABC123"`), insensible
  a mayúsculas/tildes, y un criterio sin ninguna coincidencia.

## Fase 1 — Backend: repositorio

- [x] **T02 — `list_products`: listado completo sin filtro**
  Agregar en `repository_producto.py` la función que trae todos los
  productos (Activos e Inactivos, ordenados por nombre) cuando no hay
  criterio de búsqueda, con test de integración.
  [Cubre RF-1, RF-6]
  Hecho cuando: `pytest -q -k list_products_sin_filtro` pasa, verificando
  que se incluyen tanto un producto Activo como uno dado de baja.

- [x] **T03 — `list_products`: aplicar el filtro**
  Integrar `core_producto.matches_search` en `list_products` para que,
  con un criterio de búsqueda, devuelva solo los productos que coinciden.
  [Cubre RF-2, RF-3, RF-4, RF-5]
  Hecho cuando: `pytest -q -k list_products_filtro` pasa, cubriendo una
  coincidencia parcial insensible a mayúsculas/tildes y un criterio sin
  coincidencias (lista vacía).

- [x] **T04 — `list_products`: paginación**
  Agregar los parámetros `page`/`page_size` (default 20), devolviendo la
  porción correspondiente y si existe una página siguiente (`has_next`).
  [Cubre RF-8]
  Hecho cuando: `pytest -q -k list_products_pagina` pasa, insertando 25
  productos y verificando que la página 1 trae 20 con `has_next=True` y
  la página 2 trae 5 con `has_next=False`.

## Fase 2 — Backend: endpoint

- [x] **T05 — Endpoint `GET /productos`: camino feliz**
  Implementar la ruta reutilizando `_serialize_product`, sin `q` ni
  `page` explícitos (defaults), con test de integración.
  [Cubre RF-1, RF-6]
  Hecho cuando: `pytest -q -k listar_productos_endpoint` pasa, devolviendo
  todos los productos creados en el test.

- [x] **T06 — Endpoint: filtro por `q`**
  Integrar el parámetro `q` en la ruta (recorte + paso a
  `list_products`).
  [Cubre RF-2, RF-3, RF-4, RF-5]
  Hecho cuando: un test de integración con `q` insensible a
  mayúsculas/tildes devuelve solo los productos esperados, y otro con `q`
  sin coincidencias devuelve `"products": []`.

- [x] **T07 — Endpoint: paginación por `page`**
  Integrar el parámetro `page` en la ruta.
  [Cubre RF-8]
  Hecho cuando: un test de integración con más de 20 productos confirma
  que `page=2` devuelve el resto y `has_next=False`.

## Fase 3 — Frontend: API

- [x] **T08 — `listarProductos` en `productosApi.js`**
  Implementar la función que llama a `GET /productos` con `q`/`page` y
  devuelve `{ products, page, hasNext }`, con tests con `fetch` mockeado.
  [Cubre RF-1, RF-2, RF-8]
  Hecho cuando: `npm run test -- productosApi` pasa, cubriendo una
  llamada sin parámetros y una con `q`/`page`.

## Fase 4 — Frontend: componente

- [x] **T09 — Esqueleto de `ProductoListado.jsx`: carga inicial**
  Al montarse, pedir la página 1 sin filtro y renderizar la tabla (SKU,
  Nombre, Marca, Precio, Stock, Estado) con los productos devueltos.
  [Cubre RF-1, RF-6]
  Hecho cuando: un test de RTL con `listarProductos` mockeado confirma
  que se llama sin `q` al montar y que la tabla muestra las filas
  devueltas, incluido un producto Inactivo.

- [x] **T10 — Campo de búsqueda**
  Agregar el input de búsqueda con botón/submit que llama a
  `listarProductos` con el `q` ingresado.
  [Cubre RF-2, RF-7]
  Hecho cuando: un test de RTL confirma que buscar un criterio llama a
  `listarProductos` con ese `q`, y que borrar el criterio y volver a
  buscar llama sin `q`.

- [x] **T11 — Mensaje de "sin resultados"**
  Mostrar el mensaje correspondiente cuando `products` viene vacío, en
  vez de una tabla vacía.
  [Cubre RF-5]
  Hecho cuando: un test de RTL con `listarProductos` mockeado devolviendo
  `products: []` muestra el mensaje de "no se encontraron resultados" y
  no renderiza la tabla.

- [x] **T12 — Paginación: Anterior/Siguiente**
  Agregar los controles de paginación: habilitados/deshabilitados según
  `hasNext`/página actual, y reinicio a la página 1 al cambiar el
  criterio de búsqueda.
  [Cubre RF-8]
  Hecho cuando: un test de RTL confirma que con `hasNext: true` el botón
  "Siguiente" pide la página 2, que con `hasNext: false` el botón está
  deshabilitado, y que cambiar el criterio estando en la página 2 vuelve
  a pedir la página 1.

## Fase 5 — Integración de navegación

- [x] **T13 — Pestaña "Listar Productos" en `App.jsx`**
  Agregar la octava pestaña junto a las siete existentes.
  [Soporte - sin RF directo]
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar hacia la nueva pestaña.

## Fase 6 — Verificación final

- [x] **T14 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-8 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-8]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada RF de la spec tiene un test
  correspondiente pasando.
