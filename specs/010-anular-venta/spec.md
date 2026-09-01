# Spec 010 — Anular Venta

## Contexto y objetivo
El sistema ya permite registrar ventas ([[009-alta-venta]]), pero no hay
forma de revertir una venta procesada por error o cancelada por el
cliente. El objetivo de esta feature es que el Administrador pueda anular
una venta existente localizándola por su ID, para que su estado pase a
"Anulada" y el stock de cada producto involucrado se reponga
automáticamente. Esta spec introduce el estado "Anulada" en el modelo de
Venta, ya anticipado (sin usarse todavía) desde [[009-alta-venta]].

## Usuarios
- **Administrador**: único rol que anula ventas en esta feature.

## Historias de usuario

### HU-VEN-02: Anular Venta
Como Administrador
Quiero anular una venta registrada
Para revertir una transacción errónea o cancelada por el cliente.

## Requisitos funcionales

### RF-1: Búsqueda de venta por ID
El sistema deberá permitir al Administrador buscar una venta ingresando
su ID, como paso previo a la anulación.

- CUANDO el Administrador ingresa un ID de venta y solicita la
  búsqueda, EL SISTEMA deberá localizar la venta registrada cuyo ID
  coincida con el ingresado.

### RF-2: Venta no encontrada
- SI no existe ninguna venta registrada con el ID buscado, ENTONCES EL
  SISTEMA deberá advertir que la venta no fue encontrada y no deberá
  habilitar ninguna acción de anulación.

### RF-3: Confirmación previa a la anulación
- CUANDO la búsqueda localiza una venta en estado "Confirmada", EL
  SISTEMA deberá solicitar al Administrador que confirme la anulación
  antes de modificarla.

### RF-4: Ejecución de la anulación y reposición de stock
- CUANDO el Administrador confirma la anulación de una venta en estado
  "Confirmada", EL SISTEMA deberá cambiar su estado a "Anulada", mostrar
  el mensaje "Venta anulada exitosamente", y reingresar al stock de cada
  producto involucrado la cantidad correspondiente a su ítem en esa
  venta.

### RF-5: Cancelación de la confirmación
- CUANDO el Administrador cancela la confirmación de anulación, EL
  SISTEMA no deberá modificar el estado de la venta ni el stock de
  ningún producto.

### RF-6: Bloqueo de venta ya anulada al buscarla
- SI la venta localizada ya se encuentra en estado "Anulada", ENTONCES
  EL SISTEMA deberá advertir que la venta ya se encuentra anulada, y no
  deberá solicitar confirmación.

### RF-7: Verificación del estado al confirmar
A diferencia de la baja de cliente ([[002-baja-cliente]] RF-8), la baja
de producto ([[006-baja-producto]] RF-8) y el registro de venta
([[009-alta-venta]] RF-16) —donde se decidió explícitamente no
re-verificar el estado al confirmar—, acá el sistema **sí** debe
comprobar el estado de la venta en el momento de confirmar, porque
aplicar la anulación dos veces sobre la misma venta repondría el stock
dos veces: un error de datos real, no una condición de carrera
tolerable.

- SI al momento de confirmar la anulación la venta ya no se encuentra en
  estado "Confirmada" (por ejemplo, porque ya fue anulada por otra vía
  entre la búsqueda y la confirmación), ENTONCES EL SISTEMA deberá
  advertir que la venta ya se encuentra anulada y no deberá modificar su
  estado ni reponer stock nuevamente.

### RF-8: Persistencia sin eliminación
- EL SISTEMA nunca eliminará el registro de una venta ni de sus ítems
  como parte del proceso de anulación; el proceso de anulación
  únicamente podrá modificar el estado de la venta y el stock de los
  productos involucrados.

## Requisitos no funcionales
- Todos los mensajes de advertencia y confirmación dirigidos al
  Administrador deben estar en español.
- El cambio de estado y la reposición de stock deben persistirse de
  forma consistente en la base de datos oficial del proyecto: si falla
  la anulación, no debe quedar stock repuesto sin que la venta
  correspondiente quede anulada, y viceversa (misma exigencia de
  atomicidad que [[009-alta-venta]]).

## Casos límite
- Intento de anular una venta ya Anulada, detectado en la búsqueda:
  bloqueado por RF-6, sin llegar a pedir confirmación.
- Intento de confirmar la anulación de una venta que fue anulada por
  otra vía entre la búsqueda y la confirmación (condición de carrera):
  bloqueado por RF-7, sin duplicar la reposición de stock.
- Venta con varios ítems: se repone el stock de cada producto por
  separado, según la cantidad de su propio ítem (RF-4).
- Anular una venta cuyo producto fue dado de baja (Inactivo) después de
  la venta: el stock se repone igual, sin importar el estado actual del
  producto.
- El Administrador cancela la confirmación: la venta permanece
  "Confirmada" y el stock no cambia (RF-5).

## Fuera de alcance
- Listado, búsqueda general o filtrado de ventas más allá de la
  búsqueda puntual por ID necesaria para iniciar la anulación (posible
  feature futura, análoga al listado de cliente/producto).
- Revertir una anulación (volver una venta "Anulada" a "Confirmada").
- Restricciones de tiempo para anular (ej. un plazo máximo desde el
  registro de la venta).
- Registro de motivo o comentario asociado a la anulación.
- Notificación al cliente sobre la anulación.
- Historial de auditoría de anulaciones.
- Edición de una venta ya registrada (fuera de alcance también de
  [[009-alta-venta]]).
- Autenticación y gestión de roles de usuario (se asume que el sistema
  ya identifica quién opera como Administrador).

## Criterios de finalización
- Un Administrador puede buscar una venta "Confirmada" por ID y anularla
  tras confirmar, quedando en estado "Anulada" y con el stock de cada
  producto repuesto según su ítem (RF-1, RF-3, RF-4).
- Buscar un ID sin venta asociada advierte "no encontrada" y no habilita
  ninguna acción de anulación (RF-2).
- Intentar anular una venta ya Anulada advierte que ya se encuentra
  anulada, sin modificar nada (RF-6).
- Un intento de confirmar la anulación sobre una venta que ya no está
  "Confirmada" en ese momento se rechaza sin duplicar la reposición de
  stock (RF-7).
- Cancelar la confirmación no modifica el estado de la venta ni el stock
  de ningún producto (RF-5).
- Todos los criterios de aceptación de HU-VEN-02 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Se identificó y resolvió durante la
entrevista una divergencia deliberada respecto al criterio de "sin
re-verificación" usado en las bajas de cliente/producto y en el alta de
venta: acá sí se re-verifica el estado al confirmar (RF-7), porque el
riesgo de no hacerlo (reponer stock dos veces) es un error de datos, no
una condición de carrera tolerable.
