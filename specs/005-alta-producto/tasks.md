# Tasks 005 — Alta de Producto

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: núcleo de validación (`core_producto.py`)

- [x] **T01 — `validate_positive_number`**
  Crear `core_producto.py` con la función que valida que un valor sea un
  número positivo (rechaza no numéricos, cero y negativos), con sus tests
  unitarios.
  [Cubre RF-3]
  Hecho cuando: `pytest -q -k validate_positive_number` pasa, cubriendo
  `"350.50"` (válido), `"0"`, `"-5"` y `"abc"` (los tres inválidos).

- [x] **T02 — `validate_positive_integer`**
  Agregar la función que valida que un valor sea un entero positivo
  (rechaza no numéricos, decimales, cero y negativos), con sus tests
  unitarios.
  [Cubre RF-4]
  Hecho cuando: `pytest -q -k validate_positive_integer` pasa, cubriendo
  `"100"` (válido), `"0"`, `"-1"`, `"5.5"` y `"abc"` (los cuatro
  inválidos).

## Fase 1 — Backend: modelo y persistencia

- [x] **T03 — Modelo `Product`**
  Agregar la clase `Product` (tabla `products`) a `models.py`, con las
  columnas de `plan.md` (`sku` único e indexado, `name`, `brand`,
  `description` nullable, `unit_price` Float, `stock` Integer).
  [Cubre RF-1 a RF-5]
  Hecho cuando: un test confirma que `Base.metadata.create_all(engine)`
  crea la tabla `products` sin errores sobre una base SQLite temporal.

- [x] **T04 — `sku_exists`**
  Crear `repository_producto.py` con la función que detecta un SKU ya
  registrado sin distinguir mayúsculas (`func.lower()`), con tests de
  integración.
  [Cubre RF-5]
  Hecho cuando: `pytest -q -k sku_exists` pasa, cubriendo SKU exacto
  duplicado, SKU duplicado con distinta capitalización y SKU no
  registrado (`False`).

- [x] **T05 — `create_product`**
  Agregar la función que inserta un producto nuevo, con test de
  integración cubriendo una `description` vacía/ausente.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k create_product` pasa, verificando que el
  producto persiste con los valores ingresados.

## Fase 2 — Backend: endpoint

- [x] **T06 — Endpoint `POST /productos`: camino feliz y campos obligatorios**
  Crear `routes/productos.py`: recorta y valida los 5 campos obligatorios
  (reutilizando el patrón de `_normalize_payload`/`_validate_fields` de
  `routes/clientes.py`, adaptado a los campos de Producto), y completa el
  alta exitosa.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k alta_producto_exitosa` pasa (con y sin
  `description`), y un envío con los 5 campos obligatorios vacíos devuelve
  las 5 advertencias correspondientes.

- [x] **T07 — Endpoint: validación de `unit_price` y `stock`**
  Integrar `validate_positive_number`/`validate_positive_integer` en el
  endpoint.
  [Cubre RF-3, RF-4]
  Hecho cuando: tests de integración confirman que `unit_price` en `"0"`,
  negativo y no numérico, y `stock` en `"0"`, negativo, `"5.5"` y no
  numérico, devuelven la misma advertencia de "número positivo" cada uno.

- [x] **T08 — Endpoint: SKU duplicado y reporte combinado**
  Integrar `sku_exists` en el endpoint; confirmar que múltiples errores a
  la vez se reportan juntos, sin crear el producto.
  [Cubre RF-5, RF-6]
  Hecho cuando: un test de integración con SKU duplicado (incluida una
  variante con mayúsculas distintas) bloquea el alta, y otro con
  `unit_price` negativo + SKU duplicado a la vez devuelve ambas
  advertencias en un mismo intento.

- [x] **T09 — Registrar el router de productos en `main.py`**
  Incluir `routes/productos.py` en la app de `main.py`, junto al de
  clientes.
  [Soporte - sin RF directo]
  Hecho cuando: `pytest -q -k test_main` pasa, confirmando que
  `POST /productos` aparece entre las rutas expuestas por la app.

## Fase 3 — Frontend: campos y validación

- [x] **T10 — `productoFields.js`**
  Crear el módulo con la metadata de los 6 campos (label, hint), análogo a
  `clienteFields.js`.
  [Cubre RF-1, RF-2]
  Hecho cuando: `npm run typecheck` pasa sin errores sobre el nuevo
  archivo.

- [x] **T11 — `validationProducto.js`**
  Crear el módulo puro que replica las reglas de `core_producto.py`
  (obligatoriedad de los 5 campos requeridos, `unit_price`/`stock`
  positivos), con sus tests unitarios sin React.
  [Cubre RF-2, RF-3, RF-4]
  Hecho cuando: `npm run test -- validationProducto` pasa, cubriendo
  campos vacíos, `unit_price`/`stock` inválidos y varios errores juntos en
  un mismo intento.

## Fase 4 — Frontend: API y componente

- [x] **T12 — `altaProducto` en `productosApi.js`**
  Crear el módulo con la función que llama a `POST /productos`, con tests
  con `fetch` mockeado.
  [Cubre RF-1, RF-6]
  Hecho cuando: `npm run test -- productosApi` pasa, cubriendo una
  respuesta de éxito y una de error.

- [x] **T13 — Esqueleto de `ProductoForm.jsx`**
  Formulario con los 6 campos (usando `productoFields.js`), validación
  inmediata con `validationProducto.js` antes de llamar a la API.
  [Cubre RF-2, RF-3, RF-4]
  Hecho cuando: un test de RTL con el formulario vacío muestra las 5
  advertencias de obligatoriedad (sin incluir `description`) y
  `altaProducto` no se invoca.

- [x] **T14 — Éxito y conservación de valores ante error del backend**
  Conectar el envío a `productosApi.js`: mostrar "Producto registrado
  exitosamente" y limpiar el formulario ante éxito; mostrar las
  advertencias del backend (ej. SKU duplicado) y conservar los valores
  ingresados ante un error.
  [Cubre RF-1, RF-5, RF-6]
  Hecho cuando: un test de RTL simulando éxito confirma el mensaje y el
  formulario vacío, y otro simulando un rechazo por SKU duplicado
  confirma la advertencia y que los valores ingresados no se pierden.

## Fase 5 — Integración de navegación

- [x] **T15 — Pestaña "Alta de Producto" en `App.jsx`**
  Agregar la quinta pestaña junto a las cuatro de Cliente.
  [Soporte - sin RF directo]
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar hacia la nueva pestaña.

## Fase 6 — Verificación final

- [x] **T16 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-7 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-7]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada RF de la spec tiene un test
  correspondiente pasando.
