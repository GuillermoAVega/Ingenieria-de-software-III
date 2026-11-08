# Especificación de Validación de Producto en Líneas de Comanda

Especificación nueva para el cambio `promociones`. `DetalleComanda.producto_id` pasa a ser FK a `producto.id` y se valida en el servicio antes de escribir, para que ningún valor inválido llegue a la base. Se aplica tanto a la creación anidada de detalles en `POST /comandas` como a `POST /detalles-comanda` y `PUT /detalles-comanda/{id}` cuando se envía `producto_id`.

## ADDED Requirements

### Requirement: El producto de la línea debe existir
Si `producto_id` no corresponde a ningún producto, el sistema DEBE responder 422 con error de campo (`loc = ["body", <campo>]`, `type = "producto_inexistente"`, incluyendo los ids), siguiendo la convención de `Backend/src/productos_menu/router.py`, y no persistir nada (en la creación anidada, ni la comanda ni ninguno de sus detalles). Un `producto_id` explícitamente `null` DEBE responder 422. NUNCA DEBE responder 500 por violación de FK.

#### Scenario: PRO-57 Detalle suelto con producto inexistente
- CUANDO un cliente hace POST a `/detalles-comanda` con un `producto_id` que no existe
- ENTONCES 422 con `type = "producto_inexistente"` y no se crea el detalle

#### Scenario: PRO-58 Creación anidada con producto inexistente
- CUANDO un cliente hace POST a `/comandas` con un detalle cuyo `producto_id` no existe
- ENTONCES 422 con `type = "producto_inexistente"` y no se crea la comanda ni ningún detalle

#### Scenario: PRO-59 Modificación con producto inexistente
- DADO un detalle de comanda existente
- CUANDO un cliente hace PUT con un `producto_id` que no existe
- ENTONCES 422 con `type = "producto_inexistente"` y el detalle no cambia

#### Scenario: PRO-72 producto_id null explícito
- CUANDO un cliente hace POST a `/detalles-comanda`, a `/comandas` (detalle anidado) o PUT a un detalle con `producto_id = null`
- ENTONCES 422 en cada caso y no se persiste nada

### Requirement: Rechazo de productos dados de baja en líneas nuevas
Un producto dado de baja NO DEBE aceptarse en líneas de comanda nuevas: DEBE responder 409 y no persistir nada. Aplica a la creación anidada en `POST /comandas`, a `POST /detalles-comanda` y a un PUT que cambie `producto_id` a un producto dado de baja. Un PUT que no cambie `producto_id` NO DEBE revalidar el estado del producto. Las líneas existentes con productos luego dados de baja se conservan sin cambios.

#### Scenario: PRO-60 Detalle suelto con producto dado de baja
- DADO un producto dado de baja
- CUANDO un cliente hace POST a `/detalles-comanda` con ese `producto_id`
- ENTONCES 409 y no se crea el detalle

#### Scenario: PRO-61 Creación anidada con producto dado de baja
- DADO un producto dado de baja
- CUANDO un cliente hace POST a `/comandas` con un detalle de ese producto
- ENTONCES 409 y no se crea la comanda ni ningún detalle

#### Scenario: PRO-62 PUT que cambia a un producto dado de baja
- DADO un detalle de comanda con producto activo y otro producto dado de baja
- CUANDO un cliente hace PUT con `producto_id` del producto dado de baja
- ENTONCES 409 y el detalle no cambia

#### Scenario: PRO-63 PUT sin cambiar producto_id sobre producto dado de baja después
- DADO un detalle cuyo producto fue dado de baja después de crearse
- CUANDO un cliente hace PUT cambiando solo la cantidad
- ENTONCES 200 y el detalle conserva su `producto_id`

#### Scenario: PRO-64 Producto activo válido
- DADO un producto activo
- CUANDO un cliente crea un detalle de comanda con ese `producto_id`
- ENTONCES 201
