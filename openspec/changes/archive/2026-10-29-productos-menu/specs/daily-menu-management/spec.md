# Especificación de la Gestión del Menú del Día

Capacidad nueva introducida por el cambio `productos-menu`. Códigos de estado: 422 = validación de esquema/campos o referencia inexistente en el cuerpo, 404 = id inexistente en la ruta, 409 = conflicto de regla de negocio.

**Alcance**: esta capacidad cubre únicamente el alta (`POST`), la modificación de fecha (`PUT`) y el borrado físico (`DELETE`) de registros `ProductoMenu`. Quedan explícitamente FUERA DE ALCANCE y NO DEBEN implementarse: `GET` y listados de menús del día, el cambio de `producto_id` de un registro existente y el bloqueo (RESTRICT) de la baja lógica de un producto por ser menú del día.

## ADDED Requirements

### Requirement: Entidad ProductoMenu y relación con Producto
Un `ProductoMenu` DEBE tener `id`, `producto_id` (obligatorio, referencia a un `Producto` de cualquier subtipo) y `fecha` (fecha calendario obligatoria). La fecha DEBE ser única entre todos los registros. La relación entre `ProductoMenu` y `Producto` DEBE ser bidireccional (`ProductoMenu.producto` / `Producto.menus_del_dia`, con `back_populates`, cardinalidad 0..N del lado del producto) y todos los mappers DEBEN configurarse sin errores. La respuesta de un `ProductoMenu` DEBE exponer únicamente `id`, `producto_id` y `fecha`.

#### Scenario: PMD-01 Los mappers se configuran con la nueva entidad
- DADO que los modelos de producto y de menú del día están cargados
- CUANDO se configuran los mappers de SQLAlchemy
- ENTONCES no se lanza ningún error

#### Scenario: PMD-02 La relación es bidireccional
- DADO un registro `ProductoMenu` asociado a un producto
- CUANDO se accede a `ProductoMenu.producto` y a `Producto.menus_del_dia`
- ENTONCES `producto` devuelve el producto asociado y `menus_del_dia` contiene el registro

#### Scenario: PMD-03 La respuesta expone solo id, producto_id y fecha
- DADO un alta válida
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES el cuerpo de la respuesta contiene exactamente las claves `id`, `producto_id` y `fecha`

### Requirement: Alta de un menú del día
`POST /productos-menu` con `{producto_id, fecha}` DEBE crear el registro y devolver 201 con `{id, producto_id, fecha}`. La `fecha` PUEDE ser pasada, la de hoy o futura. El `producto_id` PUEDE referir a un producto de cualquiera de los cinco subtipos (Plato, Postre, Bebida, MenuEjecutivo, ComboPromocion).

#### Scenario: PMD-04 Alta válida
- DADO un producto activo y una fecha sin menú del día
- CUANDO un cliente llama a `POST /productos-menu` con `producto_id` y `fecha`
- ENTONCES 201 y el cuerpo contiene `id`, `producto_id` y `fecha` iguales a los enviados, y el registro queda persistido

#### Scenario: PMD-05 Fecha pasada
- DADO un producto activo y una fecha anterior a hoy sin menú del día
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 201

#### Scenario: PMD-06 Fecha de hoy
- DADO un producto activo y la fecha de hoy sin menú del día
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 201

#### Scenario: PMD-07 Fecha futura
- DADO un producto activo y una fecha posterior a hoy sin menú del día
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 201

#### Scenario: PMD-08 Se acepta un producto de cualquiera de los cinco subtipos
- DADO un producto activo de cada subtipo (Plato, Postre, Bebida, MenuEjecutivo, ComboPromocion) y una fecha distinta para cada uno
- CUANDO un cliente llama a `POST /productos-menu` para cada producto
- ENTONCES cada llamada devuelve 201

### Requirement: Validación del alta
`producto_id` es obligatorio y DEBE ser un entero; `fecha` es obligatoria y DEBE ser una fecha válida. Un `producto_id` ausente o no entero DEBE devolver 422; una `fecha` ausente o inválida DEBE devolver 422. Un `producto_id` entero que no corresponda a ningún producto DEBE devolver 422. Un producto dado de baja DEBE devolver 409. Una `fecha` ya ocupada por otro registro DEBE devolver 409. Cuando concurran varios errores, la prioridad DEBE ser: esquema 422, producto inexistente 422, producto dado de baja 409, fecha ocupada 409. Una solicitud rechazada NO DEBE modificar el estado persistido. Ante una carrera entre dos altas con la misma fecha, la violación del índice UNIQUE DEBE traducirse a 409.

#### Scenario: PMD-09 producto_id ausente
- DADO un cuerpo sin el campo `producto_id`
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 y no se crea ningún registro

#### Scenario: PMD-10 producto_id no entero
- DADO un cuerpo con `producto_id = "abc"`
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 y no se crea ningún registro

#### Scenario: PMD-11 fecha ausente
- DADO un cuerpo sin el campo `fecha`
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 y no se crea ningún registro

#### Scenario: PMD-12 fecha inválida
- DADO un cuerpo con `fecha = "no-es-una-fecha"` o `fecha = "2026-02-30"`
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 y no se crea ningún registro

#### Scenario: PMD-13 producto inexistente
- DADO un `producto_id` entero que no corresponde a ningún producto
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 y no se crea ningún registro

#### Scenario: PMD-14 producto dado de baja
- DADO un producto con `dado_de_baja = true` y una fecha libre
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 409 y no se crea ningún registro

#### Scenario: PMD-15 fecha ocupada
- DADO un registro existente con `fecha = F` y un producto activo
- CUANDO un cliente llama a `POST /productos-menu` con `fecha = F`
- ENTONCES 409 y el registro existente permanece sin cambios y no se crea otro

#### Scenario: PMD-16 Esquema inválido prevalece sobre producto inexistente
- DADO un cuerpo con `producto_id` inexistente y `fecha` ausente
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 por validación de esquema

#### Scenario: PMD-17 Producto inexistente prevalece sobre fecha ocupada
- DADO una fecha ocupada y un `producto_id` inexistente
- CUANDO un cliente llama a `POST /productos-menu` con esa fecha y ese `producto_id`
- ENTONCES 422 por producto inexistente, no 409

#### Scenario: PMD-18 Producto dado de baja prevalece sobre fecha ocupada
- DADO una fecha ocupada y un producto dado de baja
- CUANDO un cliente llama a `POST /productos-menu` con esa fecha y ese producto
- ENTONCES 409 por producto dado de baja y el mensaje de error identifica ese motivo, no el de fecha ocupada

#### Scenario: PMD-19 Una solicitud rechazada no cambia nada
- DADO un conjunto de registros existentes
- CUANDO una llamada a `POST /productos-menu` es rechazada con 422 o 409
- ENTONCES el conjunto de registros persistidos es idéntico al previo

#### Scenario: PMD-20 Carrera entre altas con la misma fecha
- DADO que la verificación previa de la fecha no detecta conflicto pero otra alta ya ocupó la fecha
- CUANDO la escritura viola el índice UNIQUE sobre `fecha`
- ENTONCES la respuesta es 409 y no 500

### Requirement: Modificación de la fecha de un menú del día
`PUT /productos-menu/{id}` DEBE aceptar únicamente `fecha` y devolver 200 con `{id, producto_id, fecha}` actualizado. Conservar la fecha propia del registro DEBE ser válido. Mover el registro a una fecha libre DEBE ser válido. Una fecha ocupada por OTRO registro DEBE devolver 409. Un `id` inexistente DEBE devolver 404. Si el producto asociado está dado de baja, DEBE devolver 409. Un `producto_id` incluido en el cuerpo DEBE ignorarse y NO DEBE modificar el producto asociado. Cuando concurran varios errores, la prioridad DEBE ser: esquema 422, id inexistente 404, producto dado de baja 409, fecha ocupada por otro registro 409. Una solicitud rechazada NO DEBE modificar el estado persistido.

#### Scenario: PMD-21 Mover a una fecha libre
- DADO un registro con `fecha = F1` y una fecha libre `F2`
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con `fecha = F2`
- ENTONCES 200, la respuesta contiene `fecha = F2` y el mismo `id` y `producto_id`, y `F1` queda libre

#### Scenario: PMD-22 Conservar la fecha propia
- DADO un registro con `fecha = F`
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con `fecha = F`
- ENTONCES 200 y el registro permanece con `fecha = F`

#### Scenario: PMD-23 Fecha ocupada por otro registro
- DADO dos registros con fechas `F1` y `F2`
- CUANDO un cliente llama a `PUT` sobre el primero con `fecha = F2`
- ENTONCES 409 y ambos registros conservan sus fechas

#### Scenario: PMD-24 id inexistente
- DADO un `id` que no corresponde a ningún registro
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con una fecha válida
- ENTONCES 404

#### Scenario: PMD-25 Producto dado de baja
- DADO un registro cuyo producto fue dado de baja posteriormente y una fecha libre
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con esa fecha
- ENTONCES 409 y la fecha del registro no cambia

#### Scenario: PMD-26 producto_id en el cuerpo se ignora
- DADO un registro asociado al producto A y un producto B activo
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con `{fecha, producto_id: B}`
- ENTONCES 200, la fecha se actualiza y el `producto_id` del registro sigue siendo A

#### Scenario: PMD-27 fecha ausente o inválida en el PUT
- DADO un cuerpo sin `fecha` o con una `fecha` inválida
- CUANDO un cliente llama a `PUT /productos-menu/{id}`
- ENTONCES 422 y el registro no cambia

#### Scenario: PMD-28 Esquema inválido prevalece sobre id inexistente
- DADO un `id` inexistente y un cuerpo con `fecha` inválida
- CUANDO un cliente llama a `PUT /productos-menu/{id}`
- ENTONCES 422, no 404

#### Scenario: PMD-29 id inexistente prevalece sobre las reglas de negocio
- DADO un `id` inexistente y una fecha ocupada
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con esa fecha
- ENTONCES 404, no 409

#### Scenario: PMD-30 Producto dado de baja prevalece sobre fecha ocupada
- DADO un registro cuyo producto está dado de baja y una fecha ocupada por otro registro
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con esa fecha
- ENTONCES 409 por producto dado de baja y el mensaje de error identifica ese motivo, no el de fecha ocupada

#### Scenario: PMD-31 Una solicitud rechazada no cambia nada
- DADO un conjunto de registros existentes
- CUANDO una llamada a `PUT /productos-menu/{id}` es rechazada con 422, 404 o 409
- ENTONCES el conjunto de registros persistidos es idéntico al previo

### Requirement: Borrado físico de un menú del día
`DELETE /productos-menu/{id}` DEBE eliminar físicamente el registro y devolver 204 sin cuerpo. Un `id` inexistente, o un DELETE repetido sobre el mismo `id`, DEBE devolver 404. El borrado NO DEBE verificar el estado (`dado_de_baja`) del producto asociado. La fecha liberada DEBE poder reutilizarse en un `POST` posterior.

#### Scenario: PMD-32 Borrado exitoso
- DADO un registro existente
- CUANDO un cliente llama a `DELETE /productos-menu/{id}`
- ENTONCES 204 y el registro ya no existe en la base de datos

#### Scenario: PMD-33 id inexistente
- DADO un `id` que no corresponde a ningún registro
- CUANDO un cliente llama a `DELETE /productos-menu/{id}`
- ENTONCES 404

#### Scenario: PMD-34 DELETE repetido
- DADO un registro ya eliminado con un primer DELETE que devolvió 204
- CUANDO un cliente repite `DELETE /productos-menu/{id}`
- ENTONCES 404

#### Scenario: PMD-35 El estado del producto no se verifica
- DADO un registro cuyo producto está dado de baja
- CUANDO un cliente llama a `DELETE /productos-menu/{id}`
- ENTONCES 204 y el registro se elimina

#### Scenario: PMD-36 La fecha liberada puede reutilizarse
- DADO un registro con `fecha = F` que se elimina con 204
- CUANDO un cliente llama a `POST /productos-menu` con `fecha = F` y un producto activo
- ENTONCES 201

### Requirement: Baja de productos que son menú del día
Dar de baja lógicamente un producto que tiene registros de menú del día DEBE estar permitido. El comportamiento de la baja lógica NO DEBE cambiar (`RESTRICT_POR_TIPO` no se modifica) y NO DEBE existir ningún bloqueo (RESTRICT) por ser menú del día. Los registros de menú del día del producto dado de baja DEBEN permanecer como historial.

#### Scenario: PMD-37 La baja de un producto con menú del día está permitida
- DADO un producto activo con un registro de menú del día
- CUANDO se da de baja el producto mediante su endpoint de baja lógica
- ENTONCES la baja se completa con el mismo código de estado que para un producto sin menú del día

#### Scenario: PMD-38 Los registros permanecen tras la baja
- DADO un producto con dos registros de menú del día que se da de baja
- CUANDO se consultan los registros persistidos
- ENTONCES ambos registros siguen existiendo con su `producto_id` y `fecha` originales

### Requirement: Las respuestas de producto no cambian
Las respuestas de producto NO DEBEN exponer los menús del día: la relación `Producto.menus_del_dia` NO DEBE aparecer en ningún esquema de respuesta de producto, y el contrato de `product-catalog` NO DEBE cambiar.

#### Scenario: PMD-39 La respuesta de producto no incluye menús del día
- DADO un producto con un registro de menú del día
- CUANDO un cliente consulta el producto por su endpoint existente
- ENTONCES la respuesta no contiene `menus_del_dia` ni ninguna clave relacionada con el menú del día, y sus claves son las mismas que sin el cambio

### Requirement: Varios registros por producto
Un mismo producto PUEDE tener varios registros de menú del día en fechas distintas.

#### Scenario: PMD-40 Un producto con varias fechas
- DADO un producto activo
- CUANDO un cliente llama a `POST /productos-menu` dos veces con ese producto y fechas distintas
- ENTONCES ambas llamadas devuelven 201 y `Producto.menus_del_dia` contiene los dos registros
