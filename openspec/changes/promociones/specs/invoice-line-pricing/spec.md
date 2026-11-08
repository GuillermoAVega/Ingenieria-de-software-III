# Especificación de Precios de Líneas de Factura

Especificación nueva para el cambio `promociones`. Cubre `POST /detalles-factura` y `PUT /detalles-factura/{id}`. El backend es la única fuente de `precio_unitario`, `precio_final` y `promocion_id`.

## ADDED Requirements

### Requirement: Entrada sin datos de precio ni promoción
`DetalleFacturaCreate` y `DetalleFacturaUpdate` NO DEBEN aceptar `precio_unitario`, `precio_final` ni `promocion_id` como datos de entrada. Siguiendo la convención vigente de los esquemas (Pydantic por defecto, sin `extra="forbid"`), si el cliente envía esos campos DEBEN ignorarse sin error y NUNCA influir en el resultado. El Alta DEBE exigir `factura_id`, `detalle_comanda_id` y `cantidad > 0`.

#### Scenario: PRO-29 Campos de precio enviados son ignorados
- DADO una factura y un detalle de comanda válidos con producto de precio 100
- CUANDO un cliente hace POST con `precio_unitario = 1`, `precio_final = 1` y `promocion_id = 999`
- ENTONCES 201 y `precio_unitario = 100`, `precio_final` calculado por el servidor y `promocion_id` determinado por la detección automática

#### Scenario: PRO-30 detalle_comanda_id obligatorio
- CUANDO un cliente hace POST sin `detalle_comanda_id` o con `null`
- ENTONCES 422

### Requirement: Validación del detalle de comanda
El `detalle_comanda_id` DEBE existir y estar activo (404 en caso contrario) y pertenecer a la comanda de la factura (400 en caso contrario, conforme al comportamiento vigente). El producto de la línea se obtiene de `DetalleComanda.producto_id`.

#### Scenario: PRO-31 Detalle de comanda inexistente
- CUANDO un cliente hace POST con un `detalle_comanda_id` que no existe
- ENTONCES 404 y no se crea la línea

#### Scenario: PRO-32 Detalle de comanda de otra comanda
- DADO un detalle de comanda que pertenece a una comanda distinta de la de la factura
- CUANDO un cliente hace POST con ese `detalle_comanda_id`
- ENTONCES 400 y no se crea la línea

### Requirement: Detección automática de la promoción
Al crear una línea, el backend DEBE seleccionar entre las promociones que cumplan todo lo siguiente: no estar dadas de baja; incluir el producto del detalle de comanda; estar vigentes a `Factura.fecha_hora_emision.date()`, con límites inclusivos (`fecha_desde <= fecha_emision <= fecha_hasta`). De los candidatos DEBE elegir el de mayor `descuento`; ante empate, el de menor `id`. Si no hay candidatos, `promocion_id` DEBE ser `null` y el descuento 0. Una promoción creada o modificada con posterioridad NO DEBE afectar líneas ya existentes.

#### Scenario: PRO-33 Sin promoción aplicable
- DADO un producto sin promociones
- CUANDO se crea la línea
- ENTONCES `promocion_id = null` y `precio_final = precio_unitario * cantidad`

#### Scenario: PRO-34 Una promoción vigente
- DADO una promoción activa del 10 por ciento que incluye el producto y está vigente a la fecha de emisión
- CUANDO se crea la línea
- ENTONCES `promocion_id` es el de esa promoción

#### Scenario: PRO-35 Mayor descuento gana
- DADO dos promociones vigentes para el producto, con 10 y 25 por ciento
- CUANDO se crea la línea
- ENTONCES se aplica la de 25 por ciento

#### Scenario: PRO-36 Empate por menor id
- DADO dos promociones vigentes con el mismo descuento para el producto
- CUANDO se crea la línea
- ENTONCES se aplica la de menor `id`

#### Scenario: PRO-37 Límites inclusivos de vigencia
- DADO una promoción con `fecha_desde` igual a la fecha de emisión y otra con `fecha_hasta` igual a la fecha de emisión
- CUANDO se crea la línea en cada caso
- ENTONCES ambas son candidatas

#### Scenario: PRO-38 Fuera de vigencia
- DADO una promoción cuya `fecha_hasta` es anterior a la fecha de emisión, o cuya `fecha_desde` es posterior
- CUANDO se crea la línea
- ENTONCES no es candidata y `promocion_id = null`

#### Scenario: PRO-39 Promoción dada de baja
- DADO una promoción vigente dada de baja que incluye el producto
- CUANDO se crea la línea
- ENTONCES no es candidata

#### Scenario: PRO-40 Promoción de otro producto
- DADO una promoción vigente que no incluye el producto de la línea
- CUANDO se crea la línea
- ENTONCES no es candidata

#### Scenario: PRO-41 La vigencia usa la fecha de emisión de la factura
- DADO una promoción vigente hoy pero no a la fecha de emisión de la factura
- CUANDO se crea la línea
- ENTONCES no es candidata

#### Scenario: PRO-42 Promoción posterior no afecta líneas existentes
- DADO una línea creada sin promoción
- CUANDO se crea después una promoción vigente que incluye el producto
- ENTONCES la línea conserva `promocion_id = null` y su `precio_final`

### Requirement: Cálculo de precios
`precio_unitario` DEBE ser un snapshot de `Producto.precio` al crear la línea (no cambia si el producto cambia de precio después). `precio_final` DEBE calcularse en `Decimal` como `precio_unitario * cantidad * (1 - descuento / 100)`, redondeado a 2 decimales (half-up), y persistirse con ese redondeo; sin promoción, el descuento es 0.

#### Scenario: PRO-43 Cálculo con descuento
- DADO un producto de precio 100.00, cantidad 3 y promoción del 15 por ciento
- CUANDO se crea la línea
- ENTONCES `precio_unitario = 100.00` y `precio_final = 255.00`

#### Scenario: PRO-44 Redondeo a 2 decimales
- DADO un producto de precio 10.00, cantidad 1 y promoción del 33.33 por ciento
- CUANDO se crea la línea
- ENTONCES `precio_final = 6.67`

#### Scenario: PRO-45 Descuento del 100 por ciento
- DADO una promoción del 100 por ciento
- CUANDO se crea la línea
- ENTONCES `precio_final = 0.00`

#### Scenario: PRO-46 Snapshot del precio unitario
- DADO una línea creada con `precio_unitario = 100.00`
- CUANDO el precio del producto cambia después a 150.00
- ENTONCES la línea sigue mostrando `precio_unitario = 100.00`

### Requirement: Modificación de la línea
`PUT /detalles-factura/{id}` DEBE aceptar `cantidad` y `detalle_comanda_id`. Si `detalle_comanda_id` cambia (y es válido), DEBE redetectarse la promoción y tomarse un nuevo snapshot de `precio_unitario` según el producto del nuevo detalle de comanda, y recalcularse `precio_final`. Si solo cambia `cantidad`, DEBE recalcularse `precio_final` con `precio_unitario` y la promoción actuales de la línea, sin redetectar ni cambiar `promocion_id`. Si el PUT envía el mismo `detalle_comanda_id` que ya tiene la línea, NO DEBE redetectarse. Los campos de precio o `promocion_id` enviados DEBEN ignorarse. Línea inexistente, 404.

#### Scenario: PRO-47 Cambio de cantidad
- DADO una línea con promoción del 10 por ciento, `precio_unitario = 100.00` y cantidad 1
- CUANDO un cliente hace PUT con `cantidad = 2`
- ENTONCES `precio_final = 180.00` y `promocion_id` no cambia

#### Scenario: PRO-48 Cambio de cantidad no redetecta
- DADO una línea sin promoción y, después, una promoción nueva vigente para su producto
- CUANDO un cliente hace PUT con solo `cantidad`
- ENTONCES `promocion_id` sigue siendo `null`

#### Scenario: PRO-49 Cambio de detalle_comanda_id redetecta
- DADO una línea y otro detalle de comanda válido de la misma comanda con otro producto y otra promoción vigente
- CUANDO un cliente hace PUT con el nuevo `detalle_comanda_id`
- ENTONCES se redetecta `promocion_id`, se actualiza `precio_unitario` y se recalcula `precio_final`

#### Scenario: PRO-50 Mismo detalle_comanda_id no redetecta
- DADO una línea con `detalle_comanda_id = X`
- CUANDO un cliente hace PUT con `detalle_comanda_id = X` y una promoción nueva existe
- ENTONCES `promocion_id` y `precio_unitario` no cambian

#### Scenario: PRO-51 Precios enviados en PUT son ignorados
- CUANDO un cliente hace PUT con `precio_unitario`, `precio_final` o `promocion_id`
- ENTONCES se ignoran y la respuesta refleja solo los valores calculados por el servidor

#### Scenario: PRO-52 PUT con detalle_comanda_id inválido
- CUANDO un cliente hace PUT con un `detalle_comanda_id` inexistente
- ENTONCES 404 y la línea no cambia

### Requirement: Consistencia de importe_total
`Factura.importe_total` DEBE ser siempre la suma de `precio_final` de las líneas activas de la factura, recalculada tras crear, modificar o eliminar una línea, con redondeo a 2 decimales. La baja de una promoción no recalcula líneas ni totales existentes.

#### Scenario: PRO-53 Total tras crear líneas
- DADO una factura con líneas de `precio_final` 255.00 y 10.00
- CUANDO se consulta la factura
- ENTONCES `importe_total = 265.00`

#### Scenario: PRO-54 Total tras modificar cantidad
- DADO una línea con `precio_final` 90.00 en una factura de total 90.00
- CUANDO se modifica la cantidad y el nuevo `precio_final` es 180.00
- ENTONCES `importe_total = 180.00`

#### Scenario: PRO-55 Total tras eliminar una línea
- DADO una factura con dos líneas activas
- CUANDO se elimina una
- ENTONCES `importe_total` es el `precio_final` de la restante

#### Scenario: PRO-56 Total tras la baja de la promoción
- DADO una factura con una línea que usa una promoción
- CUANDO la promoción se da de baja
- ENTONCES `importe_total` y la línea no cambian
