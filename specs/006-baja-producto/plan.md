# Plan 006 — Baja de Producto

Plan técnico para implementar `specs/006-baja-producto/spec.md`,
respetando `docs/constitution.md` y reutilizando lo ya construido en
[[005-alta-producto]] (`Product`, `core_producto.py`,
`repository_producto.py`, `routes/productos.py`) y el diseño ya validado
de [[002-baja-cliente]]/[[003-modificacion-cliente]] para Cliente (mismo
patrón de búsqueda + confirmación, misma relajación de unicidad). Este
documento no contiene código: describe estructura, decisiones y
estrategia de verificación.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`models.py` (extendido)**: agrega `ProductStatus` (enum `Activo`/
  `Inactivo`, análogo a `ClientStatus`) y la columna `status` a `Product`;
  quita el `unique=True` de `sku`. [Cubre RF-6, RF-10]
- **`core_producto.py` (extendido)**: agrega `initial_status()`, análoga a
  `core.initial_status()` de Cliente. [Cubre RF-4]
- **`repository_producto.py` (extendido)**: `sku_exists` (ya existente, la
  usa el alta de [[005-alta-producto]]) se modifica para comparar solo
  contra productos Activos; agrega `find_by_sku` (búsqueda de solo
  lectura, prioriza el resultado Activo si el SKU está compartido) y
  `deactivate_by_sku` (cambia el estado a Inactivo sin re-verificar el
  estado previo). [Cubre RF-1, RF-4, RF-6, RF-7, RF-8, RF-10]
- **`routes/productos.py` (extendido)**: agrega `GET /productos/{sku}`
  (búsqueda) y `PATCH /productos/{sku}/baja` (ejecución); `_serialize_product`
  incluye `status`; `create_product` pasa a asignar el estado inicial vía
  `core_producto.initial_status()`. [Cubre RF-1 a RF-10]

### Frontend (`app/frontend/`)

- **`productoBaja.js` (nuevo)**: módulo puro, análogo a `bajaCliente.js`:
  interpreta el resultado de la búsqueda (no encontrado / ya inactivo /
  requiere confirmación). [Cubre RF-2, RF-3, RF-6]
- **`api/productosApi.js` (extendido)**: agrega `buscarProducto(sku)`
  (`GET`) y `darDeBajaProducto(sku)` (`PATCH`), misma forma de traducción
  que las funciones ya existentes de Cliente. [Cubre RF-1, RF-2, RF-4]
- **`components/ProductoBajaForm.jsx` (nuevo)**: búsqueda por SKU, delega
  en `productoBaja.js` qué estado mostrar, diálogo de confirmación,
  cancelación sin llamar a la API. Análogo a `ClienteBajaForm.jsx`. [Cubre
  RF-1 a RF-6]
- **`App.jsx` (extendido)**: agrega la sexta pestaña "Baja de Producto".
  [Soporte, sin RF directo]

## 2. Modelo de la Base de Datos

Modificación de la tabla `products` (ya existente desde
[[005-alta-producto]]):

| Columna | Cambio | Notas |
|---|---|---|
| `status` | **Nueva**, Enum (`Activo`/`Inactivo`), `nullable=False`, sin `default` a nivel de columna | Se asigna explícitamente en `create_product` vía `core_producto.initial_status()`, igual que `Customer.status` en [[001-alta-cliente]]. [Cubre RF-4, RF-6] |
| `sku` | Se quita `unique=True` (mantiene `index=True`) | RF-10 exige permitir el mismo SKU en un producto Inactivo y uno nuevo; la unicidad real (solo contra Activos) pasa a `repository_producto.sku_exists`. [Cubre RF-10] |

No se agregan tablas nuevas.

## 3. Contrato de la Interfaz Web

### Endpoint: `GET /productos/{sku}`

- **Método y ruta:** `GET /productos/{sku}`
- **Payload de entrada:** ninguno (el SKU va en la URL).
- **Respuesta esperada (éxito):** `200 OK`
  ```json
  { "product": { "sku": "ABC123", "name": "...", "brand": "...",
    "description": "...", "unit_price": 350.5, "stock": 100, "status": "Activo" } }
  ```
  [Cubre RF-1]
- **Respuesta esperada (error):** `404 Not Found`
  ```json
  { "errors": [ { "field": "sku", "message": "Producto no encontrado" } ] }
  ```
  [Cubre RF-2]

### Endpoint: `PATCH /productos/{sku}/baja`

- **Método y ruta:** `PATCH /productos/{sku}/baja`
- **Payload de entrada:** ninguno.
- **Respuesta esperada (éxito):** `200 OK`
  ```json
  { "message": "Producto dado de baja exitosamente", "product": { "...": "...", "status": "Inactivo" } }
  ```
  Se aplica sin re-verificar el estado previo (RF-8): si el producto ya
  estaba Inactivo, la respuesta es igual de exitosa (comportamiento
  idempotente aceptado, igual que en [[002-baja-cliente]]). [Cubre RF-4,
  RF-7, RF-8]
- **Respuesta esperada (error):** `404 Not Found` si el SKU no existe,
  mismo formato que el endpoint de búsqueda.

### Vista: pestaña "Baja de Producto" (`ProductoBajaForm.jsx`)

- **Ruta/URL:** no aplica (SPA de una sola página con pestañas).
- **Propósito:** localizar un producto por SKU y darlo de baja tras
  confirmar. [Cubre HU-PROD-02]
- **Componentes/estados clave:**
  - Campo de búsqueda por SKU.
  - Estado "no encontrado" (RF-2), estado "ya inactivo" sin botón de
    confirmar (RF-6), estado "requiere confirmación" con datos del
    producto + botones Confirmar/Cancelar (RF-3, RF-5).
  - Mensaje de éxito "Producto dado de baja exitosamente" (RF-4).

## 4. Decisiones Técnicas

1. **Decisión Tomada:** agregar `ProductStatus` (enum `Activo`/`Inactivo`)
   y la columna `status` a `Product`, con `Activo` asignado explícitamente
   en `create_product` vía una nueva `core_producto.initial_status()`.
   **Justificación:** RF-3, RF-4 y RF-6 requieren distinguir Activo de
   Inactivo, concepto que no existía en [[005-alta-producto]]; replicar el
   mismo patrón que `ClientStatus`/`core.initial_status()` de Cliente
   mantiene la consistencia entre dominios y la testabilidad (regla 3 de
   la constitución).
   **Alternativa descartada:** un booleano `is_active` — descartada por
   romper la consistencia con el patrón ya usado para Cliente, donde el
   estado se expresa como los mismos dos literales en español que ya se
   muestran en la UI. *(RF-4, RF-6)*

2. **Decisión Tomada:** quitar `unique=True` de `sku` y **modificar**
   `sku_exists` (ya existente, usada por el alta de [[005-alta-producto]])
   para que compare solo contra productos Activos, en vez de crear una
   función paralela.
   **Justificación:** a diferencia de Cliente (donde el alta sigue
   bloqueando contra cualquier estado y solo la *edición*, en
   [[003-modificacion-cliente]], tiene la excepción vía una función nueva),
   en Producto no existe todavía ninguna feature de edición — RF-10 de
   esta spec exige que el ALTA en sí misma deje de bloquear contra
   Inactivos. Con un solo consumidor de la regla, modificarla en el lugar
   es más simple que mantener dos funciones.
   Riesgo aceptado: igual que con Cliente, una escritura SQL directa que
   bypasee `repository_producto.py` podría crear dos productos Activos con
   el mismo SKU; se acepta porque toda escritura de esta app ya pasa
   exclusivamente por `repository_producto.py`.
   Nota operativa: igual que en [[003-modificacion-cliente]], este cambio
   de esquema requiere recrear `database.db` en desarrollo (no hay
   Alembic en el stack).
   **Alternativa descartada:** dejar `sku_exists` intacta y agregar una
   función nueva tipo `sku_belongs_to_another_active_product` — descartada
   por ser una abstracción prematura sin una segunda función (una futura
   edición) que la necesite todavía. *(RF-10)*

3. **Decisión Tomada:** `find_by_sku` prioriza el resultado Activo cuando
   dos productos comparten el mismo SKU, mismo criterio que `find_by_dni`
   de [[002-baja-cliente]]/[[003-modificacion-cliente]].
   **Justificación:** una vez que RF-10 permite SKUs compartidos con un
   Inactivo, la búsqueda debe resolver de forma determinística a qué
   producto se refiere; como máximo puede haber un producto Activo por
   SKU (lo garantiza el `sku_exists` corregido en la decisión 2).
   **Alternativa descartada:** orden no determinístico — mismo
   razonamiento que la decisión técnica 3 de [[003-modificacion-cliente]].
   *(RF-1, RF-10)*

4. **Decisión Tomada:** reutilizar el mismo patrón de endpoints (búsqueda
   por identificador + acción de baja separada) y el mismo diseño de
   confirmación 100% Frontend, sin re-verificación al confirmar (RF-8),
   que ya se construyó y probó para [[002-baja-cliente]].
   **Justificación:** consistencia entre dominios; evita reinventar un
   mecanismo ya validado para un problema idéntico.
   **Alternativa descartada:** un mecanismo de confirmación distinto (ej.
   un token de confirmación emitido por el backend) — descartada por no
   estar pedida y por romper la consistencia entre features de baja.
   *(RF-3, RF-5, RF-8)*

5. **Decisión Tomada:** `productoBaja.js` en el Frontend es un módulo
   puro análogo a `bajaCliente.js`, en vez de un `if/else` inline en
   `ProductoBajaForm.jsx`.
   **Justificación:** regla 3 de la constitución — la interpretación del
   resultado de la búsqueda es una regla de negocio, debe ser testeable
   sin renderizar React.
   **Alternativa descartada:** inline en el componente — descartada por
   acoplar la regla de negocio a la UI. *(RF-2, RF-3, RF-6)*

## 5. Estrategia de Tests

### Backend — tests unitarios (`core_producto.py`, sin base de datos)
- `initial_status()` devuelve `"Activo"`. [Cubre RF-4]

### Backend — tests de integración (`repository_producto.py`, SQLite temporal)
- `sku_exists` ahora `False` si el único producto con ese SKU está
  Inactivo, y `True` si hay un Activo con ese SKU (aunque también exista
  un Inactivo con el mismo). [Cubre RF-10]
- `find_by_sku` devuelve el producto Activo cuando hay un Activo y un
  Inactivo con el mismo SKU. [Cubre RF-1, RF-10]
- `deactivate_by_sku` cambia el estado a Inactivo y persiste, sin tocar
  `unit_price`/`stock`; devuelve `None` si el SKU no existe; invocado
  sobre un producto ya Inactivo no lanza error (idempotente). [Cubre RF-4,
  RF-6, RF-7, RF-8]

### Backend — tests de integración (`routes/productos.py`, `TestClient`)
- Alta de un producto asigna `status: "Activo"` por defecto. [Cubre RF-4]
- `GET /productos/{sku}` sobre Activo/Inactivo informa el estado; sobre un
  SKU inexistente devuelve 404. [Cubre RF-1, RF-2]
- `PATCH /productos/{sku}/baja` sobre un producto Activo: 200, mensaje de
  éxito, estado Inactivo, `stock`/`unit_price` sin cambios; sobre un SKU
  inexistente: 404; invocado directamente sobre uno ya Inactivo: 200
  igual (documenta RF-8). [Cubre RF-4, RF-6, RF-7, RF-8, RF-9]
- Dar de baja a un producto con stock alto (ej. 500) no lo modifica.
  [Cubre RF-9]
- Un alta nueva con el SKU de un producto Inactivo se acepta (200/201);
  con el SKU de uno Activo se sigue rechazando como duplicado. [Cubre
  RF-10]

### Frontend — tests unitarios (`productoBaja.js`, sin React)
- Resultado "no encontrado" → estado `NOT_FOUND`. [Cubre RF-2]
- Producto Activo → estado `REQUIRES_CONFIRMATION`. [Cubre RF-3]
- Producto Inactivo → estado `ALREADY_INACTIVE`. [Cubre RF-6]

### Frontend — tests sobre `productosApi.js` (fetch mockeado)
- `buscarProducto`/`darDeBajaProducto`: traducen 200 y 404 a la forma
  esperada. [Cubre RF-1, RF-2, RF-4]

### Frontend — Vitest + RTL sobre `ProductoBajaForm.jsx`
Con `productosApi.js` mockeado:
- SKU inexistente: mensaje de "no encontrado", sin botón de confirmar.
  [Cubre RF-2]
- SKU de producto Inactivo: mensaje de "ya dado de baja", sin botón de
  confirmar ni llamada a `darDeBajaProducto`. [Cubre RF-6]
- SKU de producto Activo: datos + botones Confirmar/Cancelar. [Cubre RF-3]
- Confirmar: llama a `darDeBajaProducto`, muestra el mensaje de éxito.
  [Cubre RF-4]
- Cancelar: no llama a la API, el producto queda sin cambios. [Cubre RF-5]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas.
- **Regla 2 (spec antes que código):** parte de
  `specs/006-baja-producto/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** `productoBaja.js` y
  `core_producto.py` concentran las reglas de negocio, testeables sin
  React ni HTTP.
- **Regla 4 (tests obligatorios):** la estrategia cubre los diez RF de la
  spec.
- **Regla 5 (persistencia única):** todo pasa por
  `repository_producto.py`/`database.py`.
- **Regla 6 (idioma consistente):** identificadores en inglés
  (`find_by_sku`, `deactivate_by_sku`, `ProductoBajaForm.jsx`); mensajes en
  español ("Producto dado de baja exitosamente", "El producto ya se
  encuentra dado de baja").
