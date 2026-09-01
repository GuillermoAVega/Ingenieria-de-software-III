# Plan 011 — Modificación de Venta

## 1. Estructura de Módulos

No se crean módulos nuevos a nivel de archivo; esta spec extiende los
módulos ya existentes del dominio Venta, más un módulo puro nuevo en el
frontend:

- **`app/backend/models.py`**: agrega el valor `DRAFT` al enum
  `SaleStatus` ya existente. [Cubre RF-1]
- **`app/backend/repository_venta.py`**:
  - Modifica `create_sale` para crear la venta en `SaleStatus.DRAFT` y
    dejar de descontar stock al registrar. [Cubre RF-1]
  - Agrega `replace_sale_items`: reemplaza el detalle completo de una
    venta en "Borrador", re-verificando su estado antes de aplicar el
    cambio. [Cubre RF-4, RF-5, RF-10, RF-11, RF-15]
  - Agrega `close_sale`: re-verifica estado "Borrador", ítems no vacíos
    y stock suficiente por ítem; si todo es válido, descuenta stock y
    cambia el estado a "Confirmada" en un único commit atómico. [Cubre
    RF-12, RF-13, RF-14, RF-16]
  - Modifica `cancel_sale` (de [[010-anular-venta]]) para que solo
    proceda si la venta está "Confirmada"; si está en "Borrador",
    devuelve un estado de error nuevo en vez de reponer stock que nunca
    se descontó. Ver "Decisiones Técnicas" — corrige una interacción no
    contemplada en 010, sin modificar sus archivos de spec.
- **`app/backend/routes/ventas.py`**:
  - Modifica la validación de `registrar_venta` para que ya no
    confirme ni descuente stock (delega el nuevo comportamiento a
    `create_sale`). [Cubre RF-1]
  - Agrega el endpoint `PUT /ventas/{sale_id}/detalle`, con las
    validaciones de producto activo, stock y cantidad positiva
    replicadas a nivel backend (a diferencia del alta original, ver
    "Decisiones Técnicas"). [Cubre RF-2 a RF-11]
  - Agrega el endpoint `PATCH /ventas/{sale_id}/cerrar`. [Cubre RF-12 a
    RF-14, RF-16]
  - El endpoint `GET /ventas/{sale_id}` ya existente (de
    [[010-anular-venta]]) se reutiliza sin cambios para la búsqueda por
    ID (RF-2, RF-3): ya serializa `status`, que ahora puede incluir
    `"Borrador"`.
  - Modifica `anular_venta` para reportar el nuevo caso "venta en
    Borrador" con un mensaje propio, en vez de tratarlo como éxito.
- **`app/frontend/ventaDetalle.js`**: agrega `removeItem(items, sku)`,
  función pura para quitar un ítem de la lista en edición; reutiliza
  `addItem`/`computeTotal` ya existentes (de [[009-alta-venta]]) tanto
  para el alta como para la edición. [Cubre RF-5, RF-8, RF-10]
- **`app/frontend/ventaEdicion.js`** (nuevo, análogo a
  `ventaAnulacion.js`): interpreta el resultado de la búsqueda de una
  venta para su edición, sin depender de React: `NOT_FOUND` /
  `NOT_DRAFT` / `EDITABLE`. [Cubre RF-2, RF-3, RF-4]
- **`app/frontend/api/ventasApi.js`**: agrega `reemplazarDetalleVenta(id, items)`
  y `cerrarVenta(id)`; actualiza el JSDoc de `Venta.status` para incluir
  `"Borrador"`. [Cubre RF-2, RF-5, RF-12]
- **`app/frontend/components/VentaEdicionForm.jsx` + `.css`** (nuevo):
  búsqueda por ID, mensajes de no encontrada / no editable, edición del
  detalle (agregar/quitar productos, reutilizando el mismo patrón de
  búsqueda por SKU de `VentaForm.jsx`), guardado del detalle y acción de
  cierre con confirmación. [Cubre RF-2 a RF-14, RF-16]
- **`app/frontend/App.jsx`**: agrega la pestaña "Modificar Venta".
  [Soporte - sin RF directo]

## 2. Modelo de la Base de Datos

No se agregan tablas ni columnas. Único cambio:

- **`SaleStatus`** (enum, en `models.py`): se agrega
  `DRAFT = "Borrador"`, quedando `DRAFT`, `CONFIRMED = "Confirmada"`,
  `CANCELLED = "Anulada"`. [Cubre RF-1]

`Sale` y `SaleItem` mantienen su esquema actual (ver
[[009-alta-venta]]): `replace_sale_items` reemplaza las filas de
`sale_items` asociadas a una `sale_id` (borra las anteriores, inserta
las nuevas) y recalcula `Sale.total`; no se elimina nunca la fila de
`Sale`. [Cubre RF-5, RF-10, RF-15]

## 3. Contrato de la Interfaz Web

### `POST /ventas` (modificado)
- **Payload de entrada:** sin cambios — `{ dni, items: [{ sku,
  quantity, unit_price }] }` (mismas validaciones de cliente y de ítems
  de [[009-alta-venta]]; se sigue exigiendo al menos un ítem para
  registrar, ver "Decisiones Técnicas").
- **Éxito:** `201 Created` — `{ message: "Venta registrada
  exitosamente", sale }`, con `sale.status === "Borrador"` y sin que se
  haya descontado stock de ningún producto.
- **Error:** `422 Unprocessable Entity` — `{ errors: [{ field, message
  }] }` (cliente no encontrado, producto no encontrado, cantidad
  inválida o detalle vacío).
- [Cubre RF-1]

### `GET /ventas/{sale_id}` (sin cambios de código, reutilizado)
- **Éxito:** `200 OK` — `{ sale }`, ahora con `sale.status` pudiendo ser
  `"Borrador"`, `"Confirmada"` o `"Anulada"`.
- **Error:** `404 Not Found` — `{ errors: [{ field: "id", message:
  "Venta no encontrada" }] }`.
- [Cubre RF-2, RF-3]

### `PUT /ventas/{sale_id}/detalle` (nuevo)
- **Payload de entrada:** `{ items: [{ sku: string, quantity: string,
  unit_price: string }] }` (mismo formato que `POST /ventas`; `items`
  puede ser `[]`).
- **Éxito:** `200 OK` — `{ message: "Detalle actualizado
  exitosamente", sale }`, con `sale.total` recalculado y
  `sale.status === "Borrador"`.
- **Error — venta no encontrada:** `404 Not Found` — `{ errors: [{
  field: "id", message: "Venta no encontrada" }] }`.
- **Error — venta no editable:** `422 Unprocessable Entity` — `{
  errors: [{ field: "id", message: "La venta ya no admite
  modificaciones" }] }` cuando `status !== "Borrador"`.
- **Error — validación de ítems:** `422 Unprocessable Entity` — `{
  errors: [{ field, message }, ...] }`, reportando **todos** los
  problemas del intento a la vez (producto inactivo, stock
  insuficiente, cantidad no positiva o producto inexistente); el
  detalle anterior no se modifica.
- [Cubre RF-4, RF-5, RF-6, RF-7, RF-8, RF-9, RF-10, RF-11, RF-15]

### `PATCH /ventas/{sale_id}/cerrar` (nuevo)
- **Payload de entrada:** ninguno.
- **Éxito:** `200 OK` — `{ message: "Venta cerrada exitosamente", sale
  }`, con `sale.status === "Confirmada"` y el stock de cada producto
  del detalle descontado.
- **Error — venta no encontrada:** `404 Not Found` — `{ errors: [{
  field: "id", message: "Venta no encontrada" }] }`.
- **Error — venta ya no está en Borrador:** `422 Unprocessable Entity`
  — `{ errors: [{ field: "id", message: "La venta ya no se encuentra en
  Borrador" }] }`.
- **Error — detalle vacío:** `422 Unprocessable Entity` — `{ errors: [{
  field: "items", message: "La venta debe tener al menos un ítem" }]
  }`.
- **Error — stock insuficiente:** `422 Unprocessable Entity` — `{
  errors: [{ field: "items", message: "No hay stock suficiente para
  completar la operación" }] }`; ningún producto se descuenta y el
  estado no cambia (verificación atómica de todo-o-nada, RF-16).
- [Cubre RF-12, RF-13, RF-14, RF-16]

### `PATCH /ventas/{sale_id}/anular` (ajuste de contrato existente)
- **Error nuevo — venta en Borrador:** `422 Unprocessable Entity` — `{
  errors: [{ field: "id", message: "No se puede anular una venta en
  Borrador" }] }`. No repone stock (nunca se descontó). Ver
  "Decisiones Técnicas".

### Vista `Registrar Venta` (`VentaForm.jsx`, sin cambios funcionales)
- **Ruta/URL:** pestaña "Registrar Venta" en `App.jsx`.
- **Propósito:** sin cambios de interacción; el mensaje de éxito puede
  aclarar que la venta queda en "Borrador" pendiente de cierre.
- [Cubre RF-1]

### Vista `Modificar Venta` (`VentaEdicionForm.jsx`, nueva)
- **Ruta/URL:** pestaña "Modificar Venta" en `App.jsx`.
- **Propósito:** permite al Administrador buscar una venta por ID,
  editar su detalle (agregar/quitar productos, ajustar cantidades) y
  cerrarla.
- **Componentes/estados clave:**
  - Input de ID + botón "Buscar".
  - Estado "no encontrada" (RF-3).
  - Estado "no editable" cuando la venta no está en "Borrador" (RF-4),
    mostrada en modo solo lectura.
  - Estado "editable": formulario de búsqueda de producto por SKU +
    cantidad (reutiliza el patrón de `VentaForm.jsx`), tabla de ítems
    con botón "Quitar" por fila, total recalculado en vivo, botón
    "Guardar cambios" (invoca `PUT /detalle`, muestra todos los errores
    juntos si los hay), y botón "Cerrar venta" con diálogo de
    confirmación (invoca `PATCH /cerrar`, mostrando el mensaje de éxito
    o de stock insuficiente/estado inválido según corresponda).
  - [Cubre RF-2 a RF-14, RF-16]

## 4. Decisiones Técnicas (Justificadas)

### Decisión: el alta (`POST /ventas`) sigue exigiendo al menos un ítem
- **Decisión tomada:** `POST /ventas` mantiene la validación de
  [[009-alta-venta]] que rechaza un detalle vacío; el permiso de
  detalle vacío de RF-11 aplica solo a `PUT /ventas/{id}/detalle`.
- **Justificación:** en la entrevista de esta spec se resolvió que el
  mecanismo de alta es "el mismo mecanismo" que en 009 (armar el
  carrito en el frontend y enviarlo de una vez), y el propio texto de
  RF-11 habla de "cada guardado intermedio", no del alta inicial. El
  frontend de alta (`VentaForm.jsx`) ya deshabilita "Registrar venta"
  con cero ítems, por lo que exigirlo también en el backend es
  consistente con el flujo ya aprobado.
- **Alternativa descartada:** permitir detalle vacío también en `POST
  /ventas`. Se descartó por contradecir la respuesta de la entrevista
  ("mismo mecanismo, aterriza en Borrador") y por no tener un caso de
  uso claro: una venta sin ningún ítem desde el alta no aporta valor
  frente a directamente abrir la pestaña de edición más tarde.

### Decisión: las validaciones de RF-6/RF-7/RF-8 se aplican en el backend, no solo en el frontend
- **Decisión tomada:** `PUT /ventas/{sale_id}/detalle` valida producto
  activo, stock disponible y cantidad positiva del lado del servidor,
  antes de reemplazar el detalle.
- **Justificación:** a diferencia de `POST /ventas` (que delega buena
  parte de estas validaciones al frontend, por ser un flujo de un solo
  paso guiado por la UI), esta spec edita un recurso ya persistido y
  puede invocarse repetidas veces; RF-6, RF-7 y RF-8 exigen
  explícitamente que el sistema (no solo la UI) rechace productos
  inactivos, stock insuficiente y cantidades inválidas. Confiar
  únicamente en el frontend dejaría el endpoint vulnerable a guardar
  datos inválidos si se lo invoca directamente.
- **Alternativa descartada:** replicar el criterio liviano de `POST
  /ventas` (validar solo en el frontend). Se descartó porque
  contradice directamente el texto de RF-6/RF-7/RF-8, que hablan del
  "sistema" como responsable de la advertencia y el bloqueo.

### Decisión: `close_sale` verifica todo antes de modificar cualquier cosa
- **Decisión tomada:** `close_sale` primero re-consulta el estado de la
  venta, luego valida que tenga al menos un ítem, luego valida el stock
  disponible de **todos** los ítems, y solo si las tres verificaciones
  pasan aplica los descuentos de stock y el cambio de estado, todo
  dentro de una única transacción con un `commit()` final.
- **Justificación:** RF-16 exige que un cierre rechazado no modifique
  ni el estado ni el stock de ningún producto ("todo o nada"). Verificar
  todos los ítems antes de aplicar cualquier descuento evita el caso en
  que el ítem 1 ya descontó stock y el ítem 2 falla, dejando la venta a
  medio cerrar. Mismo criterio de atomicidad que `create_sale`
  ([[009-alta-venta]]) y `cancel_sale` ([[010-anular-venta]]).
- **Alternativa descartada:** descontar stock ítem por ítem y revertir
  los ya aplicados si uno falla (compensación manual). Se descartó por
  ser más compleja y más frágil ante errores a mitad de camino que
  simplemente validar todo antes de mutar nada.

### Decisión: `cancel_sale` ([[010-anular-venta]]) se corrige para no operar sobre ventas en "Borrador"
- **Decisión tomada:** `cancel_sale` solo reproduce el flujo de
  reposición de stock + cambio a "Anulada" cuando la venta está
  "Confirmada"; si está en "Borrador", devuelve un nuevo estado de
  error (`"not_confirmed"` o similar) sin tocar stock ni estado, y la
  ruta `PATCH /ventas/{id}/anular` responde 422 con un mensaje
  distinto al de "ya anulada".
- **Justificación:** antes de esta spec, `SaleStatus` solo tenía
  "Confirmada" y "Anulada", por lo que `cancel_sale` asumía
  correctamente que cualquier venta no "Anulada" era "Confirmada" (y
  por lo tanto tenía stock descontado que reponer). Con "Borrador" como
  tercer estado, esa suposición deja de ser válida: una venta en
  Borrador nunca descontó stock, así que "anularla" con la lógica
  actual sumaría stock indebidamente. Esta spec no rediseña
  anular-venta, solo corrige una interacción que 010 no pudo prever
  porque el estado "Borrador" no existía; no se modifica ningún archivo
  de `specs/010-anular-venta/`. Descartar un borrador queda
  explícitamente fuera de alcance de esta spec ("Fuera de alcance"),
  por lo que bloquear la anulación de un Borrador (en vez de
  redefinirla como mecanismo de descarte) es la opción consistente con
  ese límite ya aprobado.
- **Alternativa descartada:** permitir que "anular" también sirva para
  descartar un Borrador (marcándolo "Anulada" sin tocar stock). Se
  descartó porque el propio `spec.md` de esta feature declara el
  descarte de un borrador "fuera de alcance... para una feature
  futura"; introducirlo por la puerta de atrás en `cancel_sale`
  contradiría esa decisión ya aprobada.

## 5. Estrategia de Tests

### Tests unitarios
- `ventaDetalle.js` — `removeItem`: quita el ítem correcto por SKU,
  no afecta a otros ítems, no falla si el SKU no está presente. [Cubre
  RF-5]
- `ventaEdicion.js` — `evaluateEdicionResult` (o nombre equivalente):
  cubre los tres estados `NOT_FOUND`, `NOT_DRAFT`, `EDITABLE` a partir
  de distintos resultados de búsqueda simulados. [Cubre RF-2, RF-3,
  RF-4]
- `ventasApi.js` — `reemplazarDetalleVenta` y `cerrarVenta` con `fetch`
  mockeado: casos 200, 404 y 422 para cada una. [Cubre RF-2, RF-4,
  RF-12, RF-14]

### Tests de integración (backend, `pytest`)
- `create_sale` crea la venta en `SaleStatus.DRAFT` y no descuenta
  stock de ningún producto del detalle. [Cubre RF-1]
- `replace_sale_items`: camino feliz (reemplaza items y recalcula
  total), venta inexistente, venta no "Borrador" (no modifica nada).
  [Cubre RF-4, RF-5, RF-10, RF-15]
- `close_sale`: camino feliz (cambia a Confirmada y descuenta stock de
  cada ítem), venta inexistente, venta no "Borrador", detalle vacío,
  stock insuficiente en algún ítem (verifica que NINGÚN producto quedó
  con stock descontado y que el estado sigue en "Borrador"). [Cubre
  RF-12, RF-13, RF-14, RF-16]
- `cancel_sale` sobre una venta en "Borrador": devuelve el nuevo estado
  de error, no repone stock (porque nunca se descontó) y no cambia el
  estado de la venta. [Corrige interacción con [[010-anular-venta]]]
- Endpoint `PUT /ventas/{id}/detalle`: camino feliz, venta inexistente
  (404), venta no editable (422), producto inactivo + stock
  insuficiente + cantidad inválida reportados juntos en un mismo
  intento (RF-9), detalle vacío permitido (RF-11). [Cubre RF-2 a RF-11,
  RF-15]
- Endpoint `PATCH /ventas/{id}/cerrar`: camino feliz, venta inexistente
  (404), venta ya no en Borrador (422), detalle vacío (422), stock
  insuficiente (422, sin descuentos parciales). [Cubre RF-12 a RF-14,
  RF-16]
- Endpoint `PATCH /ventas/{id}/anular` sobre una venta en "Borrador":
  responde 422 con el mensaje nuevo, sin modificar stock.

### Tests E2E (RTL, `VentaEdicionForm.jsx`)
- Buscar una venta inexistente muestra "Venta no encontrada" y no
  renderiza el editor. [Cubre RF-3]
- Buscar una venta "Confirmada" o "Anulada" muestra el mensaje de "ya no
  admite modificaciones" en modo solo lectura, sin controles de edición.
  [Cubre RF-4]
- Buscar una venta "Borrador" muestra su detalle editable: agregar un
  producto, quitar un producto, y ver el total recalcularse en vivo.
  [Cubre RF-5, RF-10]
- Guardar un detalle con un producto inactivo o sin stock suficiente
  muestra todas las advertencias correspondientes y no limpia la tabla
  de ítems previa. [Cubre RF-6, RF-7, RF-8, RF-9]
- Cerrar una venta con éxito muestra el mensaje de éxito y refleja el
  nuevo estado "Confirmada". [Cubre RF-12]
- Intentar cerrar una venta cuyo stock cambió (backend responde 422 de
  stock insuficiente) muestra ese mensaje en vez de asumir éxito.
  [Cubre RF-16]
