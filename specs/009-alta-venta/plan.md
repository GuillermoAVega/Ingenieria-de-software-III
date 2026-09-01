# Plan 009 — Registrar Alta de Venta

Plan técnico para implementar `specs/009-alta-venta/spec.md`, respetando
`docs/constitution.md`. Esta es la primera feature del dominio Venta y la
primera que cruza Cliente y Producto: reutiliza agresivamente lo ya
construido (`repository.find_by_dni`, `repository_producto.find_by_sku`,
los endpoints `GET /clientes/{dni}` y `GET /productos/{sku}`) en vez de
duplicar búsquedas ya resueltas. Este documento no contiene código:
describe estructura, decisiones y estrategia de verificación.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`models.py` (extendido)**: agrega `SaleStatus` (enum, hoy con un
  único valor `Confirmada`), `Sale` (tabla `sales`) y `SaleItem` (tabla
  `sale_items`), sin relaciones ORM (`relationship()`) — mismo estilo
  minimalista que `Customer`/`Product` (columnas FK planas, consultadas
  manualmente desde el repositorio). [Cubre RF-15]
- **`repository_venta.py` (nuevo)**: `create_sale(session, customer,
  items)`, la única función que escribe en `sales`/`sale_items` y
  descuenta stock. Toda la operación ocurre en una sola transacción
  (ver Decisión Técnica 4). [Cubre RF-13, RF-15]
- **`routes/ventas.py` (nuevo)**: `POST /ventas`. Orquesta: resuelve
  cliente por DNI y cada producto por SKU (reutilizando
  `repository.find_by_dni`/`repository_producto.find_by_sku` solo para
  resolver existencia, sin repetir las validaciones de estado/stock ya
  hechas en el Frontend — ver Decisión Técnica 2), valida formato de
  cantidad y que el detalle no esté vacío, arma la lista de errores
  combinados, y llama a `repository_venta.create_sale`. Reutiliza
  `core_producto.validate_positive_integer` para la cantidad (no se crea
  un `core_venta.py` para una sola función idéntica a una ya existente).
  [Cubre RF-1 a RF-17]
- **`main.py` (extendido)**: incluye el nuevo router de ventas.
  [Soporte, sin RF directo]

### Frontend (`app/frontend/`)

- **`ventaDetalle.js` (nuevo)**: módulo puro, la única lógica de negocio
  real de esta feature en el Frontend. `addItem(items, candidate)`
  consolida ítems repetidos por SKU (RF-10), valida que la cantidad sea
  un entero positivo (RF-8) y que no supere el stock disponible del
  producto (RF-9); `computeTotal(items)` calcula el total (RF-13). [Cubre
  RF-7 a RF-10, RF-13]
- **`api/ventasApi.js` (nuevo)**: `registrarVenta({ dni, items })` (`POST
  /ventas`). Reutiliza `buscarCliente` (de `clientesApi.js`) y
  `buscarProducto` (de `productosApi.js`), ya existentes, para las
  búsquedas de RF-1 y RF-4 — no se agregan funciones de búsqueda nuevas.
  [Cubre RF-1, RF-4, RF-15]
- **`components/VentaForm.jsx` (nuevo)**: búsqueda de cliente por DNI
  (bloquea si Inactivo o no encontrado) → búsqueda de producto por SKU +
  cantidad, agregado al detalle vía `ventaDetalle.addItem` (bloquea si
  Inactivo, no encontrado, cantidad inválida o sin stock) → tabla del
  detalle con subtotales y total → confirmación explícita → registro.
  [Cubre RF-1 a RF-17]
- **`App.jsx` (extendido)**: agrega la novena pestaña "Registrar Venta".
  [Soporte, sin RF directo]

## 2. Modelo de la Base de Datos

Dos tablas nuevas, sin modificar `customers` ni `products`:

| Tabla | Columna | Tipo | Notas |
|---|---|---|---|
| `sales` | `id` | Integer, PK, autoincrement | ID de venta asignado automáticamente (RF-15). |
| | `customer_id` | Integer, FK a `customers.id`, `nullable=False` | Resuelto a partir del DNI buscado (RF-1). |
| | `sale_date` | DateTime, `nullable=False` | Fecha y hora del sistema al confirmar (RF-15), no ingresada por el Administrador. |
| | `total` | Float, `nullable=False` | Calculado por `repository_venta.create_sale` (RF-13). |
| | `status` | Enum `SaleStatus`, `nullable=False` | Siempre `Confirmada` al crear (RF-15); único valor definido hoy (ver Decisión Técnica 6). |
| `sale_items` | `id` | Integer, PK, autoincrement | |
| | `sale_id` | Integer, FK a `sales.id`, `nullable=False` | |
| | `product_id` | Integer, FK a `products.id`, `nullable=False` | Resuelto a partir del SKU buscado (RF-4). |
| | `quantity` | Integer, `nullable=False` | Validado como entero positivo (RF-8). |
| | `unit_price` | Float, `nullable=False` | Copia congelada del precio del producto al agregarlo al detalle (RF-7); no se vuelve a leer del producto al confirmar (ver Decisión Técnica 2). |

No hace falta recrear `database.db`: son tablas nuevas, no se modifica el
esquema de `customers`/`products`.

## 3. Contrato de la Interfaz Web

### Endpoint: `POST /ventas`

- **Método y ruta:** `POST /ventas`
- **Payload de entrada:**
  ```json
  {
    "dni": "30111222",
    "items": [
      { "sku": "ABC123", "quantity": "2", "unit_price": "350.50" }
    ]
  }
  ```
  `unit_price` es el valor que el Frontend capturó al agregar el ítem al
  detalle (RF-7); el backend no lo recalcula. `items` ya viene
  consolidado por SKU (RF-10 es responsabilidad del Frontend; ver
  Decisión Técnica 3).
- **Respuesta esperada (éxito):** `201 Created`
  ```json
  {
    "sale": {
      "id": 1,
      "customer": { "dni": 30111222, "first_name": "Juan", "last_name": "Perez" },
      "sale_date": "2026-09-01T15:30:00",
      "items": [
        { "sku": "ABC123", "name": "Coca-Cola 500ml", "quantity": 2, "unit_price": 350.5, "subtotal": 701.0 }
      ],
      "total": 701.0,
      "status": "Confirmada"
    }
  }
  ```
  [Cubre RF-15]
- **Respuesta esperada (error):** `422 Unprocessable Entity`
  ```json
  {
    "errors": [
      { "field": "dni", "message": "Cliente no encontrado" },
      { "field": "items", "message": "La venta debe tener al menos un ítem" },
      { "field": "items[0].sku", "message": "Producto no encontrado" },
      { "field": "items[1].quantity", "message": "El valor debe ser un número positivo" }
    ]
  }
  ```
  Devuelve todas las advertencias del intento juntas (RF-12). `dni`
  inexistente y `sku` inexistente en algún ítem son los únicos casos que
  devuelven 422 por "no encontrado" (no hay 404, porque el payload
  siempre trae varios datos a la vez, a diferencia de los endpoints de
  búsqueda puntual). Cantidad inválida (RF-8) y detalle vacío (RF-11)
  también devuelven 422. **No** valida estado Activo del cliente/
  productos ni stock disponible en este paso (RF-16): si se envía el DNI
  de un cliente Inactivo o un SKU con stock insuficiente, la venta se
  registra igual. [Cubre RF-2, RF-5, RF-8, RF-11, RF-12, RF-16]

### Vista: pestaña "Registrar Venta" (`VentaForm.jsx`)

- **Ruta/URL:** no aplica (SPA de una sola página con pestañas).
- **Propósito:** armar el detalle de una venta para un cliente y
  registrarla, descontando el stock correspondiente. [Cubre HU-VEN-01]
- **Componentes/estados clave:**
  - Búsqueda de cliente por DNI (reutiliza `buscarCliente`); mensajes de
    "no encontrado" (RF-2) o "no se pueden emitir ventas a clientes
    dados de baja" (RF-3) cuando corresponda; solo con un cliente Activo
    seleccionado se habilita agregar ítems.
  - Búsqueda de producto por SKU + cantidad a agregar (reutiliza
    `buscarProducto`); mensajes de "no encontrado" (RF-5), "no está
    disponible para la venta" (RF-6, producto Inactivo), "debe ser un
    número positivo" (RF-8) o "no hay stock suficiente" (RF-9), según
    corresponda; usa `ventaDetalle.addItem` para agregar/consolidar
    (RF-10).
  - Tabla del detalle: SKU, Nombre, Cantidad, Precio unitario, Subtotal,
    con el Total al pie (RF-13).
  - Botón "Registrar venta" → diálogo de confirmación (RF-14) →
    Confirmar (llama a `registrarVenta`, muestra el mensaje de éxito y
    reinicia el formulario) / Cancelar (cierra el diálogo, no llama a la
    API, el detalle armado permanece intacto — RF-17).

## 4. Decisiones Técnicas

1. **Decisión Tomada:** `Sale`/`SaleItem` usan columnas FK planas
   (`customer_id`, `product_id`, `sale_id`), sin `relationship()` de
   SQLAlchemy; `repository_venta.py` hace los `JOIN`/consultas
   manualmente cuando hace falta.
   **Justificación:** consistente con el resto del proyecto — ni
   `Customer` ni `Product` usan relaciones ORM; introducirlas solo para
   Venta rompería el estilo ya establecido sin necesidad real.
   **Alternativa descartada:** `relationship()`/`backref` entre `Sale` y
   `SaleItem` — descartada por inconsistencia de estilo, no por un
   problema técnico real. *(RF-15)*

2. **Decisión Tomada:** `unit_price` de cada ítem se persiste tal como
   lo envía el Frontend (capturado al agregar el ítem al detalle, RF-7),
   sin volver a leerlo del producto en `POST /ventas`.
   **Justificación:** RF-16 exige explícitamente no re-verificar datos
   obtenidos al armar el detalle; si el precio del producto cambiara
   (vía [[007-modificacion-producto]]) entre que se agrega el ítem y se
   confirma la venta, el ítem ya vendido debe reflejar el precio
   acordado en ese momento, no uno recalculado.
   **Alternativa descartada:** recalcular `unit_price` desde
   `Product.unit_price` al confirmar — descartada porque contradice
   RF-16 y porque un histórico de ventas con precios que cambian
   retroactivamente sería incorrecto contablemente. *(RF-7, RF-16)*

3. **Decisión Tomada:** el backend **no** vuelve a consolidar ítems con
   el mismo SKU dentro de `POST /ventas`; confía en que el Frontend ya
   los consolidó (RF-10, en `ventaDetalle.js`). Si el payload trajera el
   mismo SKU en dos ítems separados (ej. una llamada directa a la API
   que bypasee el Frontend), se crean dos filas `SaleItem` independientes
   y el stock se descuenta dos veces por separado.
   **Justificación:** consistente con RF-16 (confiar en los datos
   armados durante la construcción del detalle) y con el resto de la
   feature, donde la validación de negocio vive en el Frontend y el
   backend resuelve existencia/persistencia.
   **Alternativa descartada:** consolidar también en el backend como
   defensa adicional — descartada por duplicar una regla que ya vive en
   `ventaDetalle.js`, y porque RF-16 ya acepta expresamente confiar en
   los datos del Frontend en esta operación. *(RF-10, RF-16)*

4. **Decisión Tomada:** `repository_venta.create_sale` aplica la
   creación de `Sale`, todas las filas `SaleItem` y el descuento de
   stock de cada producto dentro de una sola sesión, con un único
   `session.commit()` al final.
   **Justificación:** el requisito no funcional de consistencia exige
   que un error a mitad de camino no deje stock descontado sin la venta
   correspondiente; un solo `commit()` final logra esa atomicidad sin
   necesitar manejo de transacciones explícito adicional.
   **Alternativa descartada:** hacer un `commit()` por cada
   `SaleItem`/descuento de stock — descartada porque un fallo a mitad de
   camino dejaría cambios parciales persistidos, violando el NFR de
   consistencia. *(NFR de consistencia, RF-15)*

5. **Decisión Tomada:** reutilizar `GET /clientes/{dni}` y `GET
   /productos/{sku}` (ya existentes) para las búsquedas de RF-1 y RF-4
   en el Frontend, sin crear endpoints de búsqueda propios de Venta.
   **Justificación:** son exactamente las mismas búsquedas ya construidas
   para baja/edición de cliente y producto; duplicarlas no aportaría
   nada distinto.
   **Alternativa descartada:** endpoints de búsqueda específicos para
   Venta — descartados por ser copias idénticas de los ya existentes.
   *(RF-1, RF-4)*

6. **Decisión Tomada:** `SaleStatus` se define hoy con un único valor
   (`Confirmada`), sin agregar todavía un valor `Anulada` u otro estado
   que ninguna feature actual usa.
   **Justificación:** la baja/anulación de venta está explícitamente
   fuera de alcance de esta spec; agregar un valor sin RF que lo use
   sería diseñar para un requisito hipotético.
   **Alternativa descartada:** definir `SaleStatus` con `Confirmada` y
   `Anulada` desde ahora, anticipando la futura baja de venta —
   descartada por la regla del proyecto de no diseñar para hipotéticos;
   se agregará cuando exista esa spec, igual que pasó con
   `ClientStatus`/`ProductStatus` al construir la baja de cada dominio.
   *(RF-15)*

7. **Decisión Tomada:** los errores de un ítem específico del detalle se
   identifican con un `field` indexado (`items[N].sku`,
   `items[N].quantity`), primer caso en el proyecto de una lista dentro
   del payload de un formulario.
   **Justificación:** el resto de los endpoints tienen campos planos
   (nunca una lista), así que no hay un patrón previo que reutilizar;
   indexar por posición es la forma más directa de que el Frontend sepa
   a qué línea del detalle corresponde cada advertencia.
   **Alternativa descartada:** devolver un único mensaje de error
   genérico para todo el detalle sin indicar qué línea falló —
   descartada porque el Frontend necesita señalar el campo exacto,
   mismo principio que ya rige para los formularios planos de
   Cliente/Producto. *(RF-12)*

## 5. Estrategia de Tests

### Backend — tests de integración (`repository_venta.py`, SQLite temporal)
- `create_sale` persiste la venta con el total calculado (suma de
  cantidad × precio unitario de cada ítem) y el estado `Confirmada`.
  [Cubre RF-13, RF-15]
- `create_sale` crea una fila `SaleItem` por cada ítem, con el
  `unit_price` recibido (no el actual del producto). [Cubre RF-7]
- `create_sale` descuenta el stock de cada producto en la cantidad
  vendida. [Cubre RF-15]
- `create_sale` con dos ítems del mismo producto (sin consolidar) crea
  dos filas `SaleItem` y descuenta el stock dos veces — documenta la
  Decisión Técnica 3. [Cubre RF-16]

### Backend — tests de integración (`routes/ventas.py`, `TestClient`)
- Registro exitoso con uno y con varios ítems: 201, total correcto,
  stock descontado, cliente e ítems reflejados en la respuesta. [Cubre
  RF-1, RF-4, RF-13, RF-15]
- DNI inexistente: 422 con la advertencia correspondiente. [Cubre RF-2]
- SKU inexistente en un ítem: 422 con `field: "items[N].sku"`. [Cubre
  RF-5]
- Cantidad inválida (cero, negativa, decimal, no numérica) en un ítem:
  422 con `field: "items[N].quantity"`. [Cubre RF-8]
- Detalle vacío (`items: []`): 422 con la advertencia sobre `items`.
  [Cubre RF-11]
- Varios problemas a la vez (DNI inexistente + SKU inexistente en otro
  ítem): 422 con ambas advertencias juntas. [Cubre RF-12]
- Enviar el DNI de un cliente Inactivo directamente a `POST /ventas`: la
  venta se registra igual (200/201), sin advertencia de "cliente dado de
  baja" — documenta RF-16 sobre RF-3. [Cubre RF-16]
- Enviar el SKU de un producto Inactivo directamente: la venta se
  registra igual — documenta RF-16 sobre RF-6. [Cubre RF-16]
- Enviar una cantidad mayor al stock disponible directamente: la venta
  se registra igual (el stock puede quedar negativo) — documenta RF-16
  sobre RF-9, el riesgo aceptado explícitamente en la spec. [Cubre
  RF-16]

### Frontend — tests unitarios (`ventaDetalle.js`, sin React)
- `addItem` agrega un ítem nuevo válido.
- `addItem` consolida (suma cantidades) cuando el SKU ya está en el
  detalle. [Cubre RF-10]
- `addItem` rechaza cantidad no positiva/no entera. [Cubre RF-8]
- `addItem` rechaza cuando la cantidad (ya consolidada) supera el stock
  disponible. [Cubre RF-9]
- `computeTotal` suma cantidad × precio unitario de todos los ítems.
  [Cubre RF-13]

### Frontend — tests sobre `ventasApi.js` (fetch mockeado)
- `registrarVenta`: traduce una respuesta 201 y una 422 a la forma
  esperada. [Cubre RF-15]

### Frontend — Vitest + RTL sobre `VentaForm.jsx`
Con `buscarCliente`/`buscarProducto`/`registrarVenta` mockeados:
- Cliente no encontrado / Inactivo: mensaje correspondiente, no habilita
  agregar ítems. [Cubre RF-2, RF-3]
- Producto no encontrado / Inactivo / cantidad inválida / stock
  insuficiente al intentar agregarlo: mensaje correspondiente, no se
  agrega al detalle. [Cubre RF-5, RF-6, RF-8, RF-9]
- Agregar el mismo SKU dos veces consolida la línea en la tabla del
  detalle. [Cubre RF-10]
- La tabla muestra el total correcto a medida que se agregan ítems.
  [Cubre RF-13]
- "Registrar venta" muestra el diálogo de confirmación; Confirmar llama
  a `registrarVenta` y, ante éxito, muestra el mensaje y reinicia el
  formulario. [Cubre RF-14, RF-15]
- Cancelar la confirmación no llama a `registrarVenta` y conserva el
  detalle armado. [Cubre RF-17]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas.
- **Regla 2 (spec antes que código):** parte de
  `specs/009-alta-venta/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** `ventaDetalle.js`
  concentra toda la regla de negocio real del Frontend (consolidación,
  validación de stock, total), testeable sin React;
  `repository_venta.py` concentra la escritura transaccional, testeable
  sin HTTP.
- **Regla 4 (tests obligatorios):** la estrategia cubre los diecisiete
  RF de la spec, incluido el comportamiento aceptado de RF-16.
- **Regla 5 (persistencia única):** `create_sale` es la única vía de
  escritura de `sales`/`sale_items` y de descuento de stock, a través de
  `database.py`.
- **Regla 6 (idioma consistente):** identificadores en inglés (`Sale`,
  `SaleItem`, `create_sale`, `VentaForm.jsx`); mensajes al Administrador
  en español ("No se pueden emitir ventas a clientes dados de baja", "No
  hay stock suficiente para completar la operación").
