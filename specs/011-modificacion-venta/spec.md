# Spec 011 — Modificación de Venta

## Contexto y objetivo
Esta spec cambia de forma sustancial el ciclo de vida de una venta
establecido en [[009-alta-venta]]. Hasta ahora, registrar una venta era
un único paso atómico: se armaba el detalle y, al confirmar, el sistema
la registraba directamente en estado "Confirmada" y descontaba el stock
en el mismo momento (RF-13 a RF-15 de [[009-alta-venta]]).

A partir de esta spec, ese único paso se divide en dos:

1. **Registrar** una venta ahora la crea en un nuevo estado, "Borrador",
   con su detalle inicial, pero **sin descontar stock todavía**.
2. Mientras está en "Borrador", el Administrador puede **editar su
   detalle** las veces que necesite (agregar, quitar o ajustar
   cantidades de productos), para ajustarlo antes del cierre definitivo.
3. Recién al **cerrar** la venta (una acción nueva que introduce esta
   spec) el sistema la pasa a "Confirmada" y descuenta el stock — el
   mismo efecto que antes ocurría de inmediato al registrar.

El objetivo es que el Administrador pueda ajustar una venta que todavía
no se cerró, en vez de tener que anularla ([[010-anular-venta]]) y
registrar una nueva si se equivocó en los productos o cantidades.

## Usuarios
- **Administrador**: único rol que modifica y cierra ventas en esta
  feature.

## Historias de usuario

### HU-VEN-03: Modificación de Venta
Como Administrador
Quiero modificar el detalle de una venta no finalizada
Para ajustar los productos o cantidades antes del cierre definitivo.

## Requisitos funcionales

### RF-1: Registro de venta en estado "Borrador"
El registro de una venta (mismas validaciones de cliente y de ítems ya
definidas en [[009-alta-venta]] RF-1 a RF-12) ya no la confirma ni
descuenta stock de inmediato.

- CUANDO el Administrador registra una nueva venta con un cliente Activo
  válido y un detalle válido, EL SISTEMA deberá crear la venta en estado
  "Borrador", con su ID, fecha y total calculado, sin descontar el stock
  de ningún producto.

### RF-2: Búsqueda de venta por ID para editar su detalle
El sistema deberá permitir al Administrador buscar una venta ingresando
su ID, como paso previo a editar su detalle.

- CUANDO el Administrador ingresa un ID de venta y solicita la
  búsqueda, EL SISTEMA deberá localizar la venta registrada cuyo ID
  coincida con el ingresado.

### RF-3: Venta no encontrada
- SI no existe ninguna venta registrada con el ID buscado, ENTONCES EL
  SISTEMA deberá advertir que la venta no fue encontrada.

### RF-4: Solo se edita el detalle de una venta en "Borrador"
- SI la venta localizada no se encuentra en estado "Borrador" (por
  ejemplo, porque ya está "Confirmada" o "Anulada"), ENTONCES EL
  SISTEMA deberá advertir que la venta ya no admite modificaciones y no
  deberá mostrar su detalle como editable.

### RF-5: Reemplazo completo del detalle
El sistema deberá permitir al Administrador reemplazar el detalle
completo de una venta en "Borrador" (agregando, quitando o ajustando la
cantidad de sus productos), enviando la lista completa de ítems
deseada.

- CUANDO el Administrador guarda una nueva lista de ítems para una
  venta en "Borrador", EL SISTEMA deberá reemplazar el detalle anterior
  por el nuevo.

### RF-6: Bloqueo de productos inactivos al editar el detalle
- SI algún producto de la nueva lista de ítems se encuentra en estado
  Inactivo, ENTONCES EL SISTEMA deberá advertir que ese producto no está
  disponible para la venta y no deberá guardar los cambios del detalle.

### RF-7: Validación de stock disponible por ítem al editar
- SI la cantidad de un ítem de la nueva lista supera el stock
  actualmente disponible de ese producto, ENTONCES EL SISTEMA deberá
  advertir que no hay stock suficiente para completar la operación y no
  deberá guardar los cambios del detalle.

### RF-8: Cantidad positiva por ítem al editar
- SI la cantidad de algún ítem de la nueva lista no es un número entero
  positivo, ENTONCES EL SISTEMA deberá advertir que el valor debe ser un
  número positivo y no deberá guardar los cambios del detalle.

### RF-9: Reporte completo de errores al guardar el detalle
- CUANDO se intenta guardar una nueva lista de ítems con más de un
  problema a la vez, ENTONCES EL SISTEMA deberá mostrar todas las
  advertencias correspondientes en el mismo intento y no deberá
  modificar el detalle anterior.

### RF-10: Recalculo automático del total
- CUANDO se guarda una nueva lista de ítems válida, EL SISTEMA deberá
  recalcular el total de la venta como la suma de cantidad por precio
  unitario de cada ítem, sin permitir que el Administrador lo ingrese
  manualmente. El precio unitario de cada ítem se toma del precio
  actual del producto en el momento de guardarlo en el detalle (mismo
  criterio que [[009-alta-venta]] RF-7).

### RF-11: El borrador admite un detalle vacío
- EL SISTEMA permitirá guardar una venta en "Borrador" con un detalle
  vacío (sin ítems); la exigencia de tener al menos un ítem aplica
  únicamente al cerrar la venta (RF-13), no a cada guardado intermedio.

### RF-12: Cierre de la venta
- CUANDO el Administrador confirma el cierre de una venta en estado
  "Borrador" con al menos un ítem válido en su detalle y stock
  disponible suficiente para cada uno (RF-16), EL SISTEMA deberá cambiar
  su estado a "Confirmada" y descontar automáticamente del stock de
  cada producto la cantidad correspondiente a su ítem —el mismo efecto
  que, antes de esta spec, ocurría de inmediato al registrar la venta en
  [[009-alta-venta]].

### RF-13: Al menos un ítem para poder cerrar
- SI el Administrador intenta cerrar una venta en "Borrador" sin ningún
  ítem en su detalle, ENTONCES EL SISTEMA deberá advertir que la venta
  debe tener al menos un ítem y no deberá cerrarla.

### RF-14: Verificación del estado al cerrar
- SI al momento de confirmar el cierre la venta ya no se encuentra en
  estado "Borrador" (por ejemplo, porque ya fue cerrada o anulada por
  otra vía entre la búsqueda y la confirmación), ENTONCES EL SISTEMA
  deberá advertir la situación y no deberá volver a descontar stock ni
  cambiar el estado (mismo motivo por el que [[010-anular-venta]] RF-7
  re-verifica antes de aplicar un cambio con efecto sobre el stock).

### RF-15: Persistencia sin eliminación
- EL SISTEMA nunca eliminará el registro de una venta ni de sus ítems
  como parte de la edición del detalle o del cierre; solo se reemplaza
  el detalle (RF-5) o se modifica su estado (RF-12).

### RF-16: Verificación de stock al cerrar
Dado que el stock nunca se reserva mientras una venta permanece en
"Borrador" (ver "Fuera de alcance"), el sistema debe volver a comprobar,
en el momento del cierre, que el stock disponible de cada producto
todavía alcanza para la cantidad de su ítem, antes de descontarlo.

- SI al momento de confirmar el cierre el stock disponible de algún
  producto ya no alcanza para la cantidad de su ítem (por ejemplo,
  porque se consumió con otra venta cerrada mientras esta seguía en
  "Borrador"), ENTONCES EL SISTEMA deberá advertir que no hay stock
  suficiente para completar la operación y no deberá cerrar la venta ni
  descontar stock de ningún producto.

## Requisitos no funcionales
- Todos los mensajes de advertencia y confirmación dirigidos al
  Administrador deben estar en español.
- El reemplazo del detalle y el cierre de una venta deben persistirse de
  forma consistente en la base de datos oficial del proyecto (mismo
  criterio de atomicidad que [[009-alta-venta]] y [[010-anular-venta]]).

## Casos límite
- Editar el detalle de una venta ya "Confirmada" o "Anulada": bloqueado
  por RF-4.
- Guardar un detalle nuevo que quita todos los ítems: permitido, la
  venta queda en "Borrador" con el detalle vacío (RF-11).
- Cerrar una venta en "Borrador" con el detalle vacío: bloqueado por
  RF-13.
- Intentar cerrar una venta que fue cerrada o anulada por otra vía entre
  la búsqueda y la confirmación del cierre: bloqueado por RF-14, sin
  duplicar el descuento de stock.
- Reemplazar el detalle con un producto que se dio de baja
  (Inactivo) después de haberlo agregado originalmente: bloqueado por
  RF-6 si ese producto sigue en la nueva lista enviada.
- Intentar cerrar una venta cuyo stock disponible se consumió con otra
  venta cerrada mientras esta permanecía en "Borrador" (el stock nunca
  se reserva durante la edición): bloqueado por RF-16, sin cerrar la
  venta ni descontar stock de ningún ítem.

## Fuera de alcance
- Eliminar o descartar un borrador sin cerrarlo (queda para una feature
  futura).
- Reactivar una venta "Anulada" (fuera de alcance también de
  [[010-anular-venta]]).
- Reserva de stock durante el tiempo que una venta permanece en
  "Borrador" (el stock recién se descuenta al cerrar, RF-12; hasta
  entonces, otros borradores o ventas pueden competir por el mismo
  stock disponible).
- Historial de auditoría de los cambios sucesivos al detalle de un
  borrador.
- Notificación al cliente sobre cambios en su venta.
- Autenticación y gestión de roles de usuario (se asume que el sistema
  ya identifica quién opera como Administrador).

## Criterios de finalización
- Registrar una venta la crea en estado "Borrador", sin descontar stock
  (RF-1).
- Un Administrador puede buscar una venta en "Borrador" por ID y
  reemplazar su detalle completo (agregando, quitando o ajustando
  cantidades), con el total recalculado automáticamente (RF-2, RF-5,
  RF-10).
- Un producto Inactivo, sin stock suficiente, o con cantidad inválida en
  la nueva lista de ítems bloquea el guardado del detalle, mostrando
  todas las advertencias del intento juntas (RF-6, RF-7, RF-8, RF-9).
- Una venta en "Borrador" y con al menos un ítem, y con stock disponible
  suficiente para cada uno en el momento del cierre, puede cerrarse,
  quedando "Confirmada" y con el stock de cada producto descontado
  (RF-12, RF-16).
- Una venta en "Borrador" sin ítems no puede cerrarse (RF-13); una venta
  que ya no está en "Borrador" no puede editarse (RF-4) ni volver a
  cerrarse (RF-14); una venta cuyo stock disponible ya no alcanza para
  algún ítem no puede cerrarse (RF-16).
- Todos los criterios de aceptación de HU-VEN-03 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Se resolvió que, al cerrar una venta en
"Borrador", el sistema re-verifica que el stock actual alcance para cada
ítem antes de descontarlo (RF-16); si no alcanza para alguno, se
rechaza el cierre sin modificar el estado de la venta ni el stock de
ningún producto (verificación atómica de todo-o-nada, previa a aplicar
cualquier descuento).
