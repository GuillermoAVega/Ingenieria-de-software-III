# Plan 016 — Selector de Producto por Nombre o Descripción en Venta

Plan técnico para implementar `specs/016-selector-producto-venta/spec.md`,
respetando `docs/constitution.md`. Reutiliza el dominio Producto ya
construido en [[005-alta-producto]]/[[008-listar-productos]]
(`core_producto.py`, `repository_producto.py`, `routes/productos.py`),
sumando un mecanismo de búsqueda propio para Venta, sin modificar el ya
existente para Listar Productos.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`core_producto.py` (extendido)**: agrega `matches_venta_search`,
  función pura que decide si un producto coincide con un criterio ya
  normalizado, comparando contra Nombre y Descripción (a diferencia de
  `matches_search`, que compara Nombre y SKU para
  [[008-listar-productos]]). Vive junto a `matches_search` porque ambas
  son reglas del dominio Producto, pero son funciones separadas: cada
  una sirve a un caso de uso con campos distintos. [Cubre RF-1, RF-2]
- **`repository_producto.py` (extendido)**: agrega
  `search_for_venta(session, query, limit=20)`, que trae los productos
  **Activos** (excluyendo Inactivos a nivel de consulta), aplica
  `core_producto.matches_venta_search`, ordena por nombre y devuelve
  como máximo `limit` resultados, sin paginación. [Cubre RF-1, RF-2,
  RF-3, RF-6]
- **`routes/productos.py` (extendido)**: agrega
  `GET /productos/buscar-venta?q=<texto>`, declarada **antes** de
  `GET /productos/{sku}` en el archivo (ver Decisión Técnica 2), que
  llama a `search_for_venta` y devuelve SKU, Nombre, precio unitario y
  stock de cada resultado. [Cubre RF-1 a RF-6]

### Frontend (`app/frontend/`)

- **`api/productosApi.js` (extendido)**: agrega
  `buscarProductosParaVenta(q)`, que llama a
  `GET /productos/buscar-venta` y devuelve `{ products }`. [Cubre RF-1,
  RF-4, RF-6]
- **`components/VentaForm.jsx` (modificado)**: el campo de texto "SKU"
  se reemplaza por un campo "Producto" con búsqueda en vivo
  (debounce) y desplegable de resultados; al elegir una opción, se
  completan `sku`/`name`/`unitPrice`/`stock` en el estado del
  componente sin otra llamada al servidor; "Agregar" pasa a usar esos
  datos ya conocidos en vez de volver a resolver el producto por SKU.
  [Cubre RF-1, RF-4, RF-5, RF-7, RF-8]
- **`components/VentaEdicionForm.jsx` (modificado)**: mismo cambio que
  en `VentaForm.jsx`, aplicado al formulario de "agregar ítem" dentro
  de la edición del detalle. [Cubre RF-1, RF-4, RF-5, RF-7, RF-8]

No se toca `ventaDetalle.js`: `addItem`/`validateQuantityFormat` ya
reciben los datos del producto como parámetros (no vuelven a buscarlo),
por lo que siguen funcionando igual una vez que el producto llega
seleccionado desde el desplegable.

## 2. Modelo de la Base de Datos
No se agregan tablas ni columnas nuevas. Esta feature es de solo
lectura sobre `products`, ya definida desde [[005-alta-producto]]:

| Columna | Uso en esta feature |
|---|---|
| `name` | Se compara normalizado contra el criterio de búsqueda. [Cubre RF-1, RF-2] |
| `description` | Se compara normalizado contra el criterio de búsqueda (a diferencia de [[008-listar-productos]], que no la usa). [Cubre RF-1, RF-2] |
| `sku`, `unit_price`, `stock` | Se devuelven en cada resultado para completar el ítem automáticamente (RF-4); no participan del filtro de esta búsqueda. |
| `status` | Se usa para excluir productos Inactivos de los resultados (RF-3); no se expone en la respuesta. |

## 3. Contrato de la Interfaz Web

### Endpoint: `GET /productos/buscar-venta`

- **Método y ruta:** `GET /productos/buscar-venta?q=<texto>`
- **Payload de entrada:** query param `q` (string, requerido para
  obtener resultados; con `q` vacío o ausente se devuelve una lista
  vacía sin consultar la base).
- **Respuesta esperada (éxito):** `200 OK`
  ```json
  {
    "products": [
      { "sku": "ABC123", "name": "Coca-Cola 500ml", "unit_price": 350.5, "stock": 100 }
    ]
  }
  ```
  Un `q` sin coincidencias devuelve `"products": []` con `200 OK`
  (RF-6 se resuelve en el Frontend a partir de un arreglo vacío).
  [Cubre RF-1 a RF-6]
- **Respuesta esperada (error):** no aplica; no hay entrada inválida
  posible más allá de un `q` vacío, que ya se resuelve como lista
  vacía.

### Vista "Registrar Venta" (`VentaForm.jsx`, flujo modificado)
- **Propósito:** sin cambios (HU-VEN-01); cambia cómo se elige el
  producto de cada ítem.
- **Componentes/estados clave:**
  - Campo "Producto" (reemplaza a "SKU"): input de texto libre +
    desplegable de resultados debajo, mientras no haya un producto
    elegido.
  - Estado "sin resultados": mensaje en el desplegable en vez de una
    lista vacía. [Cubre RF-6]
  - Al elegir una opción, el desplegable se cierra y el campo muestra
    el producto elegido (ej. su nombre); el campo "Cantidad" y el
    botón "Agregar" siguen igual que hoy. [Cubre RF-4, RF-8]
  - Editar el texto después de haber elegido un producto vuelve a
    abrir la búsqueda y descarta la selección anterior. [Cubre RF-7]

### Vista "Modificar Venta" (`VentaEdicionForm.jsx`, flujo modificado)
- Mismo comportamiento que `VentaForm.jsx`, aplicado al formulario de
  "agregar ítem" dentro de la edición del detalle de una venta en
  Borrador. [Cubre RF-1, RF-4, RF-5, RF-7, RF-8]

## 4. Decisiones Técnicas

1. **Decisión Tomada:** la búsqueda se dispara mientras el
   Administrador escribe (con un debounce corto, ej. 300ms), no al
   enviar un formulario ni al presionar un botón "Buscar".
   **Justificación:** es exactamente el mecanismo pedido y confirmado
   en la entrevista ("autocompletar con desplegable"); a diferencia de
   los listados de Cliente/Producto/Venta (que buscan al enviar,
   decisión ya validada en [[008-listar-productos]] para listas
   completas paginadas), acá se trata de un selector de una sola
   elección dentro de un formulario más grande, donde esperar un envío
   explícito sería más lento para el caso de uso pedido.
   **Alternativa descartada:** mantener el disparo por submit/botón,
   igual que los listados — descartada porque el pedido explícito fue
   un autocompletar en vivo, no un listado a demanda. *(RF-1)*

2. **Decisión Tomada:** `GET /productos/buscar-venta` se declara en
   `routes/productos.py` **antes** que `GET /productos/{sku}`.
   **Justificación:** FastAPI/Starlette resuelven las rutas en el
   orden en que se registran; si `/productos/{sku}` se declarara
   primero, capturaría cualquier request a `/productos/buscar-venta`
   interpretando `"buscar-venta"` como el valor de `sku`, impidiendo
   que la ruta nueva se alcance nunca.
   **Alternativa descartada:** ninguna real — es un requisito técnico
   de FastAPI, no una decisión de diseño con alternativas razonables.
   *(RF-1)*

3. **Decisión Tomada:** `search_for_venta` no pagina; devuelve como
   máximo `limit` (20) resultados directamente.
   **Justificación:** RF-1 y "Fuera de alcance" de la spec descartan
   explícitamente una paginación tipo Anterior/Siguiente para este
   desplegable; un límite fijo alcanza para un selector de
   autocompletar, donde se espera que el Administrador afine el
   criterio si no ve lo que busca entre las primeras coincidencias.
   **Alternativa descartada:** reutilizar el mismo esquema
   `page`/`has_next` que [[008-listar-productos]] — descartada por no
   tener sentido una navegación de páginas dentro de un desplegable de
   autocompletar. *(RF-1, RF-6)*

4. **Decisión Tomada:** al seleccionar una opción del desplegable, el
   Frontend guarda el `sku`/`name`/`unit_price`/`stock` ya devueltos
   por `buscarProductosParaVenta`, y "Agregar" los usa directamente,
   sin volver a llamar a `buscarProducto(sku)` como hace hoy el código
   antes de esta spec.
   **Justificación:** el resultado de la búsqueda ya trae todo lo
   necesario para armar el ítem (RF-4); pedirlo de nuevo sería una
   llamada redundante. La posible obsolescencia del stock entre la
   búsqueda y el "Agregar" no es un riesgo nuevo: el Backend ya
   revalida el stock al guardar el detalle
   ([[011-modificacion-venta]]) y al cerrar la venta
   ([[011-modificacion-venta]] RF-16), igual que hoy.
   **Alternativa descartada:** volver a llamar a `buscarProducto(sku)`
   al presionar "Agregar" para tener el dato más fresco posible —
   descartada por ser una llamada extra sin beneficio real, dado que
   la validación de autoridad final ya ocurre en el Backend al guardar.
   *(RF-4, RF-8)*

5. **Decisión Tomada:** cambiar el texto del campo "Producto" después
   de haber elegido una opción borra la selección guardada
   (`sku`/`name`/`unitPrice`/`stock` vuelven a `null`) y vuelve a
   habilitar la búsqueda en vivo sobre el nuevo texto.
   **Justificación:** es exactamente RF-7; evita que "Agregar" use por
   error los datos de un producto ya elegido si el Administrador
   decidió buscar otro sin haber completado una nueva elección.
   **Alternativa descartada:** conservar la selección anterior hasta
   que se elija una nueva opción del desplegable — descartada porque
   contradice RF-7 explícitamente (el pedido es que cambiar el texto
   descarte la selección previa). *(RF-7)*

6. **Decisión Tomada:** las opciones del desplegable se seleccionan
   con el evento `onMouseDown` (no `onClick`) sobre cada resultado.
   **Justificación:** el campo de texto pierde el foco (`onBlur`)
   antes de que se dispare un `onClick` en el elemento clickeado; si el
   cierre del desplegable ocurriera en el `onBlur` sin este ajuste, la
   opción desaparecería del DOM antes de que el clic llegara a
   registrarse. Usar `onMouseDown` (que ocurre antes que `onBlur`)
   evita esa carrera, un patrón estándar de implementación de
   autocompletar.
   **Alternativa descartada:** cerrar el desplegable con un `setTimeout`
   corto en el `onBlur` — descartada por ser más frágil (depende de un
   tiempo arbitrario) que resolver el orden real de los eventos del
   navegador. *(RF-4)*

7. **Decisión Tomada:** no se crea un hook compartido entre
   `VentaForm.jsx` y `VentaEdicionForm.jsx` para este selector; cada
   componente implementa su propio estado y manejadores, siguiendo el
   mismo criterio ya aplicado en
   [[013-validacion-amigable-formularios]] (decisión técnica 4: no
   extraer un hook para lógica casi idéntica duplicada en varios
   formularios).
   **Justificación:** consistencia con el estilo ya establecido en el
   proyecto.
   **Alternativa descartada:** un hook `useProductoSelector` reutilizable
   — descartada por la misma razón ya documentada en 013: sería una
   abstracción nueva sobre un patrón que el proyecto deliberadamente
   mantiene duplicado. *(RF-1, RF-4, RF-7)*

## 5. Estrategia de Tests

### Backend — tests unitarios (`core_producto.py`, sin base de datos)
- `matches_venta_search`: coincidencia parcial por nombre; coincidencia
  parcial por descripción; insensible a mayúsculas/tildes; un producto
  sin descripción (`None`) no rompe la comparación; un criterio que no
  aparece en ningún campo no coincide. [Cubre RF-1, RF-2]

### Backend — tests de integración (`repository_producto.py`, SQLite temporal)
- `search_for_venta` excluye productos Inactivos aunque coincidan.
  [Cubre RF-3]
- `search_for_venta` con un `query` que coincide por nombre o por
  descripción devuelve solo esos productos, ordenados por nombre.
  [Cubre RF-1, RF-2]
- `search_for_venta` con más de `limit` coincidencias devuelve como
  máximo `limit` resultados, sin paginar. [Cubre RF-1]
- `search_for_venta` sin `query` (vacío) devuelve una lista vacía sin
  consultar coincidencias. [Cubre RF-6]

### Backend — tests de integración (`routes/productos.py`, `TestClient`)
- `GET /productos/buscar-venta?q=...` devuelve solo productos Activos
  que coinciden por nombre o descripción, con SKU/nombre/precio/stock
  en cada resultado. [Cubre RF-1 a RF-5]
- `GET /productos/buscar-venta?q=...` sin coincidencias devuelve
  `"products": []`. [Cubre RF-6]
- `GET /productos/{sku}` (ya existente) sigue funcionando para un SKU
  real después de agregar la ruta nueva (verifica que el orden de
  declaración no rompió la ruta existente). [Soporte - sin RF directo]

### Frontend — tests sobre `productosApi.js` (fetch mockeado)
- `buscarProductosParaVenta`: traduce la llamada con `q` y devuelve
  `{ products }`. [Cubre RF-1]

### Frontend — Vitest + RTL sobre `VentaForm.jsx` y `VentaEdicionForm.jsx`
Con `buscarProductosParaVenta` mockeado:
- Escribir un criterio muestra las opciones devueltas (Nombre y SKU de
  cada una). [Cubre RF-1, RF-5]
- Un criterio sin coincidencias muestra el mensaje de "no se
  encontraron productos". [Cubre RF-6]
- Elegir una opción completa el ítem (sku/nombre/precio/stock) sin una
  segunda llamada a `buscarProducto`. [Cubre RF-4]
- Cambiar el texto después de elegir una opción impide agregar el
  ítem hasta elegir una nueva (botón "Agregar" deshabilitado). [Cubre
  RF-7]
- El resto del flujo (cantidad inválida, stock insuficiente,
  consolidación de ítems repetidos) sigue funcionando igual que antes.
  [Cubre RF-8]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas (el debounce se
  implementa con `setTimeout`/`clearTimeout` nativos, sin librerías).
- **Regla 2 (spec antes que código):** parte de
  `specs/016-selector-producto-venta/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** `matches_venta_search`
  y `search_for_venta` concentran las reglas de negocio, testeables sin
  HTTP ni React.
- **Regla 4 (tests obligatorios):** la estrategia cubre las 8 RF de la
  spec.
- **Regla 5 (persistencia única):** `search_for_venta` lee
  exclusivamente de `database.py`/la tabla `products`.
- **Regla 6 (idioma consistente):** identificadores en inglés
  (`matches_venta_search`, `search_for_venta`,
  `buscarProductosParaVenta`); mensajes en español ("No se encontraron
  productos").
