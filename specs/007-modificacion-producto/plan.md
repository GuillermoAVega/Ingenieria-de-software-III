# Plan 007 — Modificación de Producto

Plan técnico para implementar `specs/007-modificacion-producto/spec.md`,
respetando `docs/constitution.md` y reutilizando lo ya construido en
[[005-alta-producto]] y [[006-baja-producto]] (`Product`, `find_by_sku`,
`core_producto.py`, `productosApi.js`). Este documento no contiene código:
describe estructura, decisiones y estrategia de verificación.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`repository_producto.py` (extendido)**: agrega `update_product`
  (actualiza `name`, `brand`, `description`, `unit_price`, `stock`; nunca
  toca `sku` ni `status`). Reutiliza `find_by_sku` (ya existente desde
  [[006-baja-producto]]) para la búsqueda. [Cubre RF-1, RF-6, RF-7, RF-8]
- **`routes/productos.py` (extendido)**: agrega `PUT /productos/{sku}/editar`,
  con sus propias `_normalize_edit_payload`/`_validate_edit_fields` (ver
  decisión técnica 1), y reutiliza `GET /productos/{sku}` (ya existente)
  para la búsqueda de RF-1/RF-2. [Cubre RF-1 a RF-8]

### Frontend (`app/frontend/`)

- **`productoFields.js` (extendido)**: agrega `PRODUCTO_EDICION_FIELDS`,
  derivado de `PRODUCTO_FIELDS` filtrando el campo `sku`. [Cubre RF-3,
  RF-7]
- **`productoEdicion.js` (nuevo)**: módulo puro, análogo a
  `clienteEdicion.js`: interpreta el resultado de la búsqueda (no
  encontrado / encontrado con sus datos). [Cubre RF-1, RF-2]
- **`validationProducto.js` (extendido)**: agrega
  `validateProductoEdicionForm`, función nueva y separada de
  `validateProductoForm` (ver decisión técnica 1). [Cubre RF-4, RF-5]
- **`api/productosApi.js` (extendido)**: agrega `editarProducto(sku, input)`
  (`PUT /productos/{sku}/editar`). [Cubre RF-6]
- **`components/ProductoEdicionForm.jsx` (nuevo)**: búsqueda por SKU
  (reutiliza `buscarProducto`) → formulario pre-cargado con los datos
  actuales (SKU mostrado como texto de solo lectura, no como `<input>`) →
  validación inmediata con `validateProductoEdicionForm` → guarda directo
  al enviar (sin diálogo de confirmación). [Cubre RF-1 a RF-8]
- **`App.jsx` (extendido)**: agrega la séptima pestaña "Editar Producto".
  [Soporte, sin RF directo]

## 2. Modelo de la Base de Datos

No se agregan tablas ni columnas nuevas. Esta feature es de lectura y
escritura sobre las mismas columnas de `products` ya definidas en
[[005-alta-producto]]/[[006-baja-producto]] (`name`, `brand`,
`description`, `unit_price`, `stock`); `sku` y `status` se leen pero nunca
se escriben desde esta feature.

## 3. Contrato de la Interfaz Web

### Endpoint: `PUT /productos/{sku}/editar`

- **Método y ruta:** `PUT /productos/{sku}/editar` (el SKU de la URL es el
  mismo usado para la búsqueda de RF-1; no es parte del body).
- **Payload de entrada:**
  ```json
  {
    "name": "Coca-Cola 500ml", "brand": "Coca-Cola",
    "description": "Botella descartable", "unit_price": "399.90", "stock": "80"
  }
  ```
  Cualquier campo `sku` que venga en el body se ignora — el backend nunca
  lo lee para esta ruta (RF-7).
- **Respuesta esperada (éxito):** `200 OK`
  ```json
  { "message": "Producto modificado exitosamente", "product": { "sku": "ABC123", "...": "...", "status": "Activo" } }
  ```
  [Cubre RF-6]
- **Respuesta esperada (error):** `404 Not Found` si el SKU no existe;
  `422 Unprocessable Entity` con la lista de advertencias si hay campos
  vacíos o Precio/Stock inválidos (mismo formato que el alta). [Cubre
  RF-2, RF-4, RF-5]

### Vista: pestaña "Editar Producto" (`ProductoEdicionForm.jsx`)

- **Ruta/URL:** no aplica (SPA de una sola página con pestañas).
- **Propósito:** localizar un producto por SKU y editar sus datos, sin
  cambiar el SKU ni el estado. [Cubre HU-PROD-03]
- **Componentes/estados clave:**
  - Campo de búsqueda por SKU.
  - Estado "no encontrado" (RF-2).
  - Formulario pre-cargado con Nombre/Marca/Descripción/Precio/Stock
    editables y el SKU mostrado como texto fijo (RF-3, RF-7).
  - Errores de campo mostrados de inmediato (validación en el Frontend) y
    los devueltos por el backend (RF-4, RF-5).
  - Guardado directo: al enviar con datos válidos, se guarda y se muestra
    "Producto modificado exitosamente" sin diálogo de confirmación (RF-6).

## 4. Decisiones Técnicas

1. **Decisión Tomada:** las funciones de validación de la edición
   (`_normalize_edit_payload`/`_validate_edit_fields` en
   `routes/productos.py`, `validateProductoEdicionForm` en
   `validationProducto.js`) se agregan como funciones **nuevas y
   separadas** de las que ya usa el alta (`_normalize_payload`/
   `_validate_fields`/`validateProductoForm`), en vez de parametrizarlas
   para que sirvan a ambos casos.
   **Justificación:** ambas reutilizan los mismos validadores de bajo
   nivel (`core.trim_leading_trailing_space`,
   `core_producto.validate_positive_number`/`validate_positive_integer`),
   así que no hay duplicación de ninguna regla de negocio real, solo del
   wrapper que decide qué campos son obligatorios (con o sin `sku`).
   Modificar las funciones del alta —ya en producción y probadas— para
   aceptar un `required_fields` configurable introduciría un riesgo de
   regresión en una feature que ya funciona, a cambio de ahorrar unas
   pocas líneas.
   **Alternativa descartada:** parametrizar `_normalize_payload`/
   `_validate_fields`/`validateProductoForm` con listas de campos
   configurables — descartada por el riesgo de regresión en el alta.
   *(RF-4, RF-5, RF-7)*

2. **Decisión Tomada:** no se agrega ninguna verificación de SKU
   duplicado en la edición (no existe un análogo a
   `dni_belongs_to_another_active_customer` de
   [[003-modificacion-cliente]]).
   **Justificación:** RF-7 prohíbe editar el SKU; al no ser un campo del
   payload de edición, no hay ningún escenario de duplicado que
   verificar.
   **Alternativa descartada:** ninguna — no aplica, dado que Cliente sí
   permite editar el DNI y Producto no permite editar el SKU. *(RF-7)*

3. **Decisión Tomada:** guardado directo al enviar el formulario (RF-6),
   sin el patrón de búsqueda + confirmación explícita usado en
   [[006-baja-producto]].
   **Justificación:** resuelto explícitamente en la entrevista de la
   spec; a diferencia de la baja (una acción destructiva en el sentido de
   sacar al producto de circulación), editar datos es una corrección de
   bajo riesgo, análoga al alta.
   **Alternativa descartada:** reutilizar el patrón de confirmación de la
   baja — descartada porque la spec pide explícitamente lo contrario.
   *(RF-6)*

4. **Decisión Tomada:** `PRODUCTO_EDICION_FIELDS` se deriva filtrando
   `PRODUCTO_FIELDS` (excluye `sku`), en vez de declarar un array nuevo
   desde cero.
   **Justificación:** reutiliza el label/hint ya definidos para
   Nombre/Marca/Descripción/Precio/Stock; evita que ambos arrays diverjan
   por error si se cambia el texto de un campo en el futuro.
   **Alternativa descartada:** duplicar el array — descartada por
   duplicar información que ya vive en `productoFields.js`. *(RF-3)*

5. **Decisión Tomada:** el SKU se muestra en `ProductoEdicionForm.jsx`
   como texto de solo lectura, no como un `<input>` deshabilitado.
   **Justificación:** refuerza en la UI, de forma inequívoca, que el SKU
   no es editable (RF-7); un `<input disabled>` sugiere visualmente un
   campo de formulario, lo cual es engañoso para algo que nunca se envía
   en el payload.
   **Alternativa descartada:** `<input>` deshabilitado — descartada por
   ser una señal visual más débil de "esto no es un campo del
   formulario". *(RF-7)*

6. **Decisión Tomada:** tras un guardado exitoso, `ProductoEdicionForm.jsx`
   vuelve al estado de búsqueda (limpia el SKU buscado y oculta el
   formulario), igual que `ClienteEdicionForm.jsx` en
   [[003-modificacion-cliente]].
   **Justificación:** mantiene el mismo patrón de interacción ya usado
   para cerrar el ciclo de una edición completada en el resto de la app.
   **Alternativa descartada:** dejar el formulario abierto con los
   valores guardados — descartada por no estar pedida y por romper la
   consistencia entre features. *(RF-6)*

## 5. Estrategia de Tests

### Backend — tests de integración (`repository_producto.py`, SQLite temporal)
- `update_product` actualiza los 5 campos editables y nunca modifica
  `sku` ni `status`, probado tanto sobre un producto Activo como uno
  Inactivo. [Cubre RF-6, RF-7, RF-8]

### Backend — tests de integración (`routes/productos.py`, `TestClient`)
- Edición exitosa sobre un producto Activo: 200, mensaje, datos
  actualizados, `sku`/`status` sin cambios. [Cubre RF-6, RF-7]
- Edición exitosa sobre un producto Inactivo: datos actualizados,
  `status` sigue Inactivo. [Cubre RF-1, RF-6, RF-8]
- Un `sku` incluido en el body de la edición se ignora (no cambia nada).
  [Cubre RF-7]
- Campos obligatorios vacíos (Nombre, Marca, Precio, Stock — no incluye
  SKU): 422 con las 4 advertencias. [Cubre RF-4]
- `unit_price`/`stock` inválidos (cero, negativo, no numérico, `stock`
  con decimales): misma advertencia que el alta. [Cubre RF-4]
- Múltiples errores a la vez: se reportan juntos, sin guardar nada.
  [Cubre RF-5]
- Edición sobre un SKU inexistente: 404. [Cubre RF-2]

### Frontend — tests unitarios (`productoEdicion.js`, sin React)
- Resultado "no encontrado" → estado `NOT_FOUND`. [Cubre RF-2]
- Producto encontrado → estado `FOUND` con sus datos. [Cubre RF-1, RF-3]

### Frontend — tests unitarios (`validateProductoEdicionForm`, sin React)
- Obligatoriedad de los 4 campos requeridos (no exige `sku`).
  `unit_price`/`stock` inválidos. Descripción opcional. Varios errores
  juntos. [Cubre RF-4, RF-5]

### Frontend — tests sobre `productosApi.js` (fetch mockeado)
- `editarProducto`: traduce una respuesta 200 y una 422 a la forma
  esperada. [Cubre RF-6]

### Frontend — Vitest + RTL sobre `ProductoEdicionForm.jsx`
Con `productosApi.js` mockeado:
- SKU inexistente: mensaje de "no encontrado", sin formulario. [Cubre
  RF-2]
- SKU existente: formulario pre-cargado, con el SKU mostrado como texto
  fijo (no como input). [Cubre RF-1, RF-3, RF-7]
- Envío con un campo inválido: advertencia inmediata, sin llamar a
  `editarProducto`. [Cubre RF-4, RF-5]
- Envío válido: se llama a `editarProducto`, se muestra "Producto
  modificado exitosamente" y el formulario vuelve al estado de búsqueda.
  [Cubre RF-6]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas.
- **Regla 2 (spec antes que código):** parte de
  `specs/007-modificacion-producto/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** `productoEdicion.js` y
  `validateProductoEdicionForm` son testeables sin React; la validación
  de negocio del backend vive en `core_producto.py`/`routes/productos.py`,
  testeable sin levantar la UI.
- **Regla 4 (tests obligatorios):** la estrategia cubre los ocho RF de la
  spec.
- **Regla 5 (persistencia única):** todo pasa por
  `repository_producto.py`/`database.py`.
- **Regla 6 (idioma consistente):** identificadores en inglés
  (`update_product`, `ProductoEdicionForm.jsx`); mensajes en español
  ("Producto modificado exitosamente").
