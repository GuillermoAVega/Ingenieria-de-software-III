# Plan 019 — Correcciones sobre Cliente, Producto y Venta

Plan técnico para implementar `specs/019-correcciones-cliente-producto-venta/spec.md`,
respetando `docs/constitution.md` y reutilizando lo ya construido para
Cliente ([[003-modificacion-cliente]], [[004-listar-clientes]],
[[014-correcciones-cliente]]), Producto ([[005-alta-producto]]) y Venta
([[012-listar-ventas]], [[018-mejoras-venta-cliente]]). Este documento no
contiene código: describe estructura, decisiones y estrategia de
verificación.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`routes/clientes.py` (extendido)**:
  - `editar_cliente` (hoy `PUT /clientes/{dni}/editar`): agrega, luego
    de `find_by_dni` y antes de validar el payload, un chequeo de
    `customer.status`. Si es `ClientStatus.INACTIVE`, devuelve `422`
    con `CUSTOMER_INACTIVE_MESSAGE` (nueva constante) y no llama a
    `repository.update_customer`. [Cubre RF-2]
  - `listar_clientes` (`GET /clientes`): agrega el parámetro de query
    `field` (`"first_name" | "last_name" | "dni"`, default
    `"first_name"`). Se pasa junto con `q` y `page` a
    `repository.list_customers`. [Cubre RF-10, RF-11]
- **`repository.py` (extendido)**:
  - `list_customers(session, query, field, page, page_size=20)`: en
    vez de comparar `query` contra los tres campos a la vez
    (`core.matches_search`), usa una nueva función de `core` que
    compara solo contra el campo indicado. Si `query` es `None`/vacío,
    sigue devolviendo el listado completo sin filtrar (comportamiento
    de RF-1 y RF-14 sin cambios). [Cubre RF-11, RF-14, RF-15]
- **`core.py` (extendido)**:
  - `matches_search_field(normalized_query, field, *, dni, first_name, last_name)`:
    aplica `normalize_search_text` + coincidencia parcial (`in`) sobre
    el campo elegido únicamente; para `"dni"` compara contra `str(dni)`
    igual que hoy. Reemplaza el uso de `matches_search` desde
    `list_customers` (que puede quedar sin uso o eliminarse si ningún
    otro módulo la referencia). [Cubre RF-11, RF-12]
- **`routes/productos.py`**: sin cambios. RF-4/RF-5 son solo el texto
  de ayuda de un campo, que vive en el frontend.
- **`routes/ventas.py`**: sin cambios. `GET /ventas/{sale_id}` ya
  devuelve los datos que el modal necesita (reutilizado desde
  [[018-mejoras-venta-cliente]]).
- **Esquema de base de datos**: sin cambios (ver sección 2).

### Frontend (`app/frontend/`)

- **`clienteEdicion.js` (extendido)**: `evaluateEdicionBusqueda` agrega
  un tercer estado `INACTIVE` (además de `FOUND`/`NOT_FOUND`): si
  `searchResult.customer.status === "Inactivo"`, devuelve
  `{ state: "INACTIVE", message: INACTIVE_MESSAGE, customer }` en vez
  de `FOUND`. La función sigue sin depender de React. [Cubre RF-1]
- **`components/ClienteEdicionForm.jsx` (modificado)**: cuando
  `evaluateEdicionBusqueda` devuelve `INACTIVE`, muestra el mensaje y
  no llama a `setFormValues`/`setEditingDni`, por lo que el formulario
  precargado y el botón "Guardar cambios" no se renderizan. Si de
  todos modos llega un `422` de `editarCliente` con el motivo de
  cliente inactivo (defensa en profundidad, RF-2), lo muestra igual
  que cualquier otro error de campo ya manejado hoy. [Cubre RF-1, RF-2]
- **`productoFields.js` (modificado)**: cambia el `hint` de la entrada
  `sku` de `"Cualquier texto, sin espacios al inicio/fin"` a
  `"Identificador único del producto"`. Ningún otro campo de
  `PRODUCTO_FIELDS` ni la validación de `sku` se toca. [Cubre RF-4,
  RF-5]
- **`components/VentasListado.jsx` (modificado)**:
  - Reemplaza el contenido del botón de ver detalle (hoy el emoji
    `👁`) por un ícono SVG inline (`<svg>` de "ojo"), manteniendo el
    mismo `aria-label`. [Cubre RF-7]
  - Agrega un botón de cierre con ícono SVG de "X" dentro del modal,
    con `aria-label="Cerrar detalle"`, que llama a
    `handleCloseDetail` (ya existente). [Cubre RF-8]
  - No cambia la lógica de apertura/cierre (`handleViewDetail`,
    `handleCloseDetail`, `evaluateDetalleVenta`) ni el contenido del
    modal (tabla de ítems, total, fecha, cliente, estado), ya
    correctos desde [[018-mejoras-venta-cliente]]. [Cubre RF-6]
- **`components/VentasListado.css` (extendido)**: agrega las reglas
  que hoy faltan para `.ventas-listado__modal-backdrop` (`position:
  fixed`, cubre todo el viewport, fondo semitransparente oscuro,
  `z-index` por encima de la tabla, centra el contenido) y
  `.ventas-listado__modal` (tarjeta con fondo sólido, borde
  redondeado, ancho máximo, `max-height` con scroll interno). El
  backdrop, al ocupar todo el viewport y estar por encima en
  `z-index`, impide clicks sobre el listado de fondo mientras el modal
  está abierto. [Cubre RF-6, RF-9]
- **`components/ClienteListado.jsx` (modificado)**: reemplaza el único
  `<input>` de búsqueda por un `<select>` (`Nombre` / `Apellido` /
  `DNI`, valor por defecto `"first_name"`) más un `<input>` de texto
  para el valor. Dos estados nuevos: `fieldInput` (el `<select>`,
  cambia libremente sin disparar búsqueda — RF-13) y `appliedField`
  (se fija recién en `handleSearch`, junto con `appliedQuery`, igual
  patrón que ya existe para el texto). Pasa `field: appliedField` a
  `listarClientes`. [Cubre RF-10, RF-11, RF-13]
- **`api/clientesApi.js` (extendido)**: `listarClientes({ q, field,
  page })` agrega `field` como query param (`?field=...`) cuando está
  presente, junto a `q` y `page` ya existentes. [Cubre RF-10, RF-11,
  wiring]

## 2. Modelo de la Base de Datos

Sin cambios. Se reutilizan `Customer` (con `ClientStatus.ACTIVE` /
`ClientStatus.INACTIVE`), `Product` y `Sale`/`SaleItem` tal como están
definidos desde [[001-alta-cliente]], [[005-alta-producto]] y
[[009-alta-venta]]:

- No se agrega ninguna tabla, columna, índice ni valor de enum nuevo.
- RF-2 (bloqueo de edición) es una regla de la ruta, no un cambio de
  esquema: se apoya en la columna `Customer.status` que ya existe.
- RF-10/RF-11 (filtro por campo) es un cambio de cómo se arma la
  consulta en `repository.list_customers`, no de qué columnas existen
  en `customers`.

## 3. Contrato de la Interfaz Web

### `PUT /clientes/{dni}/editar` (modificado)

- **Payload de entrada**: sin cambios (`dni`, `first_name`,
  `last_name`, `email`, `phone`).
- **Respuesta esperada (Éxito)**: sin cambios — `200 OK` con
  `{ "message": EDICION_SUCCESS_MESSAGE, "customer": {...} }`, solo
  para clientes en estado Activo.
- **Respuesta esperada (Error, nueva)**: `422 Unprocessable Entity`
  con `{ "errors": [{ "field": "status", "message":
  "El cliente está inactivo y no puede modificarse" }] }` cuando el
  cliente encontrado por `dni` está Inactivo. No se modifica ningún
  dato. [Cubre RF-2]
- **Respuestas de error existentes** (404 no encontrado, 422 de
  formato o DNI en uso): sin cambios. [Cubre RF-3]

### `GET /clientes` (modificado)

- **Query params**: `q` (opcional, sin cambios), `page` (opcional, sin
  cambios), `field` (opcional, nuevo: `"first_name" | "last_name" |
  "dni"`, default `"first_name"` si se omite o llega vacío).
- **Respuesta esperada (Éxito)**: sin cambios de forma — `200 OK` con
  `{ "customers": [...], "page": N, "has_next": bool }` — pero
  `customers` ahora refleja coincidencias solo contra el campo pedido
  en `field` cuando hay `q`. Sin `q`, se ignora `field` y se devuelve
  el listado completo paginado (sin cambios respecto a
  [[004-listar-clientes]] RF-1). [Cubre RF-10, RF-11, RF-14]

### `GET /ventas/{sale_id}` — sin cambios de contrato

Reutilizado tal cual para alimentar el modal de detalle (ya usado
desde [[018-mejoras-venta-cliente]]). [Cubre RF-6]

### Vista `/clientes/editar` (Modificar Cliente)

- **Propósito**: buscar un cliente por DNI y editar sus datos.
- **Componentes/estados clave (cambio)**: tras la búsqueda, tres
  resultados posibles en vez de dos — `NOT_FOUND` (sin cambios),
  `INACTIVE` (nuevo: banner con el mensaje, sin formulario ni botón de
  guardar) y `FOUND` (sin cambios: formulario precargado, guardado
  directo). [Cubre RF-1, RF-3]

### Vista `/productos/nuevo` (Alta de Producto)

- **Propósito**: sin cambios.
- **Componentes/estados clave (cambio)**: el texto de ayuda bajo
  Código/SKU pasa a ser "Identificador único del producto". [Cubre
  RF-4]

### Vista `/ventas` (Listado de Ventas)

- **Propósito**: sin cambios.
- **Componentes/estados clave (cambio)**: la columna de acción muestra
  un ícono SVG (en vez de un emoji) que abre un modal con fondo
  superpuesto real (backdrop bloqueante) y un botón de cierre con
  ícono "X", además del botón "Cerrar" de texto ya existente. [Cubre
  RF-6, RF-7, RF-8, RF-9]

### Vista `/clientes` (Listado de Clientes)

- **Propósito**: sin cambios.
- **Componentes/estados clave (cambio)**: la barra de búsqueda pasa de
  un único input a un `<select>` de campo (Nombre/Apellido/DNI,
  default Nombre) más un input de valor; cambiar el `<select>` no
  dispara búsqueda por sí solo. [Cubre RF-10, RF-11, RF-13]

## 4. Decisiones Técnicas (Justificadas)

### Decisión: bloquear la edición tanto en el frontend (tras la búsqueda) como en el backend (al guardar)
- **Justificación**: RF-1 pide que la pantalla no muestre el
  formulario; RF-2 pide que la API rechace el guardado igual, sin
  depender de que la UI lo haya evitado (ej. otro cliente HTTP, o un
  cambio de estado concurrente entre la búsqueda y el guardado). Es el
  mismo criterio de "defensa en profundidad" que ya usa el proyecto
  para duplicados de DNI (validado en frontend y re-validado en el
  backend).
- **Alternativa descartada**: validar solo en el backend y dejar que
  el frontend muestre el formulario igual, mostrando el error recién
  al guardar. No cumple RF-1, que pide no mostrar el formulario ni el
  botón desde la búsqueda.

### Decisión: filtrar por campo en el backend (`repository.list_customers`), no en el frontend
- **Justificación**: la paginación de 20 (RF-15) ya se calcula sobre
  el resultado filtrado en el backend ([[004-listar-clientes]] RF-8);
  filtrar del lado del cliente rompería esa paginación (habría que
  traer todos los clientes para filtrar en el navegador). Mantiene
  además el principio de "lógica separada de la interfaz" de la
  constitución: la comparación de campos es lógica de negocio
  testeable sin renderizar UI.
- **Alternativa descartada**: mandar los tres campos ya filtrados por
  el frontend con `q` fijo y forzar el campo eligiendo qué columnas
  mirar client-side. Duplicaría la lógica de coincidencia parcial /
  insensible a tildes que ya vive en `core.py`.

### Decisión: no crear un componente `Modal` genérico reutilizable
- **Justificación**: la spec pide corregir el modal de detalle de
  venta puntualmente (RF-6 a RF-9); ya existe un solo modal en el
  proyecto (`VentasListado.jsx`). Extraer un componente genérico ahora
  sería una abstracción sin un segundo caso de uso real, contra la
  regla de no diseñar para requisitos hipotéticos.
- **Alternativa descartada**: crear `components/Modal.jsx` reutilizable
  desde ya. Se descarta hasta que exista un segundo modal real que lo
  justifique.

### Decisión: mantener `field` como parámetro de query separado de `q`, en vez de un mini-lenguaje tipo `q=nombre:ana`
- **Justificación**: dos parámetros simples (`field`, `q`) son
  triviales de validar y de mapear 1:1 desde el `<select>` +
  `<input>` del frontend (RF-10); no hay necesidad de parsear texto
  combinado en el backend.
- **Alternativa descartada**: un único string combinado. Añade
  parseo y casos de error (formato inválido) que RF-10/RF-11 no piden.

### Decisión: el ícono SVG de ver detalle y el de cierre se embeben inline en el JSX, no como archivos `.svg` importados
- **Justificación**: son íconos únicos de dos líneas, sin variantes;
  el proyecto no tiene hoy un pipeline de assets SVG (no hay carpeta
  `assets/icons` ni loader configurado en `vite.config`), y agregar
  uno para dos íconos sería sobre-ingeniería.
- **Alternativa descartada**: agregar una librería de íconos externa.
  El stack fijo de la constitución no incluye dependencias nuevas sin
  justificación, y dos íconos no la ameritan.

## 5. Estrategia de Tests

### Tests unitarios

- **Backend (`pytest`)**: `core.matches_search_field` — coincidencia
  parcial e insensible a mayúsculas/tildes contra `first_name`,
  contra `last_name`, y contra `dni` (numérico) por separado; un
  valor que coincide con `first_name` no matchea cuando `field` es
  `"last_name"` y viceversa. [Cubre RF-11, RF-12]
- **Frontend (`Vitest`, sin renderizar)**: `clienteEdicion.test.js` —
  `evaluateEdicionBusqueda` con un cliente Activo (devuelve `FOUND`),
  uno Inactivo (devuelve `INACTIVE` con el mensaje) y una búsqueda sin
  resultados (devuelve `NOT_FOUND`, sin cambios). [Cubre RF-1]

### Tests de integración (backend, `pytest` + `TestClient`)

- `test_routes_clientes.py`, casos nuevos:
  - `PUT /clientes/{dni}/editar` sobre un cliente Inactivo: devuelve
    `422` con el mensaje de cliente inactivo y no persiste ningún
    cambio (se vuelve a leer el cliente y sus datos siguen iguales).
    [Cubre RF-2]
  - `PUT /clientes/{dni}/editar` sobre un cliente Activo: sigue
    funcionando exactamente igual que hoy (no regresión). [Cubre RF-3]
  - `GET /clientes?field=first_name&q=...`: solo matchea por nombre,
    un cliente con ese apellido pero otro nombre no aparece. [Cubre
    RF-11]
  - `GET /clientes?field=last_name&q=...` y
    `GET /clientes?field=dni&q=...`: análogos para apellido y DNI
    (incluyendo DNI parcial). [Cubre RF-11, RF-12, caso límite de DNI
    parcial]
  - `GET /clientes` sin `field` ni `q`: devuelve el listado completo
    paginado, sin cambios de comportamiento. [Cubre RF-14, RF-15]

### Tests E2E (Vitest + React Testing Library)

Con `clientesApi.js`/`ventasApi.js`/`productosApi.js` mockeados (sin
red real), siguiendo el mismo patrón que
`tests/frontend/ClienteListado.test.jsx` y
`tests/frontend/VentasListado.test.jsx` (o equivalentes) ya existentes:

- **`ClienteEdicionForm.jsx`**:
  - Buscar un cliente Inactivo: se muestra el mensaje de cliente
    inactivo y no aparece el formulario precargado ni el botón
    "Guardar cambios". [Cubre RF-1]
  - Buscar un cliente Activo: comportamiento sin cambios (formulario
    precargado, guardado directo). [Cubre RF-3]
- **`ProductoForm.jsx`**: el texto de ayuda bajo el campo Código/SKU es
  "Identificador único del producto". [Cubre RF-4]
- **`VentasListado.jsx`**:
  - El botón de ver detalle no contiene el emoji `👁` como texto (se
    verifica por `aria-label` y la presencia de un `<svg>`). [Cubre
    RF-7]
  - Al hacer click, el modal se renderiza con la clase de backdrop
    (verificable por `role="dialog"` + contenedor superpuesto ya
    existente) y muestra los productos de la venta (sin cambios de
    contenido). [Cubre RF-6]
  - El botón de cierre con ícono "X" llama a la función que oculta el
    modal (el modal deja de estar en el DOM). [Cubre RF-8]
- **`ClienteListado.jsx`**:
  - El `<select>` de campo tiene "Nombre" seleccionado por defecto.
    [Cubre RF-10]
  - Elegir "Apellido" y escribir un valor, sin buscar todavía: no se
    llama a `listarClientes` de nuevo hasta presionar "Buscar" (se
    verifica que la última llamada mockeada sigue siendo la inicial).
    [Cubre RF-13]
  - Presionar "Buscar" con "DNI" elegido y un valor: `listarClientes`
    se llama con `field: "dni"` y ese valor. [Cubre RF-10, RF-11]
  - Presionar "Buscar" con el input de valor vacío: `listarClientes`
    se llama sin `q` (o con `q` vacío), mostrando el listado completo.
    [Cubre RF-14]
