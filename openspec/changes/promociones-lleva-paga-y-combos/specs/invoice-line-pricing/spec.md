# Delta de Precios de Líneas de Factura (invoice-line-pricing)

Delta sobre `invoice-line-pricing` del cambio `promociones` (todavía no archivado). Se mantienen los ids PRO-xx de los escenarios modificados; los nuevos usan el prefijo `PLC-` (numeración continua con `promotion-management`, desde PLC-24). El backend sigue siendo la única fuente de `precio_unitario`, `precio_final`, `promocion_id` y `unidades_gratis`. El cliente solo envía `factura_id`, `detalle_comanda_id` y `cantidad`; cualquier otro campo se ignora.

## ADDED Requirements

### Requirement: Motor de promociones agrupado por producto
El cálculo se realiza por grupo: las líneas activas de una factura F que comparten el mismo producto P (el de `DetalleComanda.producto_id`). Para recalcular el grupo:
1. Antes de calcular se DEBE ejecutar la baja automática por vencimiento.
2. `total = Σ cantidad` de las líneas activas del grupo.
3. Candidatas = promociones no dadas de baja, que incluyen P y vigentes a `Factura.fecha_hora_emision.date()` (límites inclusivos), más las promociones ya referenciadas por líneas activas del grupo (conservadas aunque estén dadas de baja o vencidas; no se revalidan).
4. El ahorro de cada candidata se calcula en `Decimal` (conversión `Decimal(str(...))`, nunca desde `float` directo):
   - `porcentaje`: `Σ (precio_unitario * cantidad - precio_final)` por línea, con `precio_final` por línea como `precio_unitario * cantidad * (1 - descuento / 100)` redondeado a 2 decimales (ROUND_HALF_UP).
   - `lleva_paga`: unidades gratis del grupo `⌊total / lleva⌋ * (lleva - paga)`, asignadas a las líneas de menor `precio_unitario` (empate: menor id de línea), hasta la `cantidad` de cada línea; ahorro = `Σ precio_unitario * unidades_gratis`.
5. Gana la candidata de mayor ahorro en pesos; ante empate, la de menor `id`. Una candidata con ahorro 0 NO DEBE ganar. No se acumulan promociones: un grupo recibe como máximo una.
6. Resultado por línea:
   - `porcentaje` ganadora: todas las líneas del grupo reciben `promocion_id` y su `precio_final` con descuento; `unidades_gratis = 0`.
   - `lleva_paga` ganadora: `precio_final = precio_unitario * (cantidad - unidades_gratis)`; solo las líneas con `unidades_gratis > 0` reciben `promocion_id`; las demás quedan con `promocion_id = null`, `unidades_gratis = 0` y `precio_final = precio_unitario * cantidad`.
   - Sin ganadora: todas las líneas con `promocion_id = null`, `unidades_gratis = 0` y `precio_final = precio_unitario * cantidad`.
7. Se recalcula `Factura.importe_total`.

El recálculo se dispara solo para el grupo afectado: al crear, modificar o dar de baja una línea. Si el PUT cambia `detalle_comanda_id`, se recalculan el grupo del producto anterior (sin la línea) y el del nuevo; si ambos productos coinciden, un único grupo. Una promoción `lleva_paga` actúa únicamente sobre unidades del mismo producto; las unidades de productos distintos nunca se combinan.

#### Scenario: PLC-24 2x1 con una sola línea
- DADO una promoción `lleva_paga` 2x1 vigente para un producto de precio 100.00 y una factura sin líneas de ese producto
- CUANDO se crea una línea con `cantidad = 2`
- ENTONCES `unidades_gratis = 1`, `precio_final = 100.00` y `promocion_id` es el de la promoción

#### Scenario: PLC-25 3x2 con cantidad 3
- DADO una promoción 3x2 vigente y un producto de precio 100.00
- CUANDO se crea una línea con `cantidad = 3`
- ENTONCES `unidades_gratis = 1` y `precio_final = 200.00`

#### Scenario: PLC-26 Menos unidades que lleva
- DADO una promoción 3x2 vigente y un producto de precio 100.00
- CUANDO se crea una línea con `cantidad = 2`
- ENTONCES `unidades_gratis = 0`, `precio_final = 200.00` y `promocion_id = null`

#### Scenario: PLC-27 Múltiplos de lleva
- DADO una promoción 3x2 vigente y un producto de precio 100.00
- CUANDO se crea una línea con `cantidad = 7`
- ENTONCES `unidades_gratis = 2` y `precio_final = 500.00`

#### Scenario: PLC-28 Varias líneas del mismo producto suman unidades
- DADO una promoción 2x1 vigente y una línea existente de 1 unidad del producto
- CUANDO se crea una segunda línea con 1 unidad del mismo producto
- ENTONCES el grupo suma 2 unidades y se bonifica 1; el `importe_total` de la factura baja en el precio de una unidad

#### Scenario: PLC-29 Las unidades gratis van a la línea más barata
- DADO una promoción 2x1 vigente y dos líneas activas del mismo producto con `precio_unitario` 100.00 (línea 1, `cantidad = 1`) y 80.00 (línea 2, `cantidad = 1`)
- CUANDO se recalcula el grupo
- ENTONCES la línea 2 tiene `unidades_gratis = 1`, `precio_final = 0.00` y `promocion_id` de la promoción; la línea 1 tiene `unidades_gratis = 0`, `precio_final = 100.00` y `promocion_id = null`

#### Scenario: PLC-30 Empate de precio asigna a la línea de menor id
- DADO una promoción 2x1 vigente y dos líneas del mismo producto con igual `precio_unitario` y `cantidad = 1`
- CUANDO se recalcula el grupo
- ENTONCES la línea de menor id recibe la unidad gratis

#### Scenario: PLC-31 Unidades gratis repartidas entre líneas
- DADO una promoción 3x1 (`lleva = 3`, `paga = 1`) y dos líneas del mismo producto con 1 unidad a 50.00 (línea 1) y 2 unidades a 100.00 (línea 2)
- CUANDO se recalcula el grupo
- ENTONCES las 2 unidades gratis (`⌊3/3⌋ * (3 - 1)`) se asignan a la línea 1 (1 unidad, `precio_final = 0.00`) y a la línea 2 (1 unidad, `precio_final = 100.00`)

#### Scenario: PLC-32 Productos distintos no se combinan
- DADO una promoción 2x1 vigente para los productos A y B, y una línea de 1 unidad de A y otra de 1 unidad de B
- CUANDO se recalculan los grupos
- ENTONCES ninguna línea tiene unidades gratis

#### Scenario: PLC-33 Gana el mayor ahorro en pesos entre tipos
- DADO un producto de precio 100.00, una promoción `porcentaje` del 30 por ciento y una promoción 2x1 vigentes, y una línea con `cantidad = 2`
- CUANDO se crea la línea
- ENTONCES gana la 2x1 (ahorro 100.00 frente a 60.00) y `precio_final = 100.00`

#### Scenario: PLC-34 Porcentaje supera a lleva_paga
- DADO un producto de precio 100.00, una promoción `porcentaje` del 60 por ciento y una promoción 2x1 vigentes, y una línea con `cantidad = 2`
- CUANDO se crea la línea
- ENTONCES gana el porcentaje (ahorro 120.00 frente a 100.00) y `precio_final = 80.00`

#### Scenario: PLC-35 Empate de ahorro entre tipos gana el menor id
- DADO dos promociones vigentes con el mismo ahorro en pesos para el grupo (por ejemplo `porcentaje` del 50 por ciento y 2x1 sobre `cantidad = 2`)
- CUANDO se calcula el grupo
- ENTONCES gana la de menor `id`

#### Scenario: PLC-36 Ahorro 0 no gana
- DADO una promoción 3x2 vigente y un grupo con 2 unidades
- CUANDO se calcula el grupo
- ENTONCES no hay ganadora, `promocion_id = null` y `unidades_gratis = 0`

#### Scenario: PLC-37 No se acumulan promociones
- DADO un producto con una promoción `porcentaje` y una promoción `lleva_paga` vigentes
- CUANDO se calcula el grupo
- ENTONCES todas las líneas con promoción referencian la misma, la ganadora

#### Scenario: PLC-38 Las líneas lleva_paga sin unidades gratis quedan sin promoción
- DADO una promoción 2x1 ganadora y dos líneas del mismo producto donde las unidades gratis se asignan solo a una
- CUANDO se calcula el grupo
- ENTONCES la otra línea tiene `promocion_id = null`, `unidades_gratis = 0` y `precio_final = precio_unitario * cantidad`

#### Scenario: PLC-39 Porcentaje: todas las líneas del grupo reciben la promoción
- DADO una promoción `porcentaje` ganadora y dos líneas del mismo producto
- CUANDO se calcula el grupo
- ENTONCES ambas líneas tienen el mismo `promocion_id` y `unidades_gratis = 0`

#### Scenario: PLC-40 Precios distintos dentro de un mismo producto
- DADO un grupo con líneas de `precio_unitario` 100.00 y 120.00 (snapshots distintos)
- CUANDO se aplica una 2x1
- ENTONCES la unidad gratis se asigna a la línea de 100.00

#### Scenario: PLC-41 Promoción conservada tras su baja
- DADO una línea con `promocion_id` de una promoción 2x1 que luego se da de baja, y otra promoción del 10 por ciento vigente para el producto
- CUANDO se recalcula el grupo de esa línea
- ENTONCES la promoción dada de baja sigue siendo candidata y compite por mayor ahorro

#### Scenario: PLC-42 Promoción conservada no se revalida por vigencia
- DADO una línea con una promoción ya aplicada cuya `fecha_hasta` es anterior a la fecha de emisión
- CUANDO se recalcula el grupo
- ENTONCES la promoción sigue siendo candidata

#### Scenario: PLC-43 La baja automática precede al cálculo
- DADO una promoción vencida con `dado_de_baja = false` en la base que incluye el producto, no referenciada por ninguna línea
- CUANDO se crea una línea del producto
- ENTONCES se da de baja automáticamente antes del cálculo y no es candidata

#### Scenario: PLC-44 Alta de línea recalcula el grupo
- DADO una promoción 2x1 vigente y una línea existente de 1 unidad
- CUANDO se crea una segunda línea del mismo producto con 1 unidad
- ENTONCES se recalculan ambas líneas del grupo y `importe_total` refleja las nuevas bonificaciones

#### Scenario: PLC-45 Baja de línea recalcula el grupo
- DADO una promoción 2x1 y dos líneas de 1 unidad del mismo producto, con una unidad gratis
- CUANDO se da de baja una de las líneas
- ENTONCES la línea restante pierde la bonificación (`unidades_gratis = 0`, `promocion_id = null`, `precio_final = precio_unitario * cantidad`) y `importe_total` se recalcula

#### Scenario: PLC-46 La línea dada de baja conserva sus datos históricos
- DADO una línea con `promocion_id`, `precio_final` y `unidades_gratis` que se da de baja
- CUANDO se consulta la línea inactiva
- ENTONCES conserva su `promocion_id` y su `precio_final` anteriores y no se recalcula

#### Scenario: PLC-47 Cambio de detalle_comanda_id recalcula ambos grupos
- DADO una promoción 2x1 para los productos A y B, dos líneas de producto A (una con unidad gratis) y una línea de B
- CUANDO la línea de A cambia a un `detalle_comanda_id` de producto B
- ENTONCES se recalcula el grupo de A (sin esa línea) y el de B (con esa línea) y `importe_total` se recalcula

#### Scenario: PLC-48 Cambio de detalle_comanda_id al mismo producto
- DADO una línea cuyo `detalle_comanda_id` cambia a otro detalle del mismo producto
- CUANDO se aplica el PUT
- ENTONCES se recalcula un único grupo

#### Scenario: PLC-49 Combo con lleva_paga
- DADO un combo con precio manual 500.00 en una promoción 2x1 vigente
- CUANDO se crea una línea del combo con `cantidad = 2`
- ENTONCES `precio_unitario = 500.00`, `unidades_gratis = 1` y `precio_final = 500.00`

#### Scenario: PLC-50 Cálculo exacto en Decimal
- DADO un producto de precio 33.33 con una promoción 3x2 y `cantidad = 3`
- CUANDO se calcula la línea
- ENTONCES `precio_final = 66.66` sin errores de coma flotante

### Requirement: Unidades gratis en la línea
`DetalleFactura` DEBE tener `unidades_gratis` (entero, por defecto 0) y toda respuesta de línea (alta, consulta, listado, modificación) DEBE exponerlo. Es calculado por el servidor y se ignora si el cliente lo envía. Una línea con `unidades_gratis > 0` siempre tiene `promocion_id` no nulo.

#### Scenario: PLC-51 Respuesta incluye unidades_gratis
- DADO una línea sin promoción
- CUANDO se consulta
- ENTONCES `unidades_gratis = 0`

#### Scenario: PLC-52 unidades_gratis enviado por el cliente se ignora
- CUANDO un cliente hace POST o PUT con `unidades_gratis = 5`
- ENTONCES se ignora y la respuesta refleja el valor calculado por el servidor

## MODIFIED Requirements

### Requirement: Detección automática de la promoción
Al calcular un grupo (véase "Motor de promociones agrupado por producto"), el backend DEBE considerar candidatas las promociones que cumplan todo lo siguiente: no estar dadas de baja; incluir el producto del detalle de comanda; estar vigentes a `Factura.fecha_hora_emision.date()`, con límites inclusivos (`fecha_desde <= fecha_emision <= fecha_hasta`); más las promociones ya referenciadas por líneas activas del grupo. De las candidatas DEBE elegir la de mayor ahorro total en pesos para el grupo; ante empate, la de menor `id`. Si no hay candidata con ahorro mayor que 0, `promocion_id` DEBE ser `null` y no se aplica descuento. Una promoción creada o modificada con posterioridad NO DEBE afectar líneas existentes mientras su grupo no se recalcule; un recálculo del grupo (alta, modificación o baja de una línea del mismo producto) sí la considera.

#### Scenario: PRO-33 Sin promoción aplicable
- DADO un producto sin promociones
- CUANDO se crea la línea
- ENTONCES `promocion_id = null`, `unidades_gratis = 0` y `precio_final = precio_unitario * cantidad`

#### Scenario: PRO-34 Una promoción vigente
- DADO una promoción activa `porcentaje` del 10 por ciento que incluye el producto y está vigente a la fecha de emisión
- CUANDO se crea la línea
- ENTONCES `promocion_id` es el de esa promoción

#### Scenario: PRO-35 Mayor ahorro gana
- DADO dos promociones `porcentaje` vigentes para el producto, con 10 y 25 por ciento
- CUANDO se crea la línea
- ENTONCES se aplica la de 25 por ciento (mayor ahorro en pesos)

#### Scenario: PRO-36 Empate por menor id
- DADO dos promociones vigentes con el mismo ahorro en pesos para el producto
- CUANDO se crea la línea
- ENTONCES se aplica la de menor `id`

#### Scenario: PRO-39 Promoción dada de baja
- DADO una promoción vigente dada de baja que incluye el producto y que ninguna línea del grupo referencia
- CUANDO se crea la línea
- ENTONCES no es candidata

#### Scenario: PRO-42 Promoción posterior no afecta líneas existentes
- DADO una línea creada sin promoción
- CUANDO se crea después una promoción vigente que incluye el producto y no se modifica ninguna línea de ese producto
- ENTONCES la línea conserva `promocion_id = null` y su `precio_final`

### Requirement: Modificación de la línea
`PUT /detalles-factura/{id}` DEBE aceptar `cantidad` y `detalle_comanda_id`. Tras aplicar el cambio DEBE recalcularse el grupo del producto de la línea (con redetección de la promoción ganadora entre las candidatas vigentes y las conservadas) y el `importe_total`. Si `detalle_comanda_id` cambia (y es válido), DEBE tomarse un nuevo snapshot de `precio_unitario` según el producto del nuevo detalle de comanda, y recalcularse tanto el grupo del producto anterior como el del nuevo. Si el PUT envía el mismo `detalle_comanda_id` que ya tiene la línea, el `precio_unitario` NO cambia. Los campos de precio, `promocion_id` o `unidades_gratis` enviados DEBEN ignorarse. Línea inexistente, 404.

#### Scenario: PRO-47 Cambio de cantidad
- DADO una línea con promoción `porcentaje` del 10 por ciento, `precio_unitario = 100.00` y cantidad 1
- CUANDO un cliente hace PUT con `cantidad = 2`
- ENTONCES `precio_final = 180.00` y `promocion_id` sigue siendo el de la promoción

#### Scenario: PRO-48 Cambio de cantidad recalcula el grupo con las candidatas vigentes
- DADO una línea sin promoción y, después, una promoción nueva vigente para su producto
- CUANDO un cliente hace PUT con solo `cantidad`
- ENTONCES se recalcula el grupo y `promocion_id` pasa a ser el de la promoción nueva si su ahorro es mayor que 0

#### Scenario: PRO-49 Cambio de detalle_comanda_id redetecta
- DADO una línea y otro detalle de comanda válido de la misma comanda con otro producto y otra promoción vigente
- CUANDO un cliente hace PUT con el nuevo `detalle_comanda_id`
- ENTONCES se recalculan ambos grupos, se actualiza `precio_unitario` y se recalcula `precio_final`

#### Scenario: PRO-50 Mismo detalle_comanda_id conserva el snapshot
- DADO una línea con `detalle_comanda_id = X` y una promoción nueva existente
- CUANDO un cliente hace PUT con `detalle_comanda_id = X`
- ENTONCES `precio_unitario` no cambia (el grupo se recalcula con los snapshots existentes)

#### Scenario: PLC-53 Cambio de cantidad en lleva_paga
- DADO una línea de 2 unidades con una 3x2 sin bonificación
- CUANDO un cliente hace PUT con `cantidad = 3`
- ENTONCES `unidades_gratis = 1`, `promocion_id` es el de la 3x2 y `precio_final = precio_unitario * 2`

### Requirement: Consistencia de importe_total
`Factura.importe_total` DEBE ser siempre la suma de `precio_final` de las líneas activas de la factura, recalculada tras crear, modificar o eliminar una línea (y tras el recálculo de los grupos afectados), con redondeo a 2 decimales. La baja de una promoción no recalcula líneas ni totales existentes. Una línea dada de baja conserva su `promocion_id`, `precio_final` y `unidades_gratis` anteriores y no participa del total.

#### Scenario: PRO-55 Total tras eliminar una línea
- DADO una factura con dos líneas activas
- CUANDO se elimina una
- ENTONCES `importe_total` es la suma de `precio_final` de las líneas activas restantes, ya recalculado el grupo del producto de la línea eliminada

## REMOVED Requirements

Ninguno.
