# Especificación de la Baja Lógica de Productos

Especificación delta para el cambio `productos-backend`. Los cambios de estado se realizan mediante DELETE lógico o mediante PUT con `dado_de_baja`; no existe un endpoint de estado dedicado. Los listados, la lectura polimórfica y el parámetro `?incluir_bajas` están fuera de alcance (véase product-catalog); el estado de un producto se verifica con `GET /productos/<subtype>/{id}`, que siempre devuelve el producto con `dado_de_baja` visible. Nota no funcional: la lógica de baja/reactivación se comparte en una única función de servicio, sin duplicarse por subtipo.

## ADDED Requirements

### Requirement: DELETE lógico
`DELETE /productos/<subtype>/{id}` DEBE establecer `dado_de_baja = true` y NO DEBE eliminar físicamente la fila. DEBE devolver 204 (sin cuerpo) en caso de éxito y 404 si el id no existe o pertenece a otro subtipo. Eliminar un producto ya dado de baja DEBE ser idempotente y devolver 204 (sin cuerpo).

#### Scenario: Dar de baja un plato
- DADO un Plato activo que no está en ningún compuesto
- CUANDO un cliente llama a `DELETE /productos/platos/{id}`
- ENTONCES 204 sin cuerpo y `GET /productos/platos/{id}` muestra `dado_de_baja = true`

#### Scenario: Id desconocido
- DADO que no existe ninguna Bebida con id 999
- CUANDO un cliente llama a `DELETE /productos/bebidas/999`
- ENTONCES 404

#### Scenario: DELETE repetido
- DADO un Postre ya dado de baja
- CUANDO un cliente llama a DELETE nuevamente
- ENTONCES 204 sin cuerpo y el estado no cambia

### Requirement: Cambio de estado vía PUT
El PUT de cada subtipo DEBE aceptar `dado_de_baja`. `dado_de_baja = true` da de baja; `dado_de_baja = false` reactiva. El cuerpo completo DEBE validarse (esquema y campos) antes de aplicar cualquier lógica de estado: un PUT con `dado_de_baja = true` y un cuerpo por lo demás inválido DEBE devolver 422 y no cambiar nada. Un PUT con `dado_de_baja = false` sobre un producto ya activo DEBE tratarse como una edición normal, con las validaciones habituales. Si `dado_de_baja` se omite en el PUT, DEBE conservarse el estado actual del producto (no reactiva ni da de baja). Un PUT con `dado_de_baja = true` sobre un producto ya dado de baja DEBE ser idempotente (200 sin cambio de estado); en un combo vencido, véase product-catalog.

#### Scenario: PUT con dado_de_baja true y cuerpo inválido
- DADO un Plato activo que no está en ningún compuesto
- CUANDO un cliente le hace PUT con `dado_de_baja = true` y `precio = 0`
- ENTONCES 422 y el Plato sigue activo

#### Scenario: PUT con dado_de_baja false sobre un producto activo
- DADO un Plato activo "Milanesa"
- CUANDO un cliente le hace PUT con `dado_de_baja = false` y una nueva `descripcion` válida
- ENTONCES 200, el Plato sigue activo y la `descripcion` se actualiza

#### Scenario: PUT con dado_de_baja false sobre un producto activo y cuerpo inválido
- DADO un Plato activo
- CUANDO un cliente le hace PUT con `dado_de_baja = false` y `nombre = ""`
- ENTONCES 422

#### Scenario: PUT sin dado_de_baja sobre un producto dado de baja
- DADO un Postre dado de baja
- CUANDO un cliente le hace PUT con una nueva `descripcion` válida y sin el campo `dado_de_baja`
- ENTONCES 200 y el Postre sigue dado de baja

#### Scenario: Dar de baja vía PUT
- DADO un Postre activo que no está en ningún compuesto
- CUANDO un cliente le hace PUT con `dado_de_baja = true`
- ENTONCES 200 y el Postre queda dado de baja

#### Scenario: Reactivar vía PUT
- DADO un Plato dado de baja
- CUANDO un cliente le hace PUT con `dado_de_baja = false`
- ENTONCES 200 y el Plato queda activo

### Requirement: RESTRICT en la baja de componentes
Un Plato, Bebida o Postre NO DEBE darse de baja (mediante DELETE o mediante PUT con `dado_de_baja = true`) mientras sea componente de un MenuEjecutivo activo o de un ComboPromocion activo y no vencido (`fecha_hasta >= today`, incluidos los combos futuros). Un combo vencido (`fecha_hasta < today`) que sigue activo NO DEBE bloquear la baja de sus componentes. La respuesta DEBE ser 409 e incluir los ids de todos los compuestos bloqueantes. La verificación y la escritura DEBEN ocurrir en una sola transacción.

#### Scenario: Bloqueado por un menú activo (DELETE)
- DADO un Plato activo usado por el menú activo 10
- CUANDO un cliente llama a `DELETE /productos/platos/{id}`
- ENTONCES 409 que lista el 10 como bloqueante y el Plato sigue activo

#### Scenario: Bloqueado por un combo activo (PUT)
- DADO una Bebida activa en el combo activo 20 con `fecha_hasta >= today`
- CUANDO un cliente hace PUT de la Bebida con `dado_de_baja = true`
- ENTONCES 409 que lista el 20 y la Bebida sigue activa

#### Scenario: Bloqueado por un combo futuro
- DADO un Postre en un combo activo cuya `fecha_desde` está en el futuro y cuya `fecha_hasta >= today`
- CUANDO un cliente da de baja el Postre
- ENTONCES 409 que lista ese combo

#### Scenario: Múltiples bloqueantes
- DADO un Plato en el menú activo 10 y en el combo activo 20
- CUANDO se intenta la baja
- ENTONCES 409 que lista tanto el 10 como el 20

#### Scenario: Los compuestos dados de baja o vencidos no bloquean
- DADO un Plato cuyos únicos compuestos son un menú dado de baja y un combo vencido
- CUANDO un cliente da de baja el Plato
- ENTONCES la baja tiene éxito

#### Scenario: Un combo vencido pero activo no bloquea la baja
- DADO un Plato cuyo único compuesto es un combo activo con `fecha_hasta` anterior a hoy
- CUANDO un cliente llama a `DELETE /productos/platos/{id}`
- ENTONCES 204 y el Plato queda dado de baja

### Requirement: Los compuestos se dan de baja libremente
MenuEjecutivo y ComboPromocion DEBEN poder darse de baja siempre mediante DELETE o PUT, sin RESTRICT. La baja de un combo vencido que sigue activo DEBE estar permitida, tanto por DELETE como por PUT con `dado_de_baja = true` sin otros cambios (véase product-catalog).

#### Scenario: Dar de baja un menú
- DADO un menú activo
- CUANDO un cliente llama a `DELETE /productos/menus-ejecutivos/{id}`
- ENTONCES el menú queda dado de baja y sus componentes no cambian

#### Scenario: Dar de baja un combo vencido mediante DELETE
- DADO un combo activo con `fecha_hasta` de ayer
- CUANDO un cliente llama a `DELETE /productos/combos/{id}`
- ENTONCES el combo queda dado de baja

#### Scenario: Dar de baja un combo vía PUT
- DADO un combo activo no vencido
- CUANDO un cliente hace PUT con `dado_de_baja = true` y el resto de los datos válidos
- ENTONCES 200 y el combo queda dado de baja

### Requirement: Validación de la reactivación
La reactivación de un MenuEjecutivo o ComboPromocion DEBE validar que todos los componentes existan y estén activos, de lo contrario 409 (esta verificación de componentes activos aplica porque el compuesto queda activo; un PUT que mantiene el compuesto dado de baja no la ejecuta, véase product-catalog). La reactivación de cualquier producto DEBE volver a verificar la unicidad de `nombre` (recortado y sin distinguir mayúsculas, pero distinguiendo tildes) entre los productos activos, de lo contrario 409. La reactivación de un combo vencido DEBE devolver 409 (véase product-catalog).

#### Scenario: Reactivar un menú con un componente inactivo
- DADO un menú dado de baja cuyo Plato ahora está dado de baja
- CUANDO un cliente hace PUT con `dado_de_baja = false`
- ENTONCES 409 y el menú sigue dado de baja

#### Scenario: Reactivar un combo con componentes activos
- DADO un combo dado de baja no vencido con todos los componentes activos
- CUANDO un cliente hace PUT con `dado_de_baja = false`
- ENTONCES 200 y el combo queda activo

#### Scenario: Conflicto de nombre en la reactivación
- DADO un Plato dado de baja "Milanesa" y otro producto activo distinto "Milanesa"
- CUANDO un cliente hace PUT del primero con `dado_de_baja = false`
- ENTONCES 409

#### Scenario: Reactivar un componente
- DADO una Bebida dada de baja con un nombre único
- CUANDO un cliente hace PUT con `dado_de_baja = false`
- ENTONCES 200 y queda activa

### Requirement: Invariante de componentes activos
Después de cualquier operación, ningún MenuEjecutivo activo ni ComboPromocion activo con `fecha_hasta >= today` DEBERÁ referenciar un componente inactivo.

#### Scenario: Invariante tras una baja bloqueada
- DADO un Plato en un menú activo
- CUANDO la baja se rechaza con 409
- ENTONCES el Plato y el menú siguen ambos activos
