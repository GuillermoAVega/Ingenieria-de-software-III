# Tasks 004 — Listar Clientes

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: núcleo de búsqueda (`core.py`)

- [x] **T01 — `normalize_search_text`**
  Implementar en `core.py` la función que normaliza un texto a minúsculas
  y sin tildes, con sus tests unitarios.
  [Cubre RF-4]
  Hecho cuando: `pytest -q -k normalize_search_text` pasa, cubriendo
  `"Pérez"`/`"perez"` y `"ÑOÑO"`/`"ñoño"` normalizando al mismo valor.

- [x] **T02 — `matches_search`**
  Implementar en `core.py` la función que decide si un cliente coincide
  con un criterio ya normalizado (Nombre, Apellido o DNI, coincidencia
  parcial), con sus tests unitarios.
  [Cubre RF-2, RF-3]
  Hecho cuando: `pytest -q -k matches_search` pasa, cubriendo coincidencia
  por nombre, por apellido, por DNI parcial (ej. `"301112"` contra un
  cliente de DNI `30111222`) y un criterio sin ninguna coincidencia.

## Fase 1 — Backend: repositorio

- [x] **T03 — `list_customers`: listado completo sin filtro**
  Implementar en `repository.py` la función que trae todos los clientes
  (Activos e Inactivos, ordenados por apellido y nombre) cuando no hay
  criterio de búsqueda, con test de integración sobre SQLite temporal.
  [Cubre RF-1, RF-6]
  Hecho cuando: `pytest -q -k list_customers_sin_filtro` pasa, verificando
  que se incluyen tanto un cliente Activo como uno dado de baja.

- [x] **T04 — `list_customers`: aplicar el filtro**
  Integrar `core.matches_search` en `list_customers` para que, con un
  criterio de búsqueda, devuelva solo los clientes que coinciden.
  [Cubre RF-2, RF-3, RF-4, RF-5]
  Hecho cuando: `pytest -q -k list_customers_filtro` pasa, cubriendo una
  coincidencia parcial insensible a mayúsculas/tildes y un criterio sin
  coincidencias (lista vacía).

- [x] **T05 — `list_customers`: paginación**
  Agregar los parámetros `page`/`page_size` (default 20) a
  `list_customers`, devolviendo la porción correspondiente y si existe una
  página siguiente (`has_next`).
  [Cubre RF-8]
  Hecho cuando: `pytest -q -k list_customers_pagina` pasa, insertando 25
  clientes y verificando que la página 1 trae 20 con `has_next=True` y la
  página 2 trae 5 con `has_next=False`.

## Fase 2 — Backend: endpoint

- [x] **T06 — Endpoint `GET /clientes`: camino feliz**
  Implementar la ruta reutilizando `_serialize_customer`, sin `q` ni
  `page` explícitos (defaults), con test de integración vía `TestClient`.
  [Cubre RF-1, RF-6]
  Hecho cuando: `pytest -q -k listar_clientes_endpoint` pasa, devolviendo
  todos los clientes creados en el test.

- [x] **T07 — Endpoint: filtro por `q`**
  Integrar el parámetro `q` en la ruta (recorte + paso a
  `list_customers`).
  [Cubre RF-2, RF-3, RF-4, RF-5]
  Hecho cuando: un test de integración con `q` insensible a
  mayúsculas/tildes devuelve solo los clientes esperados, y otro con `q`
  sin coincidencias devuelve `"customers": []`.

- [x] **T08 — Endpoint: paginación por `page`**
  Integrar el parámetro `page` en la ruta.
  [Cubre RF-8]
  Hecho cuando: un test de integración con más de 20 clientes creados
  confirma que `page=2` devuelve el resto y `has_next=False`.

## Fase 3 — Frontend: API

- [x] **T09 — `listarClientes` en `clientesApi.js`**
  Implementar la función que llama a `GET /clientes` con `q`/`page` y
  devuelve `{ customers, page, hasNext }`, con tests con `fetch` mockeado.
  [Cubre RF-1, RF-2, RF-8]
  Hecho cuando: `npm run test -- clientesApi` pasa, cubriendo una llamada
  sin parámetros y una con `q`/`page`.

## Fase 4 — Frontend: componente

- [x] **T10 — Esqueleto de `ClienteListado.jsx`: carga inicial**
  Al montarse, pedir la página 1 sin filtro y renderizar la tabla (DNI,
  Nombre, Apellido, Estado) con los clientes devueltos.
  [Cubre RF-1, RF-6]
  Hecho cuando: un test de RTL con `listarClientes` mockeado confirma que
  se llama sin `q` al montar y que la tabla muestra las filas devueltas,
  incluido un cliente Inactivo.

- [x] **T11 — Campo de búsqueda**
  Agregar el input de búsqueda con botón/submit que llama a
  `listarClientes` con el `q` ingresado.
  [Cubre RF-2, RF-7]
  Hecho cuando: un test de RTL confirma que buscar un criterio llama a
  `listarClientes` con ese `q`, y que borrar el criterio y volver a buscar
  llama sin `q` (vuelve a la lista completa).

- [x] **T12 — Mensaje de "sin resultados"**
  Mostrar el mensaje correspondiente cuando `customers` viene vacío, en
  vez de una tabla vacía.
  [Cubre RF-5]
  Hecho cuando: un test de RTL con `listarClientes` mockeado devolviendo
  `customers: []` muestra el mensaje de "no se encontraron resultados" y
  no renderiza la tabla.

- [x] **T13 — Paginación: Anterior/Siguiente**
  Agregar los controles de paginación: habilitados/deshabilitados según
  `hasNext`/página actual, y reinicio a la página 1 al cambiar el
  criterio de búsqueda.
  [Cubre RF-8]
  Hecho cuando: un test de RTL confirma que con `hasNext: true` el botón
  "Siguiente" pide la página 2, que con `hasNext: false` el botón está
  deshabilitado, y que cambiar el criterio estando en la página 2 vuelve a
  pedir la página 1.

## Fase 5 — Integración de navegación

- [x] **T14 — Pestaña "Listar Clientes" en `App.jsx`**
  Agregar la cuarta pestaña junto a Alta, Baja y Edición.
  [Soporte - sin RF directo]
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar entre las cuatro vistas.

## Fase 6 — Verificación final

- [x] **T15 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-8 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-8]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada RF de la spec tiene un test
  correspondiente pasando.
