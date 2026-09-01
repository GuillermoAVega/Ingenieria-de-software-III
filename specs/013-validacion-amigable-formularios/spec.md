# Spec 013 — Validación Amigable de Formularios

## Contexto y objetivo
Esta spec no nace de una nueva historia de usuario del negocio, sino de
feedback directo del Administrador sobre la experiencia de uso de los
formularios ya construidos ([[001-alta-cliente]],
[[003-modificacion-cliente]], [[005-alta-producto]],
[[007-modificacion-producto]], [[009-alta-venta]],
[[011-modificacion-venta]]). Se identificaron tres mejoras concretas:

1. Varios mensajes de error de formato son genéricos ("El formato del
   DNI es inválido") en vez de decir explícitamente qué se espera.
2. Todos los formularios validan recién al enviar (o al presionar
   "Agregar" en Venta); un campo con formato inválido no se avisa hasta
   ese momento, aunque el Administrador ya haya terminado de escribirlo
   y pasado al siguiente campo.
3. La validación de email exige un punto en el dominio (TLD), cuando el
   criterio real debería ser solo la estructura `usuario@dominio`
   (un dominio con punto, como `dominio.com`, también la cumple y se
   sigue aceptando).

Una cuarta mejora propuesta en la misma conversación —reactivar
automáticamente a un cliente Inactivo al reintentar el alta con su
DNI— **se evaluó y se descarta explícitamente** para esta ronda (ver
"Fuera de alcance").

El objetivo de esta spec es mejorar los mensajes de formato y adelantar
su aviso al momento en que el Administrador termina de completar cada
campo, sin cambiar ninguna regla de negocio de fondo (qué es válido
sigue siendo lo mismo, salvo el email).

## Usuarios
- **Administrador**: único rol que completa estos formularios.

## Alcance: qué formularios se ven afectados
Se relevó la arquitectura actual de los seis formularios con reglas de
formato conocidas de antemano (sin depender de una búsqueda al
servidor):

- `ClienteForm.jsx` (alta) y `ClienteEdicionForm.jsx` (edición):
  comparten los 5 campos de `CLIENTE_FIELDS` y la función pura
  `validateClienteForm`.
- `ProductoForm.jsx` (alta) y `ProductoEdicionForm.jsx` (edición):
  comparten `PRODUCTO_FIELDS`/`PRODUCTO_EDICION_FIELDS` y las funciones
  puras `validateProductoForm`/`validateProductoEdicionForm`.
- El campo "Cantidad" del armado de ítems en `VentaForm.jsx` y
  `VentaEdicionForm.jsx`: tiene una regla de formato propia (entero
  positivo) independiente de la búsqueda de producto.

Quedan fuera los campos de búsqueda de un solo valor (DNI en Anular/
Editar Cliente y Venta, SKU en Baja/Editar Producto, ID en Anular/
Modificar Venta): hoy no tienen una regla de formato propia, solo se
resuelven contra el backend ("no encontrado"/"encontrado"), así que no
hay nada que adelantar. Ver "Fuera de alcance".

## Historias de usuario

### HU-SYS-05: Validación amigable de formularios
Como Administrador
Quiero que los formularios me avisen con mensajes claros y apenas
termino de completar cada campo si algo está mal
Para corregir mis datos más rápido, sin tener que enviar el formulario
para enterarme.

## Requisitos funcionales

### RF-1: Mensaje específico para el formato del DNI (Cliente)
- SI el DNI ingresado (en alta o edición de Cliente) no tiene el
  formato esperado, ENTONCES EL SISTEMA deberá advertir "El DNI debe
  contener solo números (7 u 8 dígitos)", en vez del mensaje genérico
  actual.

### RF-2: Mensaje específico para el formato del Teléfono (Cliente)
- SI el teléfono ingresado (en alta o edición de Cliente) no tiene el
  formato esperado, ENTONCES EL SISTEMA deberá advertir "El teléfono
  debe contener solo números y guiones", en vez del mensaje genérico
  actual.

### RF-3: Validación de email sin exigir TLD
Se reemplaza el criterio de validación de email definido en
[[001-alta-cliente]] RF-3 (y heredado por [[003-modificacion-cliente]]):
ya no se exige un punto en el dominio.

- CUANDO el email ingresado tiene la estructura `usuario@dominio` (una
  única arroba, con texto no vacío y sin espacios antes y después),
  EL SISTEMA deberá aceptarlo como válido, tenga o no un punto en el
  dominio (`usuario@dominio` y `usuario@dominio.com` son ambos
  válidos).
- SI el email no cumple esa estructura (sin arroba, con espacios, con
  parte local o dominio vacíos), ENTONCES EL SISTEMA deberá advertir
  "El email debe tener el formato usuario@dominio".
- Esta validación se actualiza tanto en el Backend
  (`core.validate_email`, autoridad final) como en el Frontend
  (`validation.js`, feedback inmediato), manteniendo el mismo criterio
  en ambos.

### RF-4: Aviso de formato al perder el foco (Cliente)
- CUANDO el Administrador completa un campo de `ClienteForm` o
  `ClienteEdicionForm` con algún contenido y pasa a otro campo (el
  campo pierde el foco), EL SISTEMA deberá validar el formato de ese
  campo de inmediato y, si no es válido, mostrar su mensaje de error
  sin esperar a que se envíe el formulario.

### RF-5: Aviso de formato al perder el foco (Producto)
- Mismo comportamiento que RF-4, aplicado a los campos "Precio
  unitario" y "Stock" de `ProductoForm` y `ProductoEdicionForm`.

### RF-6: Aviso de formato al perder el foco (Cantidad en Venta)
- Mismo comportamiento que RF-4, aplicado al campo "Cantidad" del
  armado de ítems en `VentaForm` y `VentaEdicionForm`: si al perder el
  foco el valor cargado no es un número entero positivo, EL SISTEMA
  deberá mostrar el mensaje correspondiente antes de que el
  Administrador presione "Agregar".

### RF-7: Un campo vacío no se marca como error al perder el foco
- SI el Administrador deja un campo vacío y pasa a otro sin haber
  escrito nada, ENTONCES EL SISTEMA no deberá mostrar ningún error en
  ese campo todavía; la exigencia de campo obligatorio sigue
  aplicándose recién al enviar el formulario (o presionar "Agregar" en
  Venta), como hasta ahora.

### RF-8: La validación final al enviar no se elimina
- EL SISTEMA deberá seguir validando todos los campos al enviar el
  formulario (o al presionar "Agregar" en Venta), sin importar si ya
  se validaron individualmente al perder el foco; el aviso por campo
  (RF-4 a RF-6) complementa la validación final, no la reemplaza.

### RF-9: Corregir un campo limpia su error de inmediato
- CUANDO el Administrador modifica el valor de un campo que tiene un
  error mostrado (ya sea por RF-4/RF-5/RF-6 o por el envío del
  formulario), EL SISTEMA deberá quitar ese error apenas empieza a
  escribir de nuevo, sin esperar a que vuelva a perder el foco
  (comportamiento ya existente, se preserva explícitamente).

## Requisitos no funcionales
- Todos los mensajes de validación deben estar en español y ser
  específicos sobre qué formato se espera (no genéricos como "Formato
  inválido").
- La regla de validación de cada campo debe seguir siendo la misma en
  Backend y Frontend (el Backend sigue siendo la autoridad final ante
  cualquier discrepancia, mismo criterio que ya documentan
  `validation.js`/`validationProducto.js`).

## Casos límite
- Un valor con espacios al inicio o al final que, tras recortarlos,
  cumple el formato (ej. DNI `" 30111222 "`): no debe marcarse como
  error al perder el foco, mismo criterio de recorte que ya se aplica
  al enviar.
- Pegar un valor inválido con el mouse/teclado y salir del campo con
  Tab o con el mouse: el aviso debe aparecer igual que si se hubiera
  escrito manualmente (se dispara al perder el foco, no al tipear).
- Un campo con error de formato al que el Administrador borra todo su
  contenido y luego le quita el foco: el error de formato desaparece
  (queda vacío), y no aparece "campo obligatorio" hasta el envío
  (RF-7).
- Email sin punto en el dominio (ej. `admin@localhost`): pasa a ser
  válido en esta spec, cuando antes era rechazado (RF-3).
- Email con punto en el dominio (ej. `admin@dominio.com`): sigue siendo
  válido, ya que también cumple la estructura `usuario@dominio` (RF-3).
- Email con más de una arroba (ej. `a@b@c`) o con espacios: sigue
  siendo inválido (RF-3).
- El campo "Cantidad" de Venta con un valor no numérico o negativo,
  perdiendo el foco antes de haber buscado el producto por SKU: se
  avisa igual (RF-6), ya que la regla de formato no depende del
  resultado de esa búsqueda.

## Fuera de alcance
- Reactivar automáticamente a un cliente Inactivo al reintentar el
  alta con su DNI: evaluado en la conversación y descartado
  explícitamente por el Administrador para esta ronda. Queda como una
  posible feature futura, a especificar aparte si se retoma.
- Validación en tiempo real por cada tecla (`onChange`); el aviso
  adelantado de esta spec se dispara únicamente al perder el foco
  (`onBlur`), no mientras se escribe.
- Cambios de mensajes de error en Producto o Venta más allá de agregar
  el aviso por pérdida de foco: sus mensajes actuales ("El valor debe
  ser un número positivo", "El campo es obligatorio") ya son
  específicos y no se modifican.
- Aviso adelantado en los campos de búsqueda de un solo valor (DNI en
  Anular/Editar Cliente y Venta, SKU en Baja/Editar Producto, ID en
  Anular/Modificar Venta): no tienen una regla de formato propia hoy,
  solo se resuelven contra el backend.
- Validar que el dominio del email exista realmente (DNS, MX, etc.);
  se sigue validando solo la estructura sintáctica.
- Rediseño visual de los formularios más allá de mostrar el mensaje de
  error correspondiente.

## Criterios de finalización
- El DNI y el Teléfono de Cliente muestran sus mensajes específicos
  ante un formato inválido, en alta y en edición (RF-1, RF-2).
- Un email con la estructura `usuario@dominio` se acepta con o sin
  punto en el dominio, tanto en Backend como en Frontend, en alta y en
  edición de Cliente (RF-3).
- En `ClienteForm`, `ClienteEdicionForm`, `ProductoForm` y
  `ProductoEdicionForm`, completar un campo con un valor inválido y
  pasar al siguiente muestra el error de inmediato, sin necesidad de
  enviar el formulario (RF-4, RF-5).
- En el armado de ítems de `VentaForm` y `VentaEdicionForm`, completar
  "Cantidad" con un valor inválido y pasar al siguiente campo muestra
  el error de inmediato (RF-6).
- Un campo vacío no muestra ningún error hasta que se envía el
  formulario (o se presiona "Agregar" en Venta) (RF-7).
- El envío del formulario (o "Agregar" en Venta) sigue validando todos
  los campos, incluso los que no perdieron el foco todavía (RF-8).
- Corregir un campo con error limpia ese error apenas se empieza a
  escribir de nuevo (RF-9).
- Todos los criterios de aceptación de HU-SYS-05 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. El alcance (qué formularios y campos se
ven afectados) y la redacción exacta de los mensajes quedaron
definidos arriba, sujetos a la aprobación de esta spec.
