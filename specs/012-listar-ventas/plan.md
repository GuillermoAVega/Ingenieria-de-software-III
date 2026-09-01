# Plan 012 — Listar Ventas

Plan técnico para implementar `specs/012-listar-ventas/spec.md`,
respetando `docs/constitution.md` y reutilizando el patrón de listado +
filtro + paginación ya validado en [[004-listar-clientes]] y
[[008-listar-productos]], sobre lo ya construido para Venta en
[[009-alta-venta]]/[[010-anular-venta]]/[[011-modificacion-venta]]
(`Sale`, `SaleItem`, `repository_venta.py`, `routes/ventas.py`,
`ventasApi.js`). Este documento no contiene código: describe estructura,
decisiones y estrategia de verificación.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`core_venta.py` (nuevo)**: primer módulo de reglas puras del dominio
  Venta, siguiendo el patrón por dominio ya establecido desde
  [[005-alta-producto]] (`core_producto.py`). Agrega:
  - `is_valid_date_range(date_from, date_to)`: decide si un rango de
    fechas es válido (ninguno de los dos extremos, o "desde" ≤ "hasta").
    [Cubre RF-6]
  - `matches_dni(dni, query)`: decide si el DNI de un cliente (entero)
    contiene, como texto, el criterio de búsqueda ingresado. [Cubre RF-4]
- **`repository_venta.py` (extendido)**: agrega `list_sales(session,
  dni=None, date_from=None, date_to=None, page=1, page_size=20)`, que:
  1. Trae, en una sola consulta con `JOIN` a `customers`, todas las
     ventas en estado "Confirmada" junto con su cliente. [Cubre RF-1,
     RF-2]
  2. Filtra en Python por rango de fechas (comparando solo la fecha,
     sin la hora, de `Sale.sale_date`) y por `core_venta.matches_dni`
     cuando corresponda. [Cubre RF-3, RF-4, RF-5]
  3. Ordena el resultado por `sale_date` descendente. [Cubre RF-1]
  4. Recorta la página pedida y calcula si existe una página siguiente.
     [Cubre RF-9]
- **`routes/ventas.py` (extendido)**: agrega `GET /ventas` (distinto de
  `GET /ventas/{sale_id}`, ya existente para la búsqueda puntual de
  [[010-anular-venta]]/[[011-modificacion-venta]]), que:
  1. Valida el rango de fechas con `core_venta.is_valid_date_range`
     antes de consultar nada. [Cubre RF-6]
  2. Recorta y normaliza el parámetro `dni`. [Cubre RF-4]
  3. Llama a `repository_venta.list_sales` y arma la respuesta paginada
     con una serialización liviana (`_serialize_sale_summary`, ver
     Decisión Técnica 2), sin items ni estado. [Cubre RF-1 a RF-10]

### Frontend (`app/frontend/`)

- **`api/ventasApi.js` (extendido)**: agrega `listarVentas({ dni,
  dateFrom, dateTo, page })`, que llama a `GET /ventas` y devuelve
  `{ success: true, sales, page, hasNext }` o `{ success: false, errors
  }` ante el 422 de rango inválido. [Cubre RF-1 a RF-9]
- **`components/VentasListado.jsx` (nuevo)**: campos "Desde", "Hasta" y
  "DNI del cliente" (disparo por submit, no por tecla, mismo patrón que
  [[008-listar-productos]]), tabla de resultados (ID, Fecha, Cliente,
  Total), mensaje de "no se encontraron resultados", mensaje de rango de
  fechas inválido, y controles Anterior/Siguiente. Al montarse, pide la
  página 1 sin filtros. [Cubre RF-1 a RF-10]
- **`App.jsx` (extendido)**: agrega la duodécima pestaña "Listar
  Ventas". [Soporte, sin RF directo]

## 2. Modelo de la Base de Datos

No se agregan tablas ni columnas nuevas. Esta feature es de solo lectura
sobre `sales` ([[009-alta-venta]]) y `customers` ([[001-alta-cliente]]):

| Columna | Uso en esta feature |
|---|---|
| `sales.status` | Filtro fijo: solo se consideran ventas `"Confirmada"`; no se expone en la respuesta (siempre sería el mismo valor). [Cubre RF-2] |
| `sales.sale_date` | Se compara (solo la fecha, sin hora) contra "desde"/"hasta"; determina el orden del listado. [Cubre RF-1, RF-3] |
| `sales.total` | Se muestra en cada fila. [Cubre RF-10] |
| `sales.customer_id` | Se une con `customers.id` para resolver el cliente de cada venta. [Cubre RF-4, RF-10] |
| `customers.dni` | Se compara (como texto, coincidencia parcial) contra el criterio de búsqueda; se muestra en cada fila. [Cubre RF-4, RF-10] |
| `customers.first_name`, `customers.last_name` | Se muestran en cada fila. [Cubre RF-10] |

El filtrado se resuelve en Python tras un único `JOIN` a `customers`, no
con múltiples consultas por venta (ver Decisión Técnica 1 y 2).

## 3. Contrato de la Interfaz Web

### Endpoint: `GET /ventas`

- **Método y ruta:** `GET /ventas?dni=<texto opcional>&date_from=<fecha ISO opcional>&date_to=<fecha ISO opcional>&page=<entero, default 1>`
- **Payload de entrada:** query params `dni` (string, opcional),
  `date_from`/`date_to` (fecha `YYYY-MM-DD`, opcionales) y `page`
  (entero ≥ 1, opcional, default 1).
- **Respuesta esperada (éxito):** `200 OK`
  ```json
  {
    "sales": [
      {
        "id": 1,
        "sale_date": "2026-03-01T10:00:00+00:00",
        "customer": { "dni": 30111222, "first_name": "Juan", "last_name": "Perez" },
        "total": 701.0
      }
    ],
    "page": 1,
    "has_next": false
  }
  ```
  Un filtro sin coincidencias devuelve `"sales": []` con `200 OK` (RF-7
  se resuelve en el Frontend a partir de un arreglo vacío). [Cubre RF-1
  a RF-5, RF-7 a RF-10]
- **Respuesta esperada (error):** `422 Unprocessable Entity` —
  `{ "errors": [{ "field": "date_range", "message": "El rango de fechas
  es inválido" }] }` cuando `date_from` es posterior a `date_to`. [Cubre
  RF-6]
  También `422 Unprocessable Entity` (generado por FastAPI) si `page`
  no es un entero ≥ 1, o si `date_from`/`date_to` no tienen formato de
  fecha válido; no alcanzable desde la UI en uso normal.

### Vista: pestaña "Listar Ventas" (`VentasListado.jsx`)

- **Ruta/URL:** no aplica (SPA de una sola página con pestañas).
- **Propósito:** consultar el historial de ventas concretadas,
  filtrando por rango de fechas y/o por DNI de cliente. [Cubre HU-VEN-04]
- **Componentes/estados clave:**
  - Campos "Desde", "Hasta" (fecha) y "DNI del cliente" (texto).
  - Tabla de resultados: ID, Fecha, Cliente (nombre y DNI), Total.
  - Estado "sin resultados": mensaje en vez de tabla vacía. [Cubre RF-7]
  - Estado "rango inválido": mensaje a partir del 422 del backend.
    [Cubre RF-6]
  - Controles "Anterior" / "Siguiente", deshabilitados cuando no hay
    página previa o siguiente. [Cubre RF-9]
  - Al aplicar o modificar cualquier filtro, la página vuelve a 1.
    [Cubre RF-8, RF-9]

## 4. Decisiones Técnicas

1. **Decisión Tomada:** filtrar (fecha y DNI) y paginar en Python,
   dentro de `repository_venta.list_sales`, trayendo todas las ventas
   "Confirmada" (con su cliente, vía `JOIN`) y aplicando comparación de
   fechas y `core_venta.matches_dni` en memoria, en vez de traducir
   ambos filtros a `WHERE`/`LIKE`/`ORDER BY`/`LIMIT` de SQL.
   **Justificación:** mismo criterio ya validado en
   [[004-listar-clientes]] y [[008-listar-productos]]: para el volumen
   de datos esperado de este proyecto (regla 1 de la constitución), no
   se justifica optimizar con SQL nativo. Además, si el rango de fechas
   se resolviera en SQL y el DNI en Python (o viceversa), calcular
   `has_next` de forma correcta exigiría paginar dos veces (una en la
   base y otra en memoria), complicando la lógica sin necesidad real.
   Un único mecanismo de filtrado in-memory mantiene la paginación
   simple y consistente con el resto del proyecto.
   **Alternativa descartada:** combinar `WHERE sale_date BETWEEN ...` en
   SQL con el filtro de DNI en Python — descartada por la complejidad de
   paginación mixta mencionada arriba, sin una necesidad de rendimiento
   real que la justifique. *(RF-3, RF-4, RF-5, RF-9)*

2. **Decisión Tomada:** el listado usa una serialización liviana propia
   (`_serialize_sale_summary`: id, fecha, cliente, total), en vez de
   reutilizar `_serialize_sale` (ya existente, con items y estado).
   **Justificación:** `_serialize_sale` consulta los `SaleItem` de la
   venta y, por cada ítem, su `Product`, para poder mostrar el detalle
   completo. RF-10 no exige ese detalle en el listado, y reutilizar esa
   función dispararía consultas adicionales innecesarias por cada una de
   las 20 filas de la página. El campo `status` tampoco se expone,
   porque RF-2 ya garantiza que siempre vale `"Confirmada"` en este
   listado.
   **Alternativa descartada:** reutilizar `_serialize_sale` tal cual y
   simplemente ignorar `items`/`status` en el Frontend — descartada por
   el costo de consultas evitables en el Backend sin ningún beneficio.
   *(RF-10)*

3. **Decisión Tomada:** `list_sales` trae las ventas y sus clientes con
   una única consulta `session.query(Sale, Customer).join(Customer,
   Sale.customer_id == Customer.id)`, en vez de resolver el cliente de
   cada venta con una consulta separada (patrón `.filter_by(id=...)`
   usado en `_serialize_sale`).
   **Justificación:** el filtro de DNI (RF-4) necesita el DNI de
   **todas** las ventas "Confirmada" antes de paginar, no solo el de las
   20 de la página resultante; resolver el cliente venta por venta
   dispararía una consulta por cada venta del historial completo (N+1).
   Un `JOIN` trae todo en una sola consulta.
   **Alternativa descartada:** el patrón de consulta-por-fila ya usado
   en `_serialize_sale` — descartada porque aquí el N+1 ocurre sobre
   *todo* el historial (para poder filtrar), no solo sobre la página ya
   recortada. *(RF-4)*

4. **Decisión Tomada:** el rango de fechas compara solo la parte de
   fecha de `Sale.sale_date` (ignorando la hora), con ambos extremos
   inclusivos.
   **Justificación:** `sale_date` se registra con hora exacta
   ([[009-alta-venta]] RF-*), pero el Administrador filtra por día
   calendario (criterio de aceptación de la HU: "rango de fechas"). Si
   se comparara el datetime completo contra la medianoche de "hasta",
   una venta registrada a las 23:59 de ese mismo día quedaría excluida
   por error.
   **Alternativa descartada:** comparar el datetime completo —
   descartada por el caso límite recién descrito. *(RF-3)*

5. **Decisión Tomada:** `core_venta.py` es el primer módulo de reglas
   puras del dominio Venta; `is_valid_date_range` y `matches_dni` viven
   ahí, no en `core.py` (genérico) ni en `core_producto.py`.
   **Justificación:** sigue el patrón por dominio ya establecido desde
   [[005-alta-producto]] (decisión técnica 1 de ese plan) y reafirmado
   en [[008-listar-productos]] (decisión técnica 2): cada dominio tiene
   su propio núcleo de reglas, testeable sin base de datos ni HTTP.
   **Alternativa descartada:** agregar estas funciones a `core.py` como
   utilidades genéricas — descartada porque ambas reglas son específicas
   de cómo Venta interpreta un rango de fechas y un DNI, no utilidades
   reutilizables por otros dominios. *(RF-4, RF-6)*

6. **Decisión Tomada:** paginación con `page` + `has_next` (sin `total`
   ni `total_pages`), igual que [[004-listar-clientes]] y
   [[008-listar-productos]].
   **Justificación:** RF-9 solo pide navegación Anterior/Siguiente, no
   números de página ni conteo total.
   **Alternativa descartada:** devolver `total`/`total_pages` —
   descartada por anticipar un requisito no pedido. *(RF-9)*

7. **Decisión Tomada:** el filtro se dispara al enviar el formulario de
   búsqueda (submit), no en cada tecla ni al cambiar cada campo de
   fecha individualmente, mismo patrón que
   [[004-listar-clientes]]/[[008-listar-productos]].
   **Justificación:** consistencia de interacción entre los tres
   listados de la app, y evita disparar filtros con un rango de fechas
   a medio completar.
   **Alternativa descartada:** aplicar el filtro apenas cambia cualquier
   campo — descartada por no estar pedida y generar filtros parciales
   confusos mientras el Administrador todavía está completando el rango.
   *(RF-3, RF-4, RF-5)*

## 5. Estrategia de Tests

### Backend — tests unitarios (`core_venta.py`, sin base de datos)
- `is_valid_date_range`: `None`/`None` es válido; "desde" ≤ "hasta" es
  válido; "desde" > "hasta" es inválido. [Cubre RF-6]
- `matches_dni`: coincidencia parcial (ej. `"3011"` coincide con DNI
  `30111222`); un criterio que no aparece en el DNI no coincide; DNI
  vacío/sin filtro coincide siempre. [Cubre RF-4]

### Backend — tests de integración (`repository_venta.py`, SQLite temporal)
- `list_sales` sin filtros devuelve solo las ventas "Confirmada"
  (excluye una en "Borrador" y otra "Anulada"), ordenadas por fecha
  descendente. [Cubre RF-1, RF-2]
- `list_sales` con `date_from`/`date_to` devuelve solo las ventas dentro
  del rango, incluidos los extremos exactos; con un solo extremo,
  incluye todo hacia ese lado. [Cubre RF-3]
- `list_sales` con `dni` parcial devuelve solo las ventas de los
  clientes cuyo DNI coincide. [Cubre RF-4]
- `list_sales` con fecha y DNI a la vez devuelve solo la intersección.
  [Cubre RF-5]
- `list_sales` sin coincidencias devuelve una lista vacía. [Cubre RF-7]
- `list_sales` con más de 20 ventas "Confirmada" devuelve solo las
  primeras 20 y `has_next=True`; la página 2 devuelve el resto con
  `has_next=False`. [Cubre RF-9]

### Backend — tests de integración (`routes/ventas.py`, `TestClient`)
- `GET /ventas` sin filtros devuelve solo las ventas "Confirmada".
  [Cubre RF-1, RF-2]
- `GET /ventas?date_from=...&date_to=...` devuelve solo las ventas del
  rango. [Cubre RF-3]
- `GET /ventas?dni=...` devuelve solo las ventas del cliente
  correspondiente, con coincidencia parcial. [Cubre RF-4]
- `GET /ventas?date_from=...&dni=...` combinados devuelve la
  intersección. [Cubre RF-5]
- `GET /ventas?date_from=...&date_to=...` con "desde" posterior a
  "hasta" devuelve 422 con el mensaje de rango inválido. [Cubre RF-6]
- `GET /ventas?dni=...` sin coincidencias devuelve `"sales": []`. [Cubre
  RF-7]
- `GET /ventas?page=2` sobre más de 20 ventas "Confirmada" devuelve el
  resto y `has_next=False`. [Cubre RF-9]
- Cada venta devuelta incluye id, fecha, cliente y total, sin `items` ni
  `status`. [Cubre RF-10]

### Frontend — tests sobre `ventasApi.js` (fetch mockeado)
- `listarVentas`: traduce una llamada sin parámetros y una con
  `dni`/`dateFrom`/`dateTo`/`page`; propaga el error 422 de rango
  inválido. [Cubre RF-1, RF-3, RF-4, RF-6, RF-9]

### Frontend — Vitest + RTL sobre `VentasListado.jsx`
Con `listarVentas` mockeado:
- Al montar, se pide la página 1 sin filtros y se renderiza la tabla.
  [Cubre RF-1]
- Filtrar sin resultados muestra "no se encontraron resultados" en vez
  de una tabla vacía. [Cubre RF-7]
- Un rango de fechas inválido (422 del backend) muestra ese mensaje.
  [Cubre RF-6]
- Borrar los filtros vuelve a pedir la lista completa (sin `dni` ni
  fechas). [Cubre RF-8]
- Con `hasNext: true`, "Siguiente" pide la página 2; con `hasNext:
  false`, el botón está deshabilitado. [Cubre RF-9]
- Cambiar cualquier filtro estando en la página 2 vuelve a pedir la
  página 1. [Cubre RF-9]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas (se descartó
  explícitamente resolver el filtro en SQL nativo; ver decisión 1).
- **Regla 2 (spec antes que código):** parte de
  `specs/012-listar-ventas/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** `core_venta.py`
  concentra "qué es un rango válido" y "qué es una coincidencia de
  DNI", testeable sin HTTP ni React.
- **Regla 4 (tests obligatorios):** la estrategia cubre los diez RF de
  la spec.
- **Regla 5 (persistencia única):** `list_sales` lee exclusivamente de
  `database.py`/las tablas `sales` y `customers`.
- **Regla 6 (idioma consistente):** identificadores en inglés
  (`list_sales`, `is_valid_date_range`, `VentasListado.jsx`); mensajes
  en español ("No se encontraron resultados", "El rango de fechas es
  inválido").
