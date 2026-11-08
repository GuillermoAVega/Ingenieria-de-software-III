# Especificación Delta de la Baja Lógica de Productos: MenuDelDia con fechas vigentes

Especificación delta para el cambio `menu-del-dia-producto`, aplicada sobre `product-logical-delete`. Códigos de estado: 422 = validación, 404 = id inexistente, 409 = conflicto de regla de negocio.

**Alcance**: se agrega una regla de baja específica del tipo `MenuDelDia`. "Hoy" se obtiene mediante `obtener_hoy` (fecha única inyectable, igual que en la regla de combos), de modo que las pruebas pueden fijarla. `RESTRICT_POR_TIPO` no se modifica: el `MenuDelDia` no es componente de ningún compuesto, por lo que su baja no depende de ellos y la baja de Plato, Bebida y Postre no se ve afectada por los registros `ProductoMenu`. Los requisitos genéricos de DELETE, PUT con `dado_de_baja` y reactivación se aplican a `MenuDelDia` salvo lo indicado.

## ADDED Requirements

### Requirement: Baja de un MenuDelDia bloqueada por fechas vigentes
Un `MenuDelDia` NO DEBE darse de baja (mediante `DELETE /productos/menus-del-dia/{id}` o mediante PUT con `dado_de_baja = true`) mientras tenga algún registro `ProductoMenu` con `fecha >= hoy` (la fecha de hoy y las futuras bloquean). La respuesta DEBE ser 409, identificar el motivo (el menú del día tiene fechas asignadas vigentes) e incluir en la clave `fechas` las fechas vigentes bloqueantes (formato ISO, en orden ascendente). Los registros con `fecha < hoy` NO DEBEN bloquear la baja. La verificación y la escritura DEBEN ocurrir en una sola transacción. Una solicitud rechazada NO DEBE modificar el estado persistido. Un `DELETE` repetido sobre un `MenuDelDia` ya dado de baja DEBE seguir siendo idempotente (204), igual que para los demás subtipos.

#### Scenario: MDD-49 Baja bloqueada con fecha futura (DELETE)
- DADO un `MenuDelDia` activo con un registro `ProductoMenu` de fecha posterior a hoy
- CUANDO un cliente llama a `DELETE /productos/menus-del-dia/{id}`
- ENTONCES 409 cuya clave `fechas` lista la fecha bloqueante y el menú sigue activo

#### Scenario: MDD-50 Baja bloqueada con fecha de hoy
- DADO un `MenuDelDia` activo con un registro `ProductoMenu` de fecha igual a hoy
- CUANDO un cliente llama a `DELETE /productos/menus-del-dia/{id}`
- ENTONCES 409 y el menú sigue activo

#### Scenario: MDD-51 Baja bloqueada vía PUT
- DADO un `MenuDelDia` activo con un registro de fecha igual o posterior a hoy
- CUANDO un cliente hace PUT con un cuerpo válido y `dado_de_baja = true`
- ENTONCES 409 y el menú sigue activo, sin cambios en ningún otro campo

#### Scenario: MDD-52 Baja permitida con solo fechas pasadas
- DADO un `MenuDelDia` activo cuyos únicos registros `ProductoMenu` tienen fecha anterior a hoy
- CUANDO un cliente llama a `DELETE /productos/menus-del-dia/{id}`
- ENTONCES 204, el menú queda dado de baja y los registros `ProductoMenu` siguen existiendo con su `fecha` original

#### Scenario: MDD-53 Baja permitida sin fechas
- DADO un `MenuDelDia` activo sin registros `ProductoMenu`
- CUANDO un cliente lo da de baja por DELETE o por PUT con `dado_de_baja = true`
- ENTONCES la baja se completa con éxito

#### Scenario: MDD-54 Múltiples bloqueantes
- DADO un `MenuDelDia` con dos registros de fecha igual o posterior a hoy y uno pasado
- CUANDO se intenta la baja
- ENTONCES 409 cuya clave `fechas` lista las dos fechas vigentes en orden ascendente y no la pasada

#### Scenario: MDD-55 El límite depende de la fecha fijada para hoy
- DADO un `MenuDelDia` con un registro de fecha F y `obtener_hoy` fijado en F más un día
- CUANDO un cliente intenta la baja
- ENTONCES la baja se permite; con `obtener_hoy` fijado en F, la baja devuelve 409

#### Scenario: MDD-56 Liberar la fecha desbloquea la baja
- DADO un `MenuDelDia` cuya única fecha vigente se elimina con `DELETE /productos-menu/{id}` (204)
- CUANDO un cliente intenta la baja del menú
- ENTONCES la baja se completa con éxito

#### Scenario: MDD-57 Baja repetida idempotente
- DADO un `MenuDelDia` ya dado de baja (con solo fechas pasadas)
- CUANDO un cliente llama a `DELETE /productos/menus-del-dia/{id}` nuevamente
- ENTONCES 204 sin cuerpo y el estado no cambia

#### Scenario: MDD-58 Invariante tras una baja bloqueada
- DADO un `MenuDelDia` con fecha vigente
- CUANDO la baja se rechaza con 409
- ENTONCES el menú sigue activo y todos sus registros `ProductoMenu` permanecen sin cambios

### Requirement: Un menú del día dado de baja no admite nuevas fechas
Mientras un `MenuDelDia` esté dado de baja, asignarle una fecha (`POST /productos-menu`) o modificar la fecha de uno de sus registros (`PUT /productos-menu/{id}`) DEBE devolver 409 (véase daily-menu-management). Reactivar el `MenuDelDia` (PUT con `dado_de_baja = false`, con las validaciones genéricas de reactivación, incluida la unicidad de `nombre`) DEBE volver a permitirlo.

#### Scenario: MDD-59 Asignar fecha a un menú dado de baja
- DADO un `MenuDelDia` dado de baja y una fecha libre
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 409 y no se crea ningún registro

#### Scenario: MDD-60 Reactivar permite asignar fechas de nuevo
- DADO un `MenuDelDia` dado de baja con nombre único entre los productos activos
- CUANDO un cliente hace PUT con `dado_de_baja = false` y luego llama a `POST /productos-menu` con una fecha libre
- ENTONCES el PUT devuelve 200 y el POST devuelve 201

#### Scenario: MDD-61 Conflicto de nombre en la reactivación
- DADO un `MenuDelDia` dado de baja "Milanesa" y otro producto activo "Milanesa"
- CUANDO un cliente hace PUT del primero con `dado_de_baja = false`
- ENTONCES 409 y el menú sigue dado de baja

## MODIFIED Requirements

### Requirement: RESTRICT en la baja de componentes
Sin cambios de comportamiento: Plato, Bebida y Postre solo son bloqueados por menús ejecutivos y combos activos. Los registros `ProductoMenu` (que ahora referencian a `MenuDelDia`, no a productos arbitrarios) NO DEBEN bloquear la baja de ningún Plato, Bebida o Postre.

#### Scenario: MDD-62 Los registros ProductoMenu no afectan la baja de otros subtipos
- DADO un Plato, un Postre y una Bebida activos fuera de compuestos, y registros `ProductoMenu` vigentes sobre algún `MenuDelDia`
- CUANDO un cliente da de baja el Plato, el Postre y la Bebida
- ENTONCES las tres bajas se completan con éxito
