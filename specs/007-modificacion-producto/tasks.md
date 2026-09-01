# Tasks 007 — Modificación de Producto

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: repositorio

- [x] **T01 — `update_product`**
  Agregar en `repository_producto.py` la función que actualiza `name`,
  `brand`, `description`, `unit_price`, `stock`, sin tocar `sku` ni
  `status`, con tests de integración.
  [Cubre RF-6, RF-7, RF-8]
  Hecho cuando: `pytest -q -k update_product` pasa, cubriendo un producto
  Activo y uno Inactivo (el `status` no cambia en ninguno de los dos
  casos, ni el `sku`).

## Fase 1 — Backend: endpoint

- [x] **T02 — Endpoint `PUT /productos/{sku}/editar`: camino feliz y no encontrado**
  Implementar la ruta con sus propias `_normalize_edit_payload`/
  `_validate_edit_fields` (reutilizando `core.trim_leading_trailing_space`
  y `core_producto.validate_positive_number`/`validate_positive_integer`,
  sin tocar las funciones del alta).
  [Cubre RF-1, RF-2, RF-6]
  Hecho cuando: `pytest -q -k editar_producto_endpoint` pasa para edición
  exitosa (sobre Activo e Inactivo) y para SKU inexistente (404).

- [x] **T03 — Endpoint: campos obligatorios y Precio/Stock inválidos**
  Cubrir en el endpoint los 4 campos obligatorios (Nombre, Marca, Precio,
  Stock — sin incluir SKU) y la validación de número/entero positivo.
  [Cubre RF-4]
  Hecho cuando: un test con los 4 campos vacíos devuelve las 4
  advertencias, y tests con `unit_price`/`stock` en cero, negativo, no
  numérico y (para `stock`) con decimales devuelven la misma advertencia
  de "número positivo".

- [x] **T04 — Endpoint: SKU ignorado en el body y reporte combinado**
  Confirmar que un `sku` incluido en el payload de edición se ignora, y
  que múltiples errores a la vez se reportan juntos sin guardar nada.
  [Cubre RF-5, RF-7]
  Hecho cuando: un test que envía `sku` distinto en el body confirma que
  el SKU del producto no cambia, y otro test con dos campos inválidos a
  la vez devuelve ambas advertencias.

## Fase 2 — Frontend: campos y validación

- [x] **T05 — `PRODUCTO_EDICION_FIELDS`**
  Agregar en `productoFields.js` el array derivado de `PRODUCTO_FIELDS`
  filtrando el campo `sku`.
  [Cubre RF-3, RF-7]
  Hecho cuando: `npm run typecheck` pasa sin errores.

- [x] **T06 — `productoEdicion.js`**
  Crear el módulo puro que interpreta el resultado de la búsqueda (no
  encontrado / encontrado), con tests unitarios sin React.
  [Cubre RF-1, RF-2]
  Hecho cuando: `npm run test -- productoEdicion` pasa, cubriendo ambos
  estados.

- [x] **T07 — `validateProductoEdicionForm`**
  Agregar en `validationProducto.js` la función nueva (no modifica
  `validateProductoForm`), con tests unitarios.
  [Cubre RF-4, RF-5]
  Hecho cuando: `npm run test -- validationProducto` sigue en verde
  (incluidos los tests existentes de `validateProductoForm`) y cubre
  además la obligatoriedad de los 4 campos de edición (sin exigir `sku`),
  `unit_price`/`stock` inválidos y varios errores juntos.

## Fase 3 — Frontend: API y componente

- [x] **T08 — `editarProducto` en `productosApi.js`**
  Implementar la función que llama a `PUT /productos/{sku}/editar`, con
  tests con `fetch` mockeado.
  [Cubre RF-6]
  Hecho cuando: `npm run test -- productosApi` pasa, cubriendo una
  respuesta 200 y una 422.

- [x] **T09 — Esqueleto de `ProductoEdicionForm.jsx`: búsqueda y formulario pre-cargado**
  Input de SKU + botón de búsqueda; al encontrar, mostrar el formulario
  con los 5 campos editables (usando `PRODUCTO_EDICION_FIELDS`) y el SKU
  como texto de solo lectura; al no encontrarlo, mostrar el mensaje de
  `productoEdicion.js`.
  [Cubre RF-1, RF-2, RF-3, RF-7]
  Hecho cuando: un test de RTL confirma ambos casos, y que el SKU se
  muestra como texto (no dentro de un `<input>`).

- [x] **T10 — Validación inmediata antes de guardar**
  Integrar `validateProductoEdicionForm`: al enviar, si hay errores,
  mostrarlos de inmediato sin llamar a `editarProducto`.
  [Cubre RF-4, RF-5]
  Hecho cuando: un test de RTL con un campo inválido confirma las
  advertencias y que `editarProducto` no fue invocada.

- [x] **T11 — Guardado exitoso**
  Conectar el envío válido a `editarProducto`: mostrar "Producto
  modificado exitosamente" y volver al estado de búsqueda.
  [Cubre RF-6]
  Hecho cuando: un test de RTL con `editarProducto` mockeado devolviendo
  éxito confirma el mensaje y que el formulario de edición desaparece
  (vuelve a la búsqueda).

## Fase 4 — Integración de navegación

- [x] **T12 — Pestaña "Editar Producto" en `App.jsx`**
  Agregar la séptima pestaña junto a las seis existentes.
  [Soporte - sin RF directo]
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar hacia la nueva pestaña.

## Fase 5 — Verificación final

- [x] **T13 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-8 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-8]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada RF de la spec tiene un test
  correspondiente pasando.
