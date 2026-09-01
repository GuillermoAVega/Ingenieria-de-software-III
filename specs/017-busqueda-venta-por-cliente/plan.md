# Plan 017 — Búsqueda de Venta por Cliente en Anular y Modificar Venta

Plan técnico para implementar `specs/017-busqueda-venta-por-cliente/spec.md`,
respetando `docs/constitution.md`. Agrega un mecanismo de búsqueda propio
(ventas de un cliente por DNI, todos los estados), reutilizado por
Anular Venta ([[010-anular-venta]]) y Modificar Venta
([[011-modificacion-venta]]), sin modificar [[012-listar-ventas]] ni las
reglas de negocio de anular/cerrar ya construidas.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`repository_venta.py` (extendido)**: agrega
  `find_sales_by_customer_dni(session, dni)`, que:
  1. Normaliza el DNI (`core.try_normalize_dni`); si no es numérico,
     se trata como cliente no encontrado.
  2. Busca **todos** los registros de `Customer` con ese DNI (puede
     haber más de uno: un Activo y uno o más Inactivos, posible desde
     [[014-correcciones-cliente]]). Si no hay ninguno, devuelve
     `(False, [])`.
  3. Trae las ventas cuyo `customer_id` pertenezca a cualquiera de esos
     clientes, ordenadas por `sale_date` descendente, sin filtrar por
     estado. Devuelve `(True, sales)`.
  [Cubre RF-1, RF-2, RF-6, RF-11]

### Frontend (`app/frontend/`)

- **`api/ventasApi.js` (extendido)**: agrega `buscarVentasDeCliente(dni)`,
  que llama al endpoint nuevo y devuelve `{ success: true, sales }` o
  `{ success: false, errors }`. [Cubre RF-1, RF-2]
- **`ventaAnulacion.js` (extendido)**: agrega
  `evaluateClienteSalesParaAnular(result)`, función pura que interpreta
  el resultado de `buscarVentasDeCliente` filtrando a las ventas
  "Confirmada": `CLIENT_NOT_FOUND` / `NO_CONFIRMED_SALES` /
  `SALES_LIST`. La lógica ya existente (`evaluateAnulacionResult`,
  sobre una venta puntual) se elimina: ya no se busca una venta por ID
  en esta pantalla. [Cubre RF-2, RF-3, RF-4]
- **`ventaEdicion.js` (extendido)**: agrega
  `evaluateClienteSalesParaModificar(result)`, función pura que
  interpreta el mismo resultado sin filtrar por estado:
  `CLIENT_NOT_FOUND` / `NO_SALES` / `SALES_LIST` (cada venta de la
  lista conserva su `status`, para que la vista decida en cuáles
  habilitar el ícono de editar). `evaluateEdicionResult` (sobre una
  venta puntual) se conserva tal cual: se reutiliza para el paso
  "presionar el ícono de editar" (RF-9, RF-10). [Cubre RF-2, RF-6, RF-7,
  RF-8]
- **`components/VentaAnulacionForm.jsx` (modificado)**: el campo "ID de
  la venta" se reemplaza por "DNI del cliente"; tras buscar, se muestra
  la lista de ventas Confirmada (o el mensaje correspondiente); cada
  fila tiene un botón "Anular" que abre el diálogo de confirmación ya
  existente, ahora sobre la venta elegida de la lista en vez de sobre
  el resultado de una búsqueda puntual. [Cubre RF-1 a RF-5, RF-11]
- **`components/VentaEdicionForm.jsx` (modificado)**: el campo "ID de la
  venta" se reemplaza por "DNI del cliente"; tras buscar, se muestra la
  lista completa de ventas del cliente con su estado; cada fila en
  "Borrador" tiene un ícono de editar que dispara `buscarVenta(id)` (ya
  existente) + `evaluateEdicionResult` (ya existente) antes de mostrar
  la vista de edición ya construida en [[011-modificacion-venta]] y
  [[016-selector-producto-venta]], que no cambia. [Cubre RF-1, RF-2,
  RF-6 a RF-11]

No se toca `routes/ventas.py`'s `GET /ventas` (listado de
[[012-listar-ventas]]), `PATCH /ventas/{id}/anular`,
`PUT /ventas/{id}/detalle`, `PATCH /ventas/{id}/cerrar`, ni
`GET /ventas/{id}`: esta spec solo agrega un endpoint nuevo para llegar
a elegir la venta, reutilizando todo lo que ya opera sobre una venta
puntual.

## 2. Modelo de la Base de Datos
No se agregan tablas ni columnas nuevas. Se lee de `sales` y
`customers`, ya definidas desde [[009-alta-venta]]/[[001-alta-cliente]]:

| Columna | Uso en esta feature |
|---|---|
| `customers.dni` | Se compara por valor exacto (normalizado) contra el DNI buscado; puede haber más de un `Customer` con el mismo valor (RF-1, ver Decisión Técnica 1). |
| `sales.customer_id` | Se filtra contra **todos** los `id` de clientes con ese DNI, no solo uno. [Cubre RF-1] |
| `sales.status` | No se filtra en el backend (a diferencia de [[012-listar-ventas]]); se expone en la respuesta para que cada pantalla decida qué mostrar/habilitar (RF-3, RF-6, RF-8). |
| `sales.sale_date` | Determina el orden del resultado (RF-11). |

## 3. Contrato de la Interfaz Web

### Endpoint: `GET /ventas/cliente/{dni}`

- **Método y ruta:** `GET /ventas/cliente/{dni}`
- **Payload de entrada:** `dni` en la ruta (string).
- **Respuesta esperada (éxito):** `200 OK`
  ```json
  {
    "sales": [
      { "id": 3, "sale_date": "2026-03-01T10:00:00+00:00", "status": "Borrador", "total": 400.0 },
      { "id": 1, "sale_date": "2026-01-15T10:00:00+00:00", "status": "Confirmada", "total": 701.0 }
    ]
  }
  ```
  Un cliente sin ventas devuelve `"sales": []` con `200 OK` (RF-4/RF-7
  se resuelven en el Frontend a partir de un arreglo vacío, tras
  aplicar el filtro de cada pantalla). [Cubre RF-1, RF-3, RF-4, RF-6,
  RF-7, RF-11]
- **Respuesta esperada (error):** `404 Not Found` —
  `{ "errors": [{ "field": "dni", "message": "Cliente no encontrado" }] }`
  cuando ningún cliente tiene ese DNI. [Cubre RF-2]

### Vista "Anular Venta" (`VentaAnulacionForm.jsx`, flujo modificado)
- **Propósito:** sin cambios (HU-VEN-02); cambia cómo se llega a
  elegir la venta.
- **Componentes/estados clave:**
  - Campo "DNI del cliente" + botón "Buscar".
  - Estado "cliente no encontrado". [Cubre RF-2]
  - Estado "sin ventas confirmadas para anular". [Cubre RF-4]
  - Estado "lista de ventas": ID, fecha y total de cada venta
    Confirmada, con un botón "Anular" por fila. [Cubre RF-3, RF-11]
  - Al presionar "Anular" en una fila, se abre el diálogo de
    confirmación ya existente (sin cambios de textos ni de llamada a
    `anularVenta`); "Cancelar" cierra el diálogo y vuelve a la lista
    (no borra la búsqueda). [Cubre RF-5]
  - Tras anular con éxito, se vuelve a pedir la lista del mismo DNI
    (la venta anulada desaparece de "Confirmada"), permitiendo anular
    otra venta del mismo cliente sin rebuscar. [Soporte - sin RF
    directo]

### Vista "Modificar Venta" (`VentaEdicionForm.jsx`, flujo modificado)
- **Propósito:** sin cambios (HU-VEN-03); cambia cómo se llega a
  elegir la venta.
- **Componentes/estados clave:**
  - Campo "DNI del cliente" + botón "Buscar".
  - Estado "cliente no encontrado". [Cubre RF-2]
  - Estado "sin ventas registradas". [Cubre RF-7]
  - Estado "lista de ventas": ID, fecha, estado y total de cada venta,
    con un ícono de editar por fila, habilitado solo si `status ===
    "Borrador"`. [Cubre RF-6, RF-8, RF-11]
  - Al presionar el ícono sobre una fila en Borrador, se llama a
    `buscarVenta(id)` (ya existente) y se evalúa con
    `evaluateEdicionResult` (ya existente): si sigue en Borrador, se
    abre la vista de edición ya construida (selector de producto,
    guardar detalle, cerrar); si ya no lo está, se advierte "La venta
    ya no admite modificaciones" sin abrir la edición. [Cubre RF-9,
    RF-10]
  - "Volver"/cerrar la vista de edición regresa a la lista de ventas
    del mismo cliente (no a un campo de DNI vacío). [Soporte - sin RF
    directo]

## 4. Decisiones Técnicas

1. **Decisión Tomada:** `find_sales_by_customer_dni` busca las ventas
   de **todos** los `Customer` que comparten ese DNI, no solo del que
   devuelve `find_by_dni` (que prioriza al Activo).
   **Justificación:** desde [[014-correcciones-cliente]], un DNI puede
   pertenecer a más de un `Customer` (uno Activo, uno o más Inactivos).
   Las ventas quedan asociadas al `customer_id` que existía en el
   momento del alta; si un cliente se dio de baja y luego otro cliente
   nuevo se registró con el mismo DNI, las ventas del primero
   pertenecen a un `id` distinto del que hoy está Activo. Buscar solo
   contra el cliente Activo dejaría fuera ventas reales de ese DNI
   (por ejemplo, un Borrador sin cerrar de un cliente que luego se dio
   de baja).
   **Alternativa descartada:** reutilizar `repository.find_by_dni`
   (devuelve un único cliente, priorizando Activo) y buscar solo sus
   ventas — descartada porque, dado el escenario de RF-2/RF-7 de
   [[014-correcciones-cliente]], podría ocultar ventas legítimas de
   ese DNI. *(RF-1, RF-6)*

2. **Decisión Tomada:** el endpoint nuevo (`GET /ventas/cliente/{dni}`)
   no filtra por estado; cada pantalla (Anular/Modificar) aplica su
   propio filtro/regla en el Frontend sobre el mismo resultado.
   **Justificación:** es exactamente lo que pide la spec (RF-3 exige
   solo Confirmada en Anular; RF-6 exige todas en Modificar) y evita
   duplicar el endpoint o agregarle un parámetro de filtro que solo
   uno de los dos casos de uso necesitaría.
   **Alternativa descartada:** dos endpoints separados (uno que ya
   filtra Confirmada para Anular, otro con todos los estados para
   Modificar) — descartada por duplicar la misma consulta base sin
   necesidad; un único endpoint compartido, decidido en la entrevista,
   ya cubre ambos casos con un filtro liviano del lado del Frontend.
   *(RF-3, RF-6)*

3. **Decisión Tomada:** al presionar el ícono de editar sobre una fila
   en "Borrador" (Modificar Venta), se vuelve a pedir el detalle
   completo con `buscarVenta(id)` y se re-evalúa con
   `evaluateEdicionResult`, en vez de asumir directamente que la venta
   sigue editable porque así figuraba en la lista.
   **Justificación:** es RF-10, y sigue el mismo criterio de
   re-verificación ya usado en el resto del proyecto (ej.
   [[010-anular-venta]] RF-7, [[011-modificacion-venta]] RF-14): el
   tiempo entre listar y elegir es una ventana real donde otro proceso
   pudo cerrar o anular esa venta.
   **Alternativa descartada:** usar directamente los datos de la fila
   de la lista (que no incluyen los ítems) para abrir la edición —
   descartada porque la lista no trae el detalle completo (RF-6 solo
   pide ID/fecha/estado/total) y porque omitiría la re-verificación de
   estado que ya es un criterio establecido en el proyecto. *(RF-9,
   RF-10)*

4. **Decisión Tomada:** tras anular una venta con éxito, Anular Venta
   vuelve a pedir la lista de ventas del mismo DNI en vez de resetear
   la búsqueda a un campo vacío.
   **Justificación:** el nuevo flujo lista varias ventas de un mismo
   cliente; resetear todo obligaría a volver a escribir el DNI para
   anular una segunda venta del mismo cliente, un paso innecesario que
   el propio cambio de esta spec (listar y elegir) busca evitar.
   **Alternativa descartada:** mantener el reseteo completo, igual que
   el flujo de una sola venta de [[010-anular-venta]] — descartada por
   ir en contra del objetivo de esta spec (elegir entre varias ventas
   del mismo cliente cómodamente).
   *(Soporte - mejora de flujo, sin RF directo)*

5. **Decisión Tomada:** `evaluateClienteSalesParaAnular` y
   `evaluateClienteSalesParaModificar` son funciones separadas, cada
   una en el módulo puro ya existente de su propia pantalla
   (`ventaAnulacion.js`/`ventaEdicion.js`), en vez de una función
   compartida con un parámetro de filtro.
   **Justificación:** mismo criterio ya aplicado repetidas veces en el
   proyecto (ej. [[008-listar-productos]] decisión 2,
   [[013-validacion-amigable-formularios]] decisión 4): cada pantalla
   mantiene su propia lógica, aunque sea parecida, en vez de introducir
   una abstracción compartida sobre dos casos de uso con reglas de
   filtrado distintas (Confirmada únicamente vs. todos los estados).
   **Alternativa descartada:** una función
   `evaluateClienteSales(result, { onlyStatus })` compartida —
   descartada por la misma razón ya documentada en specs anteriores:
   mezclar dos reglas de negocio distintas detrás de un parámetro.
   *(RF-3, RF-6)*

## 5. Estrategia de Tests

### Backend — tests de integración (`repository_venta.py`, SQLite temporal)
- `find_sales_by_customer_dni` con un DNI inexistente devuelve
  `(False, [])`. [Cubre RF-2]
- `find_sales_by_customer_dni` con un cliente sin ventas devuelve
  `(True, [])`. [Cubre RF-4, RF-7]
- `find_sales_by_customer_dni` devuelve las ventas del cliente en los
  tres estados (Borrador, Confirmada, Anulada), ordenadas por fecha
  descendente. [Cubre RF-1, RF-6, RF-11]
- `find_sales_by_customer_dni` con dos `Customer` distintos que
  comparten el mismo DNI (uno Activo, uno Inactivo, vía
  [[014-correcciones-cliente]]) devuelve las ventas de **ambos**.
  [Cubre RF-1]

### Backend — tests de integración (`routes/ventas.py`, `TestClient`)
- `GET /ventas/cliente/{dni}` con un cliente sin ventas devuelve
  `"sales": []`. [Cubre RF-4, RF-7]
- `GET /ventas/cliente/{dni}` con ventas en varios estados las
  devuelve todas, con su `status`, ordenadas por fecha descendente.
  [Cubre RF-1, RF-6, RF-11]
- `GET /ventas/cliente/{dni}` con un DNI sin cliente devuelve 404 con
  "Cliente no encontrado". [Cubre RF-2]

### Frontend — tests sobre `ventasApi.js` (fetch mockeado)
- `buscarVentasDeCliente`: casos 200 (con y sin ventas) y 404. [Cubre
  RF-1, RF-2]

### Frontend — tests unitarios (`ventaAnulacion.js`, `ventaEdicion.js`)
- `evaluateClienteSalesParaAnular`: cliente no encontrado; cliente sin
  ventas Confirmada (aunque tenga otras); lista con solo las
  Confirmada. [Cubre RF-2, RF-3, RF-4]
- `evaluateClienteSalesParaModificar`: cliente no encontrado; cliente
  sin ninguna venta; lista con las tres, conservando su `status`.
  [Cubre RF-2, RF-6, RF-7]

### Frontend — Vitest + RTL sobre `VentaAnulacionForm.jsx`
- Buscar un DNI sin cliente muestra "Cliente no encontrado". [Cubre
  RF-2]
- Un cliente sin ventas Confirmada muestra el mensaje correspondiente.
  [Cubre RF-4]
- Un cliente con varias ventas Confirmada las lista todas; "Anular" en
  una fila abre la confirmación ya existente sobre esa venta. [Cubre
  RF-3, RF-5, RF-11]
- Anular con éxito vuelve a listar las ventas restantes del mismo DNI.
  [Cubre RF-5]

### Frontend — Vitest + RTL sobre `VentaEdicionForm.jsx`
- Buscar un DNI sin cliente muestra "Cliente no encontrado". [Cubre
  RF-2]
- Un cliente sin ventas muestra el mensaje correspondiente. [Cubre
  RF-7]
- Un cliente con ventas en los tres estados las lista todas, con el
  ícono de editar habilitado solo en la de Borrador. [Cubre RF-6,
  RF-8, RF-11]
- Presionar el ícono sobre la de Borrador abre la vista de edición ya
  existente. [Cubre RF-9]
- Si entre la lista y el clic la venta dejó de estar en Borrador
  (`buscarVenta` mockeado devolviendo otro estado), se advierte que ya
  no admite modificaciones, sin abrir la edición. [Cubre RF-10]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas.
- **Regla 2 (spec antes que código):** parte de
  `specs/017-busqueda-venta-por-cliente/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):**
  `find_sales_by_customer_dni`,
  `evaluateClienteSalesParaAnular`/`evaluateClienteSalesParaModificar`
  concentran las reglas, testeables sin HTTP ni React.
- **Regla 4 (tests obligatorios):** la estrategia cubre las 11 RF de la
  spec.
- **Regla 5 (persistencia única):** `find_sales_by_customer_dni` lee
  exclusivamente de `database.py`/las tablas `sales` y `customers`.
- **Regla 6 (idioma consistente):** identificadores en inglés
  (`find_sales_by_customer_dni`, `buscarVentasDeCliente`); mensajes en
  español ("Cliente no encontrado").
