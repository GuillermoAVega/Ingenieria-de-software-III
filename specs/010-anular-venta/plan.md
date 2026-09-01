# Plan 010 — Anular Venta

Plan técnico para implementar `specs/010-anular-venta/spec.md`,
respetando `docs/constitution.md` y reutilizando lo ya construido en
[[009-alta-venta]] (`Sale`, `SaleItem`, `_serialize_sale`,
`ventasApi.js`) y el patrón de búsqueda + confirmación ya validado en
[[002-baja-cliente]]/[[006-baja-producto]]. La diferencia central de
esta spec respecto a esos precedentes es RF-7: acá el backend sí
re-verifica el estado al confirmar, porque el efecto colateral (reponer
stock) no es idempotente. Este documento no contiene código: describe
estructura, decisiones y estrategia de verificación.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`models.py` (extendido)**: agrega `CANCELLED = "Anulada"` a
  `SaleStatus` (ya anticipado, sin usarse, desde [[009-alta-venta]]).
  [Cubre RF-4, RF-6]
- **`repository_venta.py` (extendido)**: agrega `find_by_id` (búsqueda
  de solo lectura por ID, sin efectos secundarios) y `cancel_sale`
  (re-verifica el estado actual de la venta, y solo si sigue
  "Confirmada" repone el stock de cada ítem y cambia su estado a
  "Anulada"; devuelve si la venta ya estaba anulada para que la ruta
  pueda rechazar el pedido en vez de aplicar dos veces la reposición).
  [Cubre RF-1, RF-4, RF-7, RF-8]
- **`routes/ventas.py` (extendido)**: agrega `GET /ventas/{sale_id}`
  (búsqueda, reutiliza `_serialize_sale` ya existente) y `PATCH
  /ventas/{sale_id}/anular` (ejecución, con la verificación de RF-7).
  [Cubre RF-1 a RF-8]

### Frontend (`app/frontend/`)

- **`ventaAnulacion.js` (nuevo)**: módulo puro, análogo a
  `bajaCliente.js`/`productoBaja.js`: interpreta el resultado de la
  búsqueda de una venta (no encontrada / ya anulada / requiere
  confirmación). [Cubre RF-2, RF-3, RF-6]
- **`api/ventasApi.js` (extendido)**: agrega `buscarVenta(id)` (`GET`) y
  `anularVenta(id)` (`PATCH`), misma forma de traducción que las demás
  funciones de la API. [Cubre RF-1, RF-2, RF-4]
- **`components/VentaAnulacionForm.jsx` (nuevo)**: búsqueda por ID,
  delega en `ventaAnulacion.js` qué estado mostrar, diálogo de
  confirmación, y maneja explícitamente el caso en que el backend
  rechace la anulación al confirmar (RF-7) mostrando su mensaje en vez
  de asumir éxito. [Cubre RF-1 a RF-7]
- **`App.jsx` (extendido)**: agrega la décima pestaña "Anular Venta".
  [Soporte, sin RF directo]

## 2. Modelo de la Base de Datos

Ninguna tabla nueva. Extensión del enum `SaleStatus` (ya definido en
[[009-alta-venta]]) con un segundo valor:

| Valor actual | Valor nuevo |
|---|---|
| `CONFIRMED = "Confirmada"` | `CANCELLED = "Anulada"` |

No se agregan columnas a `sales`/`sale_items`; el campo `status` de
`sales` ya soporta cualquier valor del enum.

## 3. Contrato de la Interfaz Web

### Endpoint: `GET /ventas/{sale_id}`

- **Método y ruta:** `GET /ventas/{sale_id}` (`sale_id: int`, FastAPI
  valida el formato automáticamente y devuelve 422 si no es un entero).
- **Payload de entrada:** ninguno.
- **Respuesta esperada (éxito):** `200 OK`, mismo formato que la
  respuesta de `POST /ventas` (`_serialize_sale`), incluyendo `status`
  (`"Confirmada"` o `"Anulada"`). [Cubre RF-1]
- **Respuesta esperada (error):** `404 Not Found`
  ```json
  { "errors": [ { "field": "id", "message": "Venta no encontrada" } ] }
  ```
  [Cubre RF-2]

### Endpoint: `PATCH /ventas/{sale_id}/anular`

- **Método y ruta:** `PATCH /ventas/{sale_id}/anular`
- **Payload de entrada:** ninguno.
- **Respuesta esperada (éxito):** `200 OK`
  ```json
  { "message": "Venta anulada exitosamente", "sale": { "...": "...", "status": "Anulada" } }
  ```
  El stock de cada producto del detalle queda repuesto. [Cubre RF-4]
- **Respuesta esperada (error):**
  - `404 Not Found` si el `sale_id` no existe, mismo formato que la
    búsqueda. [Cubre RF-2]
  - `422 Unprocessable Entity` si la venta **ya estaba** "Anulada" en el
    momento de confirmar:
    ```json
    { "errors": [ { "field": "id", "message": "La venta ya se encuentra anulada" } ] }
    ```
    No repone stock ni vuelve a cambiar el estado (RF-7). [Cubre RF-6,
    RF-7]

### Vista: pestaña "Anular Venta" (`VentaAnulacionForm.jsx`)

- **Ruta/URL:** no aplica (SPA de una sola página con pestañas).
- **Propósito:** localizar una venta por ID y anularla tras confirmar,
  reponiendo el stock de sus productos. [Cubre HU-VEN-02]
- **Componentes/estados clave:**
  - Campo de búsqueda por ID de venta.
  - Estado "no encontrada" (RF-2), estado "ya anulada" sin botón de
    confirmar (RF-6), estado "requiere confirmación" con el detalle de
    la venta + botones Confirmar/Cancelar (RF-3, RF-5).
  - Mensaje de éxito "Venta anulada exitosamente" (RF-4), o el mensaje
    de rechazo del backend si la venta se anuló por otra vía justo antes
    de confirmar (RF-7).

## 4. Decisiones Técnicas

1. **Decisión Tomada:** `SaleStatus` se extiende con `CANCELLED =
   "Anulada"`.
   **Justificación:** ya estaba anticipado como decisión técnica 6 del
   plan de [[009-alta-venta]] ("quedará para cuando se construya la
   baja/anulación de venta"); esta es esa spec.
   **Alternativa descartada:** ninguna — es la continuación directa de
   una decisión ya tomada. *(RF-4, RF-6)*

2. **Decisión Tomada:** `repository_venta.cancel_sale` vuelve a
   consultar el estado ACTUAL de la venta (una consulta fresca, no el
   objeto ya cargado durante la búsqueda) antes de aplicar cualquier
   cambio, y devuelve una señal explícita de "ya estaba anulada" para
   que la ruta pueda rechazar el pedido con 422 en vez de aplicar la
   reposición de stock de nuevo.
   **Justificación:** RF-7 exige esto explícitamente. A diferencia de
   `deactivate_by_dni`/`deactivate_by_sku` (donde repetir la baja es
   inofensivo, el estado queda igual), repetir `cancel_sale` sin esta
   verificación duplicaría la reposición de stock — un error de datos
   real, documentado en la propia spec como la razón de apartarse del
   patrón de [[002-baja-cliente]]/[[006-baja-producto]]/[[009-alta-venta]].
   **Alternativa descartada:** aplicar el mismo criterio "sin
   re-verificación" que las demás bajas — descartada explícitamente por
   la spec, dado que acá el efecto colateral no es idempotente. *(RF-7)*

3. **Decisión Tomada:** la reposición de stock de todos los ítems y el
   cambio de estado a "Anulada" ocurren dentro de la misma sesión que la
   verificación de RF-7, con un único `commit()` al final.
   **Justificación:** mismo criterio de atomicidad que `create_sale` en
   [[009-alta-venta]] — un error a mitad de camino no debe dejar stock
   repuesto sin que la venta quede anulada, ni viceversa (NFR de
   consistencia de esta spec).
   **Alternativa descartada:** un `commit()` por cada producto repuesto
   — descartada por el mismo motivo que en 009: un fallo parcial dejaría
   cambios inconsistentes. *(NFR de consistencia, RF-4)*

4. **Decisión Tomada:** `PATCH /ventas/{sale_id}/anular` devuelve `422`
   (no `200` idempotente) cuando la venta ya estaba anulada al momento
   de confirmar.
   **Justificación:** en las bajas de cliente/producto, un `200`
   idempotente es seguro porque no hay ningún efecto colateral que se
   duplique; acá sí lo hay (el stock), así que la respuesta debe dejar
   en claro que la operación no se aplicó, no disfrazarla de éxito.
   **Alternativa descartada:** `200` con el mismo mensaje de éxito,
   igual que las bajas — descartada porque ocultaría al Frontend que la
   reposición de stock no ocurrió en este pedido. *(RF-6, RF-7)*

5. **Decisión Tomada:** nuevo endpoint `GET /ventas/{sale_id}` para la
   búsqueda, reutilizando `_serialize_sale` ya existente (usado hoy solo
   por la respuesta de `POST /ventas`).
   **Justificación:** evita reimplementar el armado del detalle de una
   venta para la respuesta de búsqueda.
   **Alternativa descartada:** duplicar la lógica de serialización
   dentro de un nuevo endpoint — descartada por duplicar código ya
   existente y probado. *(RF-1)*

6. **Decisión Tomada:** `ventaAnulacion.js` en el Frontend, módulo puro
   análogo a `bajaCliente.js`/`productoBaja.js`, con los mismos tres
   estados (`NOT_FOUND`/`ALREADY_CANCELLED`/`REQUIRES_CONFIRMATION`).
   **Justificación:** regla 3 de la constitución; mantiene el mismo
   patrón ya usado para las dos bajas anteriores.
   **Alternativa descartada:** lógica inline en el componente —
   descartada por acoplar la regla de negocio a la UI. *(RF-2, RF-3,
   RF-6)*

## 5. Estrategia de Tests

### Backend — tests de integración (`repository_venta.py`, SQLite temporal)
- `find_by_id` encuentra una venta existente y devuelve `None` si no
  existe. [Cubre RF-1, RF-2]
- `cancel_sale` sobre una venta "Confirmada": cambia el estado a
  "Anulada", repone el stock de cada ítem (incluida una venta con
  varios ítems de distintos productos), y devuelve `already_cancelled =
  False`. [Cubre RF-4, RF-8]
- `cancel_sale` sobre un `sale_id` inexistente: devuelve `(None, False)`.
  [Cubre RF-2]
- `cancel_sale` invocado dos veces seguidas sobre la misma venta: la
  segunda vez devuelve `already_cancelled = True` y el stock NO se
  repone una segunda vez. [Cubre RF-7]

### Backend — tests de integración (`routes/ventas.py`, `TestClient`)
- `GET /ventas/{sale_id}` sobre una venta "Confirmada" y sobre una
  "Anulada": informa el estado correspondiente; sobre un ID inexistente:
  404. [Cubre RF-1, RF-2]
- `PATCH /ventas/{sale_id}/anular` sobre una venta "Confirmada" con
  varios ítems: 200, mensaje de éxito, estado "Anulada", stock repuesto
  de cada producto según su ítem. [Cubre RF-4]
- `PATCH /ventas/{sale_id}/anular` sobre un `sale_id` inexistente: 404.
  [Cubre RF-2]
- `PATCH /ventas/{sale_id}/anular` invocado dos veces seguidas: la
  primera responde 200; la segunda responde 422 "la venta ya se
  encuentra anulada", y el stock del producto queda igual que después
  de la primera anulación (no se repuso dos veces). [Cubre RF-6, RF-7]

### Frontend — tests unitarios (`ventaAnulacion.js`, sin React)
- Resultado "no encontrada" → estado `NOT_FOUND`. [Cubre RF-2]
- Venta "Confirmada" → estado `REQUIRES_CONFIRMATION`. [Cubre RF-3]
- Venta "Anulada" → estado `ALREADY_CANCELLED`. [Cubre RF-6]

### Frontend — tests sobre `ventasApi.js` (fetch mockeado)
- `buscarVenta`/`anularVenta`: traducen 200, 404 y 422 a la forma
  esperada. [Cubre RF-1, RF-2, RF-4, RF-7]

### Frontend — Vitest + RTL sobre `VentaAnulacionForm.jsx`
Con `ventasApi.js` mockeado:
- ID inexistente: mensaje de "no encontrada", sin botón de confirmar.
  [Cubre RF-2]
- Venta ya "Anulada": mensaje correspondiente, sin botón de confirmar ni
  llamada a `anularVenta`. [Cubre RF-6]
- Venta "Confirmada": muestra el detalle + botones Confirmar/Cancelar.
  [Cubre RF-3]
- Confirmar con éxito: llama a `anularVenta`, muestra el mensaje de
  éxito. [Cubre RF-4]
- Cancelar: no llama a `anularVenta`, la venta queda sin cambios. [Cubre
  RF-5]
- Confirmar y que el backend rechace con 422 (simulando que se anuló
  por otra vía momentos antes): muestra el mensaje de rechazo del
  backend, no un mensaje de éxito falso. [Cubre RF-7]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas.
- **Regla 2 (spec antes que código):** parte de
  `specs/010-anular-venta/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** `ventaAnulacion.js` es
  testeable sin React; la verificación de RF-7 vive en
  `repository_venta.py`, testeable sin HTTP.
- **Regla 4 (tests obligatorios):** la estrategia cubre los ocho RF de
  la spec, con énfasis particular en probar la no-duplicación de stock
  de RF-7.
- **Regla 5 (persistencia única):** `cancel_sale` es la única vía de
  escritura para anular una venta, a través de `database.py`.
- **Regla 6 (idioma consistente):** identificadores en inglés
  (`cancel_sale`, `find_by_id`, `VentaAnulacionForm.jsx`); mensajes en
  español ("Venta anulada exitosamente", "La venta ya se encuentra
  anulada").
