# Tasks 013 — Validación Amigable de Formularios

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: reglas y mensajes

- [x] **T01 — Relajar `_EMAIL_PATTERN` en `core.py`**
  Cambiar el regex de `validate_email` para no exigir un punto en el
  dominio (`usuario@dominio`, con o sin TLD), con sus tests unitarios.
  [Cubre RF-3]
  Hecho cuando: `pytest -q -k validate_email` pasa, cubriendo
  `usuario@dominio` (sin punto, ahora válido), `usuario@dominio.com`
  (con punto, sigue válido), y casos inválidos (sin arroba, con
  espacios, más de una arroba).

- [x] **T02 — Mensajes específicos de DNI/Teléfono/Email en `routes/clientes.py`**
  Actualizar `INVALID_DNI_MESSAGE`, `INVALID_PHONE_MESSAGE` e
  `INVALID_EMAIL_MESSAGE` con la redacción de la spec.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k alta_cliente` y `pytest -q -k
  editar_cliente` pasan, verificando los tres mensajes nuevos en
  ambos endpoints (comparten `_validate_fields`).

- [x] **T03 — Tests de integración del email relajado**
  Confirmar que `POST /clientes` y `PUT /clientes/{dni}/editar` con un
  email sin punto en el dominio responden 201/200 en vez de 422.
  [Cubre RF-3]
  Hecho cuando: `pytest -q -k email_sin_tld` pasa para ambos endpoints.

## Fase 1 — Frontend: reglas puras

- [x] **T04 — Sincronizar `validation.js` con el Backend**
  Actualizar `EMAIL_PATTERN`, `INVALID_DNI_MESSAGE`,
  `INVALID_PHONE_MESSAGE` e `INVALID_EMAIL_MESSAGE`, con sus tests
  unitarios.
  [Cubre RF-1, RF-2, RF-3]
  Hecho cuando: `npm run test -- validation` pasa, cubriendo los
  mismos casos que T01 (email con/sin punto) y los mensajes nuevos de
  DNI/teléfono.

- [x] **T05 — `validateQuantityFormat` en `ventaDetalle.js`**
  Extraer la regla de "entero positivo" ya usada dentro de `addItem` a
  una función pura independiente, con sus tests unitarios.
  [Cubre RF-6]
  Hecho cuando: `npm run test -- ventaDetalle` pasa, cubriendo
  `"abc"`/`"0"`/`"-1"`/`"5.5"` (devuelven el mensaje) y `"3"` (devuelve
  `null`), y `addItem` sigue pasando sus tests existentes sin cambios
  de comportamiento.

## Fase 2 — Frontend: blur en Cliente

- [x] **T06 — `handleBlur` en `ClienteForm.jsx`**
  Agregar el manejador que, si el campo no está vacío, corre
  `validateClienteForm` y aplica/limpia solo el error de ese campo;
  conectarlo al `onBlur` de cada input de `CLIENTE_FIELDS`.
  [Cubre RF-4, RF-7, RF-9]
  Hecho cuando: un test de RTL escribe un DNI inválido, pasa el foco al
  campo Nombre, y ve el mensaje de inmediato sin haber tocado
  "Registrar cliente".

- [x] **T07 — Campo vacío no marca error al perder el foco (`ClienteForm.jsx`)**
  [Cubre RF-7]
  Hecho cuando: un test de RTL enfoca y desenfoca un campo vacío (sin
  escribir nada) y confirma que no aparece ningún mensaje de error.

- [x] **T08 — Corregir y volver a perder el foco limpia el error (`ClienteForm.jsx`)**
  [Cubre RF-9]
  Hecho cuando: un test de RTL muestra el error de blur, corrige el
  valor, pierde el foco de nuevo, y confirma que el mensaje
  desaparece.

- [x] **T09 — El envío sigue validando todo (`ClienteForm.jsx`)**
  Confirmar que ningún test existente de submit se rompió al agregar
  el blur.
  [Cubre RF-8]
  Hecho cuando: los tests de `ClienteForm.test.jsx` ya existentes para
  el envío del formulario siguen pasando sin modificaciones.

- [x] **T10 — Repetir T06 a T08 en `ClienteEdicionForm.jsx`**
  Mismo `handleBlur`, conectado a los inputs de `CLIENTE_FIELDS` dentro
  del formulario de edición.
  [Cubre RF-4, RF-7, RF-9]
  Hecho cuando: `npm run test -- ClienteEdicionForm` pasa, cubriendo
  los mismos tres casos (blur con error, campo vacío, corrección) que
  T06-T08.

## Fase 3 — Frontend: blur en Producto

- [x] **T11 — `handleBlur` en `ProductoForm.jsx`**
  Mismo patrón que T06, con `validateProductoForm` sobre
  `PRODUCTO_FIELDS` (foco en "Precio unitario" y "Stock").
  [Cubre RF-5, RF-7, RF-9]
  Hecho cuando: un test de RTL escribe un precio unitario inválido
  (ej. `"abc"`), pasa el foco a "Stock", y ve el mensaje de inmediato
  sin haber tocado "Registrar producto".

- [x] **T12 — Campo vacío y corrección en `ProductoForm.jsx`**
  [Cubre RF-7, RF-9]
  Hecho cuando: un test de RTL confirma que un campo vacío no marca
  error al perder el foco, y que corregir un valor inválido y volver a
  perder el foco limpia el mensaje.

- [x] **T13 — Repetir T11-T12 en `ProductoEdicionForm.jsx`**
  Mismo `handleBlur`, con `validateProductoEdicionForm` sobre
  `PRODUCTO_EDICION_FIELDS`.
  [Cubre RF-5, RF-7, RF-9]
  Hecho cuando: `npm run test -- ProductoEdicionForm` pasa, cubriendo
  los mismos casos que T11-T12.

## Fase 4 — Frontend: blur en Venta

- [x] **T14 — `onBlur` de "Cantidad" en `VentaForm.jsx`**
  Al perder el foco, si el valor no está vacío, correr
  `validateQuantityFormat` y mostrar el mensaje en `itemError` si no es
  válido; el `onChange` de "Cantidad" limpia `itemError` solo si su
  valor actual es el mensaje de cantidad inválida.
  [Cubre RF-6, RF-7, RF-9]
  Hecho cuando: un test de RTL escribe una cantidad inválida (ej.
  `"0"`) y pasa el foco fuera del campo, viendo el mensaje antes de
  hacer clic en "Agregar".

- [x] **T15 — El error de blur de Cantidad no pisa un error de SKU vigente**
  [Cubre RF-9]
  Hecho cuando: un test de RTL deja un error de "Producto no
  encontrado" mostrado, después escribe una cantidad válida en el
  campo Cantidad y le quita el foco, y confirma que el mensaje de SKU
  sigue visible (no se borró).

- [x] **T16 — Repetir T14-T15 en `VentaEdicionForm.jsx`**
  Mismo comportamiento en el armado de ítems del formulario de edición
  de venta.
  [Cubre RF-6, RF-7, RF-9]
  Hecho cuando: `npm run test -- VentaEdicionForm` pasa, cubriendo los
  mismos dos casos que T14-T15.

## Fase 5 — Verificación final

- [x] **T17 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-9 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-9]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck`
  terminan sin errores ni tests saltados, y cada RF de la spec tiene un
  test correspondiente pasando.
