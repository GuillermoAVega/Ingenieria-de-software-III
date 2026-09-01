# Spec 009 — Registrar Alta de Venta

## Contexto y objetivo
El sistema ya gestiona clientes ([[001-alta-cliente]] a [[004-listar-clientes]])
y productos ([[005-alta-producto]] a [[008-listar-productos]]) por
separado, pero no existe ninguna funcionalidad de venta: este es el primer
punto de encuentro entre ambos dominios. El objetivo de esta feature es
que el Administrador pueda registrar una nueva venta asociada a un
cliente, con el detalle de los productos vendidos, para procesar la
transacción y descontar automáticamente el stock involucrado.

## Usuarios
- **Administrador**: único rol que registra ventas en esta feature.

## Historias de usuario

### HU-VEN-01: Registrar Alta de Venta
Como Administrador
Quiero registrar una nueva venta
Para procesar la transacción, descontar el stock y asignarla a un
cliente.

**Datos de la venta**: ID Venta (asignado automáticamente por el
sistema), Cliente (identificado por su DNI), Fecha de venta (asignada
automáticamente por el sistema al confirmarse), Detalle de ítems
(Producto identificado por su SKU, Cantidad, Precio unitario tomado del
producto), Total (calculado automáticamente) y Estado (fijado
automáticamente en "Confirmada" al registrarse).

## Requisitos funcionales

### RF-1: Selección de cliente por DNI
El sistema deberá permitir al Administrador buscar y seleccionar al
cliente de la venta ingresando su DNI.

- CUANDO el Administrador ingresa un DNI y solicita la búsqueda, EL
  SISTEMA deberá localizar al cliente registrado cuyo DNI, comparado por
  su valor numérico (sin considerar ceros a la izquierda), coincida con
  el ingresado.

### RF-2: Cliente no encontrado
- SI no existe ningún cliente registrado con el DNI buscado, ENTONCES EL
  SISTEMA deberá advertir que el cliente no fue encontrado y no deberá
  permitir continuar armando la venta con ese DNI.

### RF-3: Bloqueo de clientes inactivos
- SI el cliente localizado se encuentra en estado Inactivo, ENTONCES EL
  SISTEMA deberá advertir que no se pueden emitir ventas a clientes dados
  de baja y no deberá permitir continuar armando la venta con ese
  cliente.

### RF-4: Selección de producto por SKU
El sistema deberá permitir al Administrador agregar ítems al detalle de
la venta buscando cada producto por su SKU.

- CUANDO el Administrador ingresa un SKU y solicita agregarlo al
  detalle, EL SISTEMA deberá localizar al producto registrado cuyo SKU,
  comparado sin distinguir mayúsculas de minúsculas, coincida con el
  ingresado.

### RF-5: Producto no encontrado
- SI no existe ningún producto registrado con el SKU buscado, ENTONCES
  EL SISTEMA deberá advertir que el producto no fue encontrado y no
  deberá agregarlo al detalle.

### RF-6: Bloqueo de productos inactivos
- SI el producto localizado se encuentra en estado Inactivo, ENTONCES EL
  SISTEMA deberá advertir que el producto no está disponible para la
  venta y no deberá agregarlo al detalle.

### RF-7: Precio unitario tomado del producto
- EL SISTEMA deberá tomar el precio unitario de cada ítem del precio
  actual cargado en el producto en el momento de agregarlo al detalle;
  el Administrador no podrá modificar ese valor.

### RF-8: Cantidad positiva por ítem
- SI la cantidad ingresada para un ítem del detalle no es un número
  entero positivo, ENTONCES EL SISTEMA deberá advertir que la cantidad
  debe ser un número positivo y no deberá agregar ese ítem al detalle.

### RF-9: Validación de stock disponible por ítem
- SI la cantidad solicitada para un producto del detalle supera el stock
  disponible de ese producto, ENTONCES EL SISTEMA deberá advertir que no
  hay stock suficiente para completar la operación y no deberá permitir
  confirmar la venta.

### RF-10: Consolidación de ítems repetidos
- CUANDO el Administrador agrega al detalle un producto cuyo SKU ya está
  presente en otro ítem del mismo detalle, EL SISTEMA deberá sumar la
  cantidad nueva a la cantidad ya cargada en esa línea, en vez de crear
  una línea separada para el mismo producto, y validar el stock
  disponible (RF-9) contra la cantidad total acumulada de ese producto.

### RF-11: Al menos un ítem requerido
- SI el Administrador intenta confirmar una venta sin ningún ítem en el
  detalle, ENTONCES EL SISTEMA deberá advertir que la venta debe tener
  al menos un ítem y no deberá registrarla.

### RF-12: Reporte completo de errores al confirmar
- CUANDO el Administrador intenta confirmar una venta con más de un
  problema a la vez (ej. cantidad inválida en un ítem y stock
  insuficiente en otro), ENTONCES EL SISTEMA deberá mostrar todas las
  advertencias correspondientes en el mismo intento y no deberá
  registrar la venta.

### RF-13: Cálculo automático del total
- EL SISTEMA deberá calcular el total de la venta como la suma, para
  cada ítem consolidado del detalle (RF-10), de la cantidad multiplicada
  por su precio unitario; el Administrador no podrá ingresar el total
  manualmente.

### RF-14: Confirmación previa al registro
- CUANDO el Administrador armó el detalle de la venta con un cliente
  Activo válido y al menos un ítem válido, EL SISTEMA deberá solicitar
  que confirme la venta antes de registrarla.

### RF-15: Registro de la venta y descuento de stock
- CUANDO el Administrador confirma una venta válida, EL SISTEMA deberá
  registrar la venta —con un ID de venta asignado automáticamente, la
  fecha y hora del sistema, el cliente, el detalle de ítems, el total
  calculado (RF-13) y el estado "Confirmada"— y descontar
  automáticamente del stock de cada producto la cantidad vendida en su
  ítem correspondiente.

### RF-16: Ausencia de re-verificación al confirmar
El sistema no deberá volver a comprobar el estado del cliente, el estado
de cada producto ni el stock disponible en el momento de confirmar la
venta; deberá aplicar el registro directamente sobre los datos obtenidos
al armar el detalle (RF-1 a RF-10), asumiendo un único Administrador
operando el sistema — mismo criterio ya aceptado en
[[002-baja-cliente]] (RF-8) y [[006-baja-producto]] (RF-8). Riesgo
aceptado explícitamente: si el estado del cliente, el estado de un
producto o su stock disponible cambiaron por otra vía entre que se armó
el detalle y se confirmó la venta, la venta se registra igual sobre los
datos ya obtenidos, sin advertir el cambio.

- CUANDO el Administrador confirma una venta cuyo detalle fue armado con
  datos válidos, EL SISTEMA deberá registrar la venta y descontar el
  stock sin volver a consultar el estado del cliente, el estado de los
  productos ni el stock disponible en ese momento.

### RF-17: Cancelación de la confirmación
- CUANDO el Administrador cancela la confirmación de la venta, EL
  SISTEMA no deberá registrar ninguna venta ni modificar el stock de
  ningún producto.

## Requisitos no funcionales
- Todos los mensajes de advertencia y confirmación dirigidos al
  Administrador deben estar en español.
- La venta y el descuento de stock deben persistirse únicamente en la
  base de datos oficial del proyecto, de forma consistente (si falla el
  registro de la venta, no debe quedar stock descontado sin la venta
  correspondiente, y viceversa).

## Casos límite
- Cliente Activo con un producto Inactivo en el detalle: se bloquea
  únicamente el ítem con el producto Inactivo (RF-6), sin impedir seguir
  armando la venta con otros productos válidos.
- Cantidad solicitada igual al stock disponible exacto: válida, no se
  considera insuficiente (RF-9).
- Producto con stock en 0: cualquier cantidad solicitada mayor a cero
  siempre supera el stock disponible, por lo que no puede agregarse
  (RF-9).
- Intento de confirmar con el detalle vacío (ningún ítem agregado):
  bloqueado por RF-11.
- El Administrador cancela la confirmación después de armar todo el
  detalle: no se registra nada y el stock permanece intacto (RF-17).
- El Administrador agrega dos veces el mismo SKU al detalle, con
  cantidades distintas: se suman en una sola línea y el stock se valida
  contra el acumulado, no contra cada cantidad por separado (RF-10).
- El stock de un producto cambia (por otra venta o por una edición) o el
  cliente pasa a Inactivo entre que se arma el detalle y se confirma la
  venta: la venta se registra igual sobre los datos obtenidos al armar
  el detalle, sin volver a advertir el cambio (RF-16, riesgo aceptado
  explícitamente).

## Fuera de alcance
- Anulación o baja de una venta ya registrada (posible feature futura,
  análoga a la baja de cliente/producto).
- Edición de una venta ya registrada.
- Listado, búsqueda o filtrado de ventas (posible feature futura, análoga
  al listado de cliente/producto).
- Medios de pago, facturación o comprobantes fiscales.
- Descuentos, promociones o modificación manual del precio unitario o el
  total.
- Múltiples clientes o múltiples vendedores por venta.
- Reportes o estadísticas de ventas.
- Reversión automática de stock (solo aplicaría si existiera una
  funcionalidad de anulación, fuera de alcance).
- Autenticación y gestión de roles de usuario (se asume que el sistema
  ya identifica quién opera como Administrador).

## Criterios de finalización
- Un Administrador puede buscar un cliente Activo por DNI, agregar uno o
  más ítems válidos (producto Activo con stock suficiente y cantidad
  positiva) y, tras confirmar, la venta queda registrada con su ID,
  fecha, total calculado y estado "Confirmada", y el stock de cada
  producto vendido queda descontado (RF-1 a RF-10, RF-13 a RF-15).
- Un cliente Inactivo no puede asignarse a una venta nueva (RF-3).
- Un producto Inactivo, sin stock suficiente, o con cantidad inválida no
  puede agregarse al detalle o impide confirmar la venta, según
  corresponda (RF-6, RF-8, RF-9).
- Agregar dos veces el mismo producto al detalle suma las cantidades en
  una sola línea, en vez de crear líneas duplicadas (RF-10).
- Un intento de confirmar con múltiples problemas a la vez muestra todas
  las advertencias juntas, sin registrar la venta (RF-12).
- Cancelar la confirmación no registra ninguna venta ni modifica ningún
  stock (RF-17).
- Todos los criterios de aceptación de HU-VEN-01 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Ambas fueron resueltas y volcadas a los
requisitos correspondientes: la consolidación de ítems repetidos (RF-10)
y la ausencia de re-verificación al confirmar, con su riesgo aceptado
explícitamente documentado (RF-16).
