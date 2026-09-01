# Plan 018 — Mejoras sobre Venta y Cliente

Plan técnico para implementar `specs/018-mejoras-venta-cliente/spec.md`,
respetando `docs/constitution.md` y reutilizando lo ya construido para
Venta ([[009-alta-venta]], [[010-anular-venta]], [[011-modificacion-venta]],
[[012-listar-ventas]], [[016-selector-producto-venta]]) y para Cliente
([[003-modificacion-cliente]]). Este documento no contiene código:
describe estructura, decisiones y estrategia de verificación.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`repository_venta.py` (extendido)**: agrega
  `create_confirmed_sale(session, customer, items)`, que crea la venta
  ya en estado "Confirmada" —con su ID, fecha, cliente, ítems y total
  calculado— y descuenta el stock de cada producto en la misma
  transacción (un único `commit`), sin pasar por "Borrador". [Cubre
  RF-4]
- **`routes/ventas.py` (extendido)**: agrega `POST /ventas/confirmar`,
  distinto de `POST /ventas` (que sigue devolviendo "Borrador" sin
  cambios, RF-3). Reutiliza `_resolve_items` (ya existente) con
  `check_product_active=True, check_stock=True` —el mismo criterio que
  ya usa `PUT /ventas/{id}/detalle`— para revalidar cada ítem antes de
  crear nada. [Cubre RF-2, RF-4, RF-5, RF-6, casos límite de errores
  combinados]
  - `GET /ventas/{sale_id}` (ya existente, sin cambios de código): se
    reutiliza tal cual para alimentar el modal de detalle del listado.
    [Cubre RF-9, RF-10]
- **`routes/clientes.py`**: sin cambios. El guardado directo (RF-13) es
  un cambio de UI en el frontend; el endpoint `PUT /clientes/{dni}` ya
  devuelve éxito o errores de campo de la misma forma.
- **Esquema de base de datos**: sin cambios (ver sección 2).

### Frontend (`app/frontend/`)

- **`dateFormat.js` (nuevo)**: módulo de una sola función pura,
  `toDateOnly(isoDateTime)`, que recorta un datetime ISO (el que ya
  devuelve el backend en `sale_date`) a su parte de fecha
  (`"2026-09-01T14:23:11+00:00"` → `"2026-09-01"`), sin depender de
  React ni de la zona horaria del navegador. [Cubre RF-12]
- **`ventaDetalle.js` (sin cambios, reutilizado)**: ya expone
  `removeItem(items, sku)` y `computeTotal(items)`, usadas hoy por
  `VentaEdicionForm.jsx`. Se reutilizan tal cual en `VentaForm.jsx` para
  RF-1, sin duplicar lógica.
- **`ventaListado.js` (nuevo)**: análogo a `ventaEdicion.js` /
  `ventaAnulacion.js`. Expone `evaluateDetalleVenta(searchResult)`, que
  interpreta el resultado de `buscarVenta(id)` para el modal de detalle
  (`FOUND` con la venta, o `NOT_FOUND` con el mensaje "Venta no
  encontrada"). [Cubre RF-9, RF-10, caso límite de venta ya inexistente]
- **`api/ventasApi.js` (extendido)**: agrega `confirmarVenta(input)`
  (mismo shape de entrada que `registrarVenta`), que hace `POST
  /ventas/confirmar`. [Cubre RF-4 a RF-6, wiring]
- **`components/VentaForm.jsx` (modificado)**: agrega el botón "Quitar"
  por ítem del detalle (usa `removeItem`) [RF-1]; agrega una segunda
  acción "Confirmar venta" junto a "Registrar venta", cada una con su
  propio modal de confirmación y su propio mensaje de éxito/error [RF-2,
  RF-3, RF-4, RF-7, RF-8]; muestra los errores de stock insuficiente o
  producto inactivo que puede devolver `POST /ventas/confirmar` [RF-5,
  RF-6].
- **`components/VentasListado.jsx` (modificado)**: agrega una columna de
  acción con el ícono de ojo por fila [RF-9]; agrega un modal que, al
  abrirse, llama a `buscarVenta(id)` y renderiza el resultado de
  `evaluateDetalleVenta` (tabla de ítems, total, fecha, cliente, estado)
  [RF-10]; cerrar el modal no dispara ningún refetch de la lista de
  fondo, que sigue con su página y filtros intactos [RF-11]; aplica
  `toDateOnly` a la columna Fecha [RF-12].
- **`components/VentaAnulacionForm.jsx` (modificado)**: aplica
  `toDateOnly` a la columna Fecha de la tabla de ventas del cliente.
  [Cubre RF-12]
- **`components/VentaEdicionForm.jsx` (modificado)**: aplica
  `toDateOnly` a la columna Fecha de la tabla de ventas del cliente.
  [Cubre RF-12]
- **`components/ClienteEdicionForm.jsx` (modificado)**: elimina el
  estado `showConfirm` y el bloque de confirmación; el `handleSubmit`
  del formulario, tras pasar `validateClienteForm` sin errores, ejecuta
  directamente lo que hoy hace `handleConfirm` (llamar a `editarCliente`
  y procesar la respuesta). No se toca `validateClienteForm` ni
  `clienteEdicion.js`. [Cubre RF-13, RF-14]

## 2. Modelo de la Base de Datos

Sin cambios. Se reutilizan `Sale`, `SaleItem`, `Product` y `Customer`
tal como están definidos desde [[009-alta-venta]] y
[[001-alta-cliente]]:

- `Sale.status` ya admite el valor `"Confirmada"` (`SaleStatus.CONFIRMED`)
  que usa `create_confirmed_sale` (RF-4); no se agrega ningún estado
  nuevo.
- `Sale.sale_date` sigue siendo un `DateTime` completo (fecha y hora):
  RF-12 es un recorte de presentación en el frontend, no un cambio de
  columna ni de lo que se persiste.
- No se agrega ninguna tabla, columna ni índice nuevo.

## 3. Contrato de la Interfaz Web

### `POST /ventas/confirmar` (nuevo)

- **Payload de entrada**: idéntico al de `POST /ventas`:
  ```json
  { "dni": "30111222", "items": [{ "sku": "ABC123", "quantity": "2", "unit_price": "350.50" }] }
  ```
- **Respuesta exitosa**: `201 Created`
  ```json
  { "message": "Venta registrada y confirmada exitosamente", "sale": { "...": "...", "status": "Confirmada" } }
  ```
- **Respuesta de error**: `422 Unprocessable Entity`
  ```json
  { "errors": [{ "field": "items[0].quantity", "message": "No hay stock suficiente para completar la operación" }] }
  ```
  Mismos campos/mensajes de error ya usados por `POST /ventas` y `PUT
  /ventas/{id}/detalle` (cliente no encontrado, ítems vacíos, producto no
  encontrado, producto inactivo, cantidad inválida, stock insuficiente),
  pudiendo devolver más de uno a la vez.
- [Cubre RF-2, RF-4, RF-5, RF-6]

### `GET /ventas/{sale_id}` (sin cambios de código, reutilizado)

- Ya devuelve `200 OK` con `{ "sale": { id, customer, sale_date, items,
  total, status } }`, o `404 Not Found` con `{ "errors": [...] }` si no
  existe. El modal de detalle de RF-10 consume esta respuesta tal cual.
- [Cubre RF-9, RF-10]

### Vista `Registrar Venta` (`VentaForm.jsx`, extendida)

- **Ruta/URL**: `/ventas` (alta).
- **Propósito**: armar el detalle de una venta nueva y elegir si queda
  en Borrador o se confirma de inmediato.
- **Componentes/estados clave**: tabla de ítems con botón "Quitar" por
  fila (nuevo); dos botones de acción ("Registrar venta" / "Confirmar
  venta"), cada uno con su propio modal "¿Confirmás…?"; banner de éxito
  con el mensaje correspondiente a la acción elegida; banner de error
  reutilizado para stock insuficiente o producto inactivo al confirmar.
- [Cubre RF-1 a RF-8]

### Vista `Listar Ventas` (`VentasListado.jsx`, extendida)

- **Ruta/URL**: `/ventas` (listado).
- **Propósito**: además de filtrar y paginar (sin cambios,
  [[012-listar-ventas]]), permite ver el detalle completo de una venta
  puntual sin salir de la pantalla.
- **Componentes/estados clave**: columna de acción con ícono de ojo por
  fila; modal de detalle con estado de carga, tabla de ítems, total,
  fecha (formateada) y botón de cierre; columna Fecha ya existente ahora
  formateada a año-mes-día.
- [Cubre RF-9 a RF-12]

### Vistas `Anular Venta` y `Modificar Venta` (ajuste menor)

- **Ruta/URL**: `/ventas` (anulación) y `/ventas` (modificación).
- **Propósito**: sin cambios de flujo; solo la columna Fecha de sus
  tablas de ventas del cliente pasa a mostrarse en año-mes-día.
- [Cubre RF-12]

### Vista `Modificar Cliente` (`ClienteEdicionForm.jsx`, ajustada)

- **Ruta/URL**: `/clientes` (modificación).
- **Propósito**: sin cambios de flujo salvo que "Guardar cambios" ya no
  abre un modal intermedio.
- **Componentes/estados clave**: se elimina el bloque
  `cliente-edicion__confirm` (modal "¿Confirmás guardar estos
  cambios?"); el botón "Guardar cambios" pasa a mostrar "Guardando…" y
  ejecutar el guardado directamente.
- [Cubre RF-13, RF-14]

## 4. Decisiones Técnicas (Justificadas)

### Decisión: endpoint dedicado `POST /ventas/confirmar`, no un flag en `POST /ventas`
- **Justificación**: sigue el patrón ya establecido en el proyecto de un
  endpoint por acción de dominio (`/anular`, `/cerrar`, `/detalle`), en
  vez de mezclar dos comportamientos distintos (crear en Borrador vs.
  crear ya Confirmada) bajo el mismo endpoint con un campo oculto en el
  payload. Mantiene `POST /ventas` y sus tests actuales intactos (RF-3).
- **Alternativa descartada**: agregar `{"confirm": true}` al payload de
  `POST /ventas`. Se descartó por diluir la responsabilidad del
  endpoint existente y obligar a ramificar sus tests por un flag en vez
  de tener un endpoint con un solo comportamiento.

### Decisión: `create_confirmed_sale` hace un único commit, no encadena `create_sale` + `close_sale`
- **Justificación**: cumple la exigencia de atomicidad del NFR de esta
  spec: si algo falla, no debe quedar ni una venta huérfana en Borrador
  ni stock descontado sin venta. Encadenar las dos funciones existentes
  implicaría dos transacciones separadas.
- **Alternativa descartada**: reutilizar `create_sale` y luego
  `close_sale` en el mismo request. Se descartó porque si `close_sale`
  fallara después de que `create_sale` ya hizo `commit`, quedaría una
  venta en "Borrador" que el Administrador nunca pidió (pidió
  "Confirmar", no "Registrar").

### Decisión: revalidar stock y estado de producto solo en "Confirmar venta", no en "Registrar venta"
- **Justificación**: "Registrar venta" no cambia de comportamiento
  (RF-3) y sigue sin revalidar al momento de guardar, mismo criterio ya
  aceptado en [[009-alta-venta]] RF-16. "Confirmar venta" es, en
  esencia, el cierre de [[011-modificacion-venta]] fusionado con el
  alta: por eso reutiliza el mismo criterio de revalidación que ya usa
  `PUT /ventas/{id}/detalle` (`check_product_active=True,
  check_stock=True`), evitando vender stock negativo o un producto ya
  dado de baja en un paso irreversible.
- **Alternativa descartada**: no revalidar en "Confirmar venta" tampoco
  (mismo criterio que "Registrar"). Se descartó porque, a diferencia de
  "Registrar", esta acción sí descuenta stock de inmediato y de forma
  definitiva.

### Decisión: el detalle del modal (RF-10) reutiliza `GET /ventas/{sale_id}` sin endpoint nuevo
- **Justificación**: ese endpoint ya devuelve exactamente los datos que
  pide RF-10 (ítems con producto/cantidad/precio/subtotal, total, fecha,
  cliente, estado); no hace falta duplicar la serialización de
  `_serialize_sale`.
- **Alternativa descartada**: crear un endpoint de listado "con
  detalle" separado de `GET /ventas`. Innecesario y redundante con
  `GET /ventas/{sale_id}`, que ya existe desde [[010-anular-venta]].

### Decisión: el formato de fecha (RF-12) se resuelve en el frontend, sin tocar el backend
- **Justificación**: el dato persistido (datetime completo) sigue
  haciendo falta para el orden y los filtros de [[012-listar-ventas]]
  (su RF-3 compara por `sale.sale_date.date()`); cambiar el formato de
  salida del backend rompería esas comparaciones y el contrato ya usado
  por otras pantallas. Una función pura de formateo (`toDateOnly`)
  aplicada solo al renderizar mantiene el dato de origen intacto.
- **Alternativa descartada**: truncar `sale_date` a solo fecha en
  `_serialize_sale`/`_serialize_sale_summary` del backend. Se descartó
  por mezclar una decisión de presentación con el contrato de datos de
  la API.

### Decisión: eliminar el modal de `ClienteEdicionForm.jsx` moviendo la lógica de `handleConfirm` a `handleSubmit`
- **Justificación**: RF-13 es puramente de interacción (un paso de UI
  menos); la validación de campos (`validateClienteForm`) y las reglas
  de negocio del backend (DNI duplicado contra otro Activo, etc.) no
  cambian ni se tocan.
- **Alternativa descartada**: mantener el modal pero sin botón
  "Cancelar". No cumple el pedido explícito de eliminar el paso
  adicional (RF-13), solo lo disimula.

## 5. Estrategia de Tests

### Tests unitarios

- **Backend (`pytest`)**: `repository_venta.create_confirmed_sale` —
  crea la venta en estado "Confirmada", descuenta el stock de cada
  producto, y hace un único `commit` (se prueba que, si se simula una
  cantidad que ya no alcanza, no se llega a crear nada). [Cubre RF-4,
  RF-5]
- **Frontend (`Vitest`, sin renderizar)**:
  - `dateFormat.test.js`: `toDateOnly` sobre distintos strings ISO
    devueltos por el backend (con y sin microsegundos, con offset
    `+00:00` o `Z`), verificando que el resultado sea siempre
    `"YYYY-MM-DD"` sin hora. [Cubre RF-12]
  - `ventaListado.test.js`: `evaluateDetalleVenta` con un resultado
    exitoso (devuelve `FOUND` con la venta) y uno fallido (devuelve
    `NOT_FOUND` con el mensaje "Venta no encontrada"). [Cubre RF-9,
    RF-10, caso límite de venta inexistente]
  - `ventaDetalle.test.js` (ya existente): sin cambios; sus casos ya
    cubren `removeItem`, ahora también usado desde `VentaForm.jsx`.

### Tests de integración (backend, `pytest` + `TestClient`)

- `test_routes_ventas.py`, casos nuevos sobre `POST /ventas/confirmar`:
  - Éxito con uno y con varios ítems: la venta queda "Confirmada" y el
    stock de cada producto queda descontado. [Cubre RF-4]
  - Cliente no encontrado, ítems vacíos, producto no encontrado,
    cantidad inválida: mismos mensajes que `POST /ventas`. [Cubre RF-2]
  - Producto inactivo en el detalle: se rechaza y no se crea ninguna
    venta ni se descuenta stock de ningún ítem. [Cubre RF-6]
  - Cantidad de un ítem mayor al stock disponible: se rechaza y no se
    crea ninguna venta. [Cubre RF-5]
  - Dos problemas a la vez (ej. stock insuficiente en un ítem y
    producto inactivo en otro): se informan ambos en la misma
    respuesta, sin crear la venta. [Cubre caso límite de errores
    combinados]

### Tests E2E (Vitest + React Testing Library)

Con `ventasApi.js`/`clientesApi.js` mockeados (sin red real):

- **`VentaForm.jsx`**:
  - Armar el detalle con dos productos y quitar uno con "Quitar": el
    ítem desaparece de la tabla y el total se recalcula. [Cubre RF-1]
  - Elegir "Registrar venta": pide confirmación, llama a
    `registrarVenta` (sin cambios) y muestra su mensaje de éxito. [Cubre
    RF-3, RF-7]
  - Elegir "Confirmar venta": pide su propia confirmación, llama a
    `confirmarVenta` y muestra el mensaje de éxito correspondiente a
    una venta "Confirmada". [Cubre RF-2, RF-4, RF-7]
  - `confirmarVenta` devuelve error de stock insuficiente o de producto
    inactivo: se muestra el mensaje de error y no se limpia el
    formulario. [Cubre RF-5, RF-6]
  - Cancelar la confirmación de cualquiera de las dos acciones: no se
    invoca ninguna función de la API. [Cubre RF-8]
- **`VentasListado.jsx`**:
  - Click en el ícono de ver detalle de una fila: se llama a
    `buscarVenta(id)` y se muestra el modal con sus ítems, total y
    estado. [Cubre RF-9, RF-10]
  - Cerrar el modal: el listado de fondo conserva la página y los
    filtros aplicados antes de abrirlo. [Cubre RF-11]
  - La columna Fecha se muestra como año-mes-día. [Cubre RF-12]
- **`VentaAnulacionForm.jsx`** y **`VentaEdicionForm.jsx`**: la columna
  Fecha de la tabla de ventas del cliente se muestra como
  año-mes-día. [Cubre RF-12]
- **`ClienteEdicionForm.jsx`**:
  - Formulario válido: al tocar "Guardar cambios" se llama a
    `editarCliente` directamente, sin mostrar ningún modal de
    confirmación intermedio. [Cubre RF-13]
  - Formulario con errores de validación: "Guardar cambios" muestra los
    errores y no llama a `editarCliente`. [Cubre RF-14]
