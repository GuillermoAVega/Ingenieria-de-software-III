# Plan 008 — Listar Productos

Plan técnico para implementar `specs/008-listar-productos/spec.md`,
respetando `docs/constitution.md` y reutilizando el diseño ya validado en
[[004-listar-clientes]] (mismo patrón de filtro + paginación) y lo ya
construido en [[005-alta-producto]]/[[006-baja-producto]]/
[[007-modificacion-producto]] (`Product`, `_serialize_product`,
`productosApi.js`). Este documento no contiene código: describe
estructura, decisiones y estrategia de verificación.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`core_producto.py` (extendido)**: agrega `matches_search` (decide si
  un producto coincide con un criterio ya normalizado, comparando contra
  Nombre y SKU), reutilizando `core.normalize_search_text` (utilidad
  genérica). Vive en `core_producto.py`, no en `core.py`, siguiendo el
  patrón por dominio ya establecido desde [[005-alta-producto]]. [Cubre
  RF-2, RF-3, RF-4]
- **`repository_producto.py` (extendido)**: agrega `list_products(session,
  query, page, page_size=20)`, que trae todos los productos (Activos e
  Inactivos, ordenados por nombre), aplica `core_producto.matches_search`
  cuando hay criterio, y devuelve la porción de esa página junto con si
  existe una página siguiente. [Cubre RF-1, RF-2, RF-6, RF-8]
- **`routes/productos.py` (extendido)**: agrega `GET /productos` (distinto
  de `GET /productos/{sku}`, ya existente para la búsqueda puntual de
  [[006-baja-producto]]/[[007-modificacion-producto]]), que orquesta:
  recorta y normaliza el parámetro `q`, llama a
  `repository_producto.list_products`, y arma la respuesta paginada
  reutilizando `_serialize_product`. [Cubre RF-1 a RF-8]

### Frontend (`app/frontend/`)

- **`api/productosApi.js` (extendido)**: agrega `listarProductos({ q, page
  })`, que llama a `GET /productos` y devuelve `{ products, page, hasNext
  }`. [Cubre RF-1, RF-2, RF-8]
- **`components/ProductoListado.jsx` (nuevo)**: input de búsqueda (disparo
  por submit, no por tecla), tabla de resultados (SKU, Nombre, Marca,
  Precio, Stock, Estado), mensaje de "no se encontraron resultados" y
  controles Anterior/Siguiente. Al montarse, pide la página 1 sin filtro.
  [Cubre RF-1 a RF-8]
- **`App.jsx` (extendido)**: agrega la octava pestaña "Listar Productos".
  [Soporte, sin RF directo]

## 2. Modelo de la Base de Datos

No se agregan tablas ni columnas nuevas. Esta feature es de solo lectura
sobre la tabla `products` ya definida en [[005-alta-producto]]/
[[006-baja-producto]]:

| Columna | Uso en esta feature |
|---|---|
| `sku` | Se compara normalizado (sin distinguir mayúsculas/tildes) contra el criterio de búsqueda. [Cubre RF-2, RF-3, RF-4] |
| `name` | Se compara normalizado contra el criterio de búsqueda. [Cubre RF-2, RF-3, RF-4] |
| `brand`, `description`, `unit_price`, `stock` | Se muestran en la tabla de resultados, pero no participan del filtro (fuera de alcance). [Cubre RF-1] |
| `status` | Se muestra en cada fila; no se usa como filtro (RF-6 exige incluir ambos estados siempre). [Cubre RF-1, RF-6] |

El filtrado se resuelve en Python, no con `LIKE` de SQL (ver Decisión
Técnica 1), igual que en [[004-listar-clientes]].

## 3. Contrato de la Interfaz Web

### Endpoint: `GET /productos`

- **Método y ruta:** `GET /productos?q=<texto opcional>&page=<entero, default 1>`
- **Payload de entrada:** query params `q` (string, opcional) y `page`
  (entero ≥ 1, opcional, default 1).
- **Respuesta esperada (éxito):** `200 OK`
  ```json
  {
    "products": [
      { "sku": "ABC123", "name": "Coca-Cola 500ml", "brand": "Coca-Cola",
        "description": "Botella descartable", "unit_price": 350.5,
        "stock": 100, "status": "Activo" }
    ],
    "page": 1,
    "has_next": false
  }
  ```
  Un `q` sin coincidencias devuelve `"products": []` con `200 OK` (RF-5 se
  resuelve en el Frontend a partir de un arreglo vacío). [Cubre RF-1 a
  RF-6, RF-8]
- **Respuesta esperada (error):** `422 Unprocessable Entity` (generado
  por FastAPI) únicamente si `page` no es un entero ≥ 1; no alcanzable
  desde la UI en uso normal.

### Vista: pestaña "Listar Productos" (`ProductoListado.jsx`)

- **Ruta/URL:** no aplica (SPA de una sola página con pestañas).
- **Propósito:** consultar y filtrar el catálogo por Nombre o Código/SKU,
  viendo stock y estado. [Cubre HU-PROD-04]
- **Componentes/estados clave:**
  - Campo de búsqueda único (`q`).
  - Tabla de resultados: SKU, Nombre, Marca, Precio unitario, Stock,
    Estado.
  - Estado "sin resultados": mensaje en vez de tabla vacía. [Cubre RF-5]
  - Controles "Anterior" / "Siguiente", deshabilitados cuando no hay
    página previa o siguiente. [Cubre RF-8]
  - Al modificar el criterio de búsqueda, la página vuelve a 1. [Cubre
    RF-7, RF-8]

## 4. Decisiones Técnicas

1. **Decisión Tomada:** filtrar y paginar en Python (dentro de
   `repository_producto.list_products`), trayendo todos los productos y
   aplicando `core_producto.matches_search`/`slice` en memoria, en vez de
   traducir el filtro a `LIKE`/`ORDER BY`/`LIMIT` de SQL.
   **Justificación:** mismo motivo que la decisión técnica 1 de
   [[004-listar-clientes]]: SQLite no resuelve de forma nativa la
   insensibilidad a tildes que pide RF-4, y agregar una extensión o
   columnas de texto normalizado no está justificado para el volumen de
   datos de este proyecto (regla 1 de la constitución).
   **Alternativa descartada:** extensión SQLite de comparación sin
   acentos, o una columna `name_normalized` mantenida en cada alta/edición
   — descartada por la misma razón que en Cliente: complejidad y riesgo
   de desincronización. *(RF-2, RF-3, RF-4)*

2. **Decisión Tomada:** `matches_search` de Producto vive en
   `core_producto.py`, no en `core.py` ni junto al `matches_search` de
   Cliente.
   **Justificación:** sigue el patrón por dominio ya establecido desde
   [[005-alta-producto]] (decisión técnica 1 de ese plan): cada dominio
   tiene su propio núcleo de reglas, reutilizando solo las utilidades
   genéricas de `core.py` (`normalize_search_text`,
   `trim_leading_trailing_space`).
   **Alternativa descartada:** agregar la función de Producto al
   `matches_search` ya existente en `core.py` (el de Cliente), con un
   parámetro que distinga el dominio — descartada por mezclar reglas de
   negocio de dos dominios sin relación en una sola función. *(RF-2,
   RF-3, RF-4)*

3. **Decisión Tomada:** el filtro compara solo contra Nombre y SKU, sin
   incluir Marca, Descripción, Precio unitario ni Stock.
   **Justificación:** es exactamente lo que pide el criterio de
   aceptación de la spec ("por nombre o código de producto"); incluir
   campos no pedidos (en especial numéricos como Precio/Stock, donde
   "coincidencia parcial de texto" no tiene un significado claro) sería
   diseñar para un requisito que no existe.
   **Alternativa descartada:** extender el filtro a Marca/Descripción
   como en un buscador genérico — descartada por no estar pedida y añadir
   ambigüedad sobre campos numéricos. *(RF-2)*

4. **Decisión Tomada:** paginación con `page` + `has_next` (sin `total`
   ni `total_pages`), igual que [[004-listar-clientes]].
   **Justificación:** RF-8 solo pide navegación Anterior/Siguiente, no
   números de página ni conteo total.
   **Alternativa descartada:** devolver `total`/`total_pages` — descartada
   por anticipar un requisito no pedido (fuera de alcance: "ordenamiento/
   paginación configurable"). *(RF-8)*

5. **Decisión Tomada:** no se crea un módulo puro adicional para decidir
   "vacío vs. con resultados" en `ProductoListado.jsx`; queda como un
   condicional simple (`products.length === 0`).
   **Justificación:** mismo razonamiento que la decisión técnica 5 de
   [[004-listar-clientes]] — la única regla de negocio real (qué cuenta
   como coincidencia) ya vive en `core_producto.py`.
   **Alternativa descartada:** un módulo `productoListado.js` con una
   función `evaluateListado(products)` — descartada por no encapsular
   ninguna regla de negocio real. *(RF-5)*

6. **Decisión Tomada:** el filtro se dispara al enviar el formulario de
   búsqueda (submit), no en cada tecla, mismo patrón que
   [[004-listar-clientes]].
   **Justificación:** consistencia de interacción entre ambos listados de
   la app.
   **Alternativa descartada:** debounce por tecla — descartada por no
   estar pedida y agregar complejidad no justificada. *(RF-2)*

## 5. Estrategia de Tests

### Backend — tests unitarios (`core_producto.py`, sin base de datos)
- `matches_search`: coincidencia parcial por nombre y por SKU (ej.
  `"abc"` coincide con el producto de SKU `"ABC123"`); insensible a
  mayúsculas/tildes en el nombre; un criterio que no aparece en ningún
  campo no coincide. [Cubre RF-2, RF-3, RF-4]

### Backend — tests de integración (`repository_producto.py`, SQLite temporal)
- `list_products` sin `query` devuelve todos los productos, Activos e
  Inactivos. [Cubre RF-1, RF-6]
- `list_products` con un `query` que coincide por nombre o SKU devuelve
  solo esos productos. [Cubre RF-2, RF-3]
- `list_products` con un `query` sin coincidencias devuelve una lista
  vacía. [Cubre RF-5]
- `list_products` con más de 20 productos devuelve solo los primeros 20 y
  `has_next=True`; la página 2 devuelve el resto con `has_next=False`.
  [Cubre RF-8]

### Backend — tests de integración (`routes/productos.py`, `TestClient`)
- `GET /productos` sin `q` devuelve todos los productos creados en el
  test, incluido uno dado de baja. [Cubre RF-1, RF-6]
- `GET /productos?q=...` con coincidencia parcial e insensible a
  mayúsculas/tildes devuelve solo los productos esperados. [Cubre RF-2,
  RF-3, RF-4]
- `GET /productos?q=...` sin coincidencias devuelve `"products": []`.
  [Cubre RF-5]
- `GET /productos?page=2` sobre más de 20 productos devuelve el resto y
  `has_next=False`. [Cubre RF-8]

### Frontend — tests sobre `productosApi.js` (fetch mockeado)
- `listarProductos`: traduce una llamada sin parámetros y una con
  `q`/`page`. [Cubre RF-1, RF-2, RF-8]

### Frontend — Vitest + RTL sobre `ProductoListado.jsx`
Con `listarProductos` mockeado:
- Al montar, se pide la página 1 sin filtro y se renderiza la tabla,
  incluido un producto Inactivo. [Cubre RF-1, RF-6]
- Buscar un criterio sin resultados muestra "no se encontraron
  resultados" en vez de una tabla vacía. [Cubre RF-5]
- Borrar el criterio vuelve a pedir la lista completa (sin `q`). [Cubre
  RF-7]
- Con `hasNext: true`, "Siguiente" pide la página 2; con `hasNext: false`,
  el botón está deshabilitado. [Cubre RF-8]
- Cambiar el criterio estando en la página 2 vuelve a pedir la página 1.
  [Cubre RF-8]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas (se descartó
  explícitamente una extensión SQLite y un mecanismo de debounce; ver
  decisiones 1 y 6).
- **Regla 2 (spec antes que código):** parte de
  `specs/008-listar-productos/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** `core_producto.py`
  concentra la regla de "qué es una coincidencia", testeable sin HTTP ni
  React.
- **Regla 4 (tests obligatorios):** la estrategia cubre los ocho RF de la
  spec.
- **Regla 5 (persistencia única):** `list_products` lee exclusivamente de
  `database.py`/la tabla `products`.
- **Regla 6 (idioma consistente):** identificadores en inglés
  (`list_products`, `ProductoListado.jsx`); mensajes en español ("No se
  encontraron resultados").
