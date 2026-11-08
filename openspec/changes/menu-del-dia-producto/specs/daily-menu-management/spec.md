# Especificación Delta de la Gestión del Menú del Día: MenuDelDia como subtipo de Producto

Especificación delta para el cambio `menu-del-dia-producto`, aplicada sobre `daily-menu-management`. Códigos de estado: 422 = validación de esquema/campos o referencia inexistente en el cuerpo, 404 = id inexistente en la ruta, 409 = conflicto de regla de negocio.

**Alcance**: `ProductoMenu` deja de referenciar a un `Producto` cualquiera y pasa a registrar las fechas en que un `MenuDelDia` (subtipo de `Producto`, véase product-catalog) fue o será menú del día. Este delta REEMPLAZA la semántica de `producto_id` de la especificación principal por `menu_del_dia_id`: todo escenario PMD-xx que mencione `producto_id`, `Producto.menus_del_dia`, "producto dado de baja" o "producto asociado" se interpreta, salvo que se modifique abajo, con `menu_del_dia_id`, `MenuDelDia.fechas`, "menú del día dado de baja" y "menú del día asociado". El módulo `src/productos_menu/` y el prefijo `/productos-menu` se conservan. Siguen FUERA DE ALCANCE: filtros o paginación en el listado, el cambio de `menu_del_dia_id` de un registro existente, migración de datos existentes (los datos previos se descartan en desarrollo) y `Promocion`.

**Efecto sobre los escenarios existentes**: PMD-02, PMD-03, PMD-08, PMD-09 a PMD-14, PMD-16 a PMD-18, PMD-25, PMD-26, PMD-30, PMD-35, PMD-37 a PMD-40, PMD-43 a PMD-45 quedan reemplazados por los escenarios MDD-xx de este documento. Los demás (PMD-01, 04 a 07, 11, 12, 15, 19 a 24, 27 a 29, 31 a 34, 36, 41, 42, 46, 47) conservan su resultado esperado, sustituyendo `producto_id` por `menu_del_dia_id` y usando un `MenuDelDia` activo como referencia.

## RENAMED Requirements

### Requirement: Entidad ProductoMenu y relación con Producto → Entidad ProductoMenu y relación con MenuDelDia

(Reason: `ProductoMenu` deja de referenciar a cualquier `Producto` y pasa a pertenecer obligatoriamente a un `MenuDelDia`.)

### Requirement: Baja de productos que son menú del día → Baja lógica de un MenuDelDia y registros de fechas

(Reason: la baja ahora aplica al subtipo `MenuDelDia` y se bloquea si tiene fechas vigentes.)

### Requirement: Listado de menús del día → Listado y consulta de menús del día

(Reason: el listado y la consulta por id se unifican en un único requisito.)

### Requirement: Varios registros por producto → Varios registros por MenuDelDia

(Reason: los registros de fechas pertenecen a un `MenuDelDia`, no a cualquier producto.)

## REMOVED Requirements

### Requirement: Consulta de un menú del día

(Reason: su contenido se incorpora a "Listado y consulta de menús del día".)

## MODIFIED Requirements

### Requirement: Entidad ProductoMenu y relación con MenuDelDia
Un `ProductoMenu` DEBE tener `id`, `menu_del_dia_id` (obligatorio, referencia a un `MenuDelDia`) y `fecha` (fecha calendario obligatoria). La fecha DEBE ser única entre todos los registros (restricción UNIQUE). La relación entre `ProductoMenu` y `MenuDelDia` DEBE ser bidireccional (`ProductoMenu.menu_del_dia` / `MenuDelDia.fechas`, con `back_populates`, cardinalidad 0..N del lado del `MenuDelDia`; cada `ProductoMenu` pertenece exactamente a un `MenuDelDia`) y todos los mappers DEBEN configurarse sin errores. `ProductoMenu` NO DEBE tener `producto_id` y `Producto.menus_del_dia` NO DEBE existir. La respuesta de alta y modificación DEBE exponer únicamente `id`, `menu_del_dia_id` y `fecha`.

#### Scenario: MDD-01 La relación es bidireccional
- DADO un registro `ProductoMenu` asociado a un `MenuDelDia`
- CUANDO se accede a `ProductoMenu.menu_del_dia` y a `MenuDelDia.fechas`
- ENTONCES `menu_del_dia` devuelve el menú asociado y `fechas` contiene el registro

#### Scenario: MDD-02 La respuesta expone solo id, menu_del_dia_id y fecha
- DADO un alta válida
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES el cuerpo de la respuesta contiene exactamente las claves `id`, `menu_del_dia_id` y `fecha`, y no contiene `producto_id`

#### Scenario: MDD-03 Un MenuDelDia sin fechas es válido
- DADO un `MenuDelDia` sin registros `ProductoMenu`
- CUANDO se accede a `MenuDelDia.fechas`
- ENTONCES la colección está vacía

### Requirement: Alta de un menú del día
`POST /productos-menu` con `{menu_del_dia_id, fecha}` DEBE crear el registro y devolver 201 con `{id, menu_del_dia_id, fecha}`. La `fecha` PUEDE ser pasada, la de hoy o futura. El `menu_del_dia_id` DEBE referir a un `MenuDelDia`; un producto de cualquier otro subtipo NO es una referencia válida.

#### Scenario: MDD-04 Alta válida
- DADO un `MenuDelDia` activo y una fecha sin registro
- CUANDO un cliente llama a `POST /productos-menu` con `menu_del_dia_id` y `fecha`
- ENTONCES 201, el cuerpo contiene `id`, `menu_del_dia_id` y `fecha` iguales a los enviados, y el registro queda persistido

#### Scenario: MDD-05 Un id de producto de otro subtipo se rechaza
- DADO un Plato activo (o un MenuEjecutivo, Postre, Bebida o ComboPromocion) cuyo id se envía como `menu_del_dia_id`
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 y no se crea ningún registro

### Requirement: Validación del alta
`menu_del_dia_id` es obligatorio y DEBE ser un entero; `fecha` es obligatoria y DEBE ser una fecha válida. Un `menu_del_dia_id` ausente o no entero DEBE devolver 422; una `fecha` ausente o inválida DEBE devolver 422. Un `menu_del_dia_id` entero que no corresponda a ningún `MenuDelDia` DEBE devolver 422. Un `MenuDelDia` dado de baja DEBE devolver 409. Una `fecha` ya ocupada por otro registro DEBE devolver 409. Cuando concurran varios errores, la prioridad DEBE ser: esquema 422, `MenuDelDia` inexistente 422, `MenuDelDia` dado de baja 409, fecha ocupada 409. Una solicitud rechazada NO DEBE modificar el estado persistido. Ante una carrera entre dos altas con la misma fecha, la violación del índice UNIQUE DEBE traducirse a 409.

#### Scenario: MDD-06 menu_del_dia_id ausente
- DADO un cuerpo sin el campo `menu_del_dia_id` (incluido un cuerpo que solo envía el antiguo `producto_id`)
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 y no se crea ningún registro

#### Scenario: MDD-07 menu_del_dia_id no entero
- DADO un cuerpo con `menu_del_dia_id = "abc"`
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 y no se crea ningún registro

#### Scenario: MDD-08 MenuDelDia inexistente
- DADO un `menu_del_dia_id` entero que no corresponde a ningún `MenuDelDia`
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 y no se crea ningún registro

#### Scenario: MDD-09 MenuDelDia dado de baja
- DADO un `MenuDelDia` con `dado_de_baja = true` y una fecha libre
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 409, el mensaje de error identifica que el menú del día está dado de baja y no se crea ningún registro

#### Scenario: MDD-10 Fecha ocupada
- DADO un registro existente con `fecha = F` y un `MenuDelDia` activo distinto o el mismo
- CUANDO un cliente llama a `POST /productos-menu` con `fecha = F`
- ENTONCES 409, el registro existente permanece sin cambios y no se crea otro

#### Scenario: MDD-11 Esquema inválido prevalece sobre MenuDelDia inexistente
- DADO un cuerpo con `menu_del_dia_id` inexistente y `fecha` ausente
- CUANDO un cliente llama a `POST /productos-menu`
- ENTONCES 422 por validación de esquema

#### Scenario: MDD-12 MenuDelDia inexistente prevalece sobre fecha ocupada
- DADO una fecha ocupada y un `menu_del_dia_id` inexistente
- CUANDO un cliente llama a `POST /productos-menu` con esa fecha y ese id
- ENTONCES 422 por menú del día inexistente, no 409

#### Scenario: MDD-13 MenuDelDia dado de baja prevalece sobre fecha ocupada
- DADO una fecha ocupada y un `MenuDelDia` dado de baja
- CUANDO un cliente llama a `POST /productos-menu` con esa fecha y ese menú
- ENTONCES 409 cuyo mensaje identifica el menú dado de baja, no la fecha ocupada

#### Scenario: MDD-14 Una solicitud rechazada no cambia nada
- DADO un conjunto de registros existentes
- CUANDO una llamada a `POST /productos-menu` es rechazada con 422 o 409
- ENTONCES el conjunto de registros persistidos es idéntico al previo

### Requirement: Modificación de la fecha de un menú del día
`PUT /productos-menu/{id}` DEBE aceptar únicamente `fecha` y devolver 200 con `{id, menu_del_dia_id, fecha}` actualizado. Conservar la fecha propia del registro DEBE ser válido. Mover el registro a una fecha libre DEBE ser válido. Una fecha ocupada por OTRO registro DEBE devolver 409. Un `id` inexistente DEBE devolver 404. Si el `MenuDelDia` asociado está dado de baja, DEBE devolver 409. Un `menu_del_dia_id` (o `producto_id`) incluido en el cuerpo DEBE ignorarse y NO DEBE modificar el menú asociado. Cuando concurran varios errores, la prioridad DEBE ser: esquema 422, id inexistente 404, `MenuDelDia` dado de baja 409, fecha ocupada por otro registro 409. Una solicitud rechazada NO DEBE modificar el estado persistido.

#### Scenario: MDD-15 Menú del día dado de baja en el PUT
- DADO un registro cuyo `MenuDelDia` fue dado de baja posteriormente (solo con fechas pasadas) y una fecha libre
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con esa fecha
- ENTONCES 409 y la fecha del registro no cambia

#### Scenario: MDD-16 menu_del_dia_id en el cuerpo se ignora
- DADO un registro asociado al `MenuDelDia` A y un `MenuDelDia` B activo
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con `{fecha, menu_del_dia_id: B}`
- ENTONCES 200, la fecha se actualiza y el `menu_del_dia_id` del registro sigue siendo A

#### Scenario: MDD-17 Menú del día dado de baja prevalece sobre fecha ocupada en el PUT
- DADO un registro cuyo `MenuDelDia` está dado de baja y una fecha ocupada por otro registro
- CUANDO un cliente llama a `PUT /productos-menu/{id}` con esa fecha
- ENTONCES 409 cuyo mensaje identifica el menú dado de baja, no la fecha ocupada

### Requirement: Borrado físico de un menú del día
Se conserva sin cambios: `DELETE /productos-menu/{id}` elimina físicamente el registro y devuelve 204; un `id` inexistente o repetido devuelve 404; NO verifica el estado (`dado_de_baja`) del `MenuDelDia` asociado; la fecha liberada puede reutilizarse.

#### Scenario: MDD-18 El borrado no verifica el estado del MenuDelDia
- DADO un registro cuyo `MenuDelDia` está dado de baja
- CUANDO un cliente llama a `DELETE /productos-menu/{id}`
- ENTONCES 204 y el registro se elimina

### Requirement: Baja lógica de un MenuDelDia y registros de fechas
El bloqueo de la baja de un `MenuDelDia` con fechas `>= hoy` se define en product-logical-delete. Cuando la baja se permite (solo fechas pasadas), los registros `ProductoMenu` del menú dado de baja DEBEN permanecer como historial con su `menu_del_dia_id` y `fecha` originales. La baja lógica de cualquier producto de otro subtipo NO DEBE verse afectada por la existencia de registros `ProductoMenu` (no existe relación entre ambos).

#### Scenario: MDD-19 Los registros pasados permanecen tras la baja
- DADO un `MenuDelDia` con dos registros de fecha pasada que se da de baja con éxito
- CUANDO se consultan los registros persistidos
- ENTONCES ambos registros siguen existiendo con su `menu_del_dia_id` y `fecha` originales

#### Scenario: MDD-20 Un MenuDelDia con fechas es un producto como cualquier otro en su respuesta
- DADO un `MenuDelDia` con un registro `ProductoMenu`
- CUANDO un cliente lo consulta por `GET /productos/menus-del-dia/{id}`
- ENTONCES la respuesta no contiene `fechas`, `menus_del_dia` ni claves relacionadas con `ProductoMenu`

### Requirement: Listado y consulta de menús del día
`GET /productos-menu` DEBE devolver 200 con la lista de todos los registros, ordenados por `fecha` descendente, sin filtros ni paginación. `GET /productos-menu/{id}` DEBE devolver el mismo detalle para un registro (404 si no existe). Cada ítem DEBE exponer exactamente `id`, `menu_del_dia_id`, `fecha`, `menu_del_dia_nombre` y `menu_del_dia_dado_de_baja`, resueltos desde el `MenuDelDia` asociado. El listado DEBE incluir los registros cuyo menú fue dado de baja, como historial. Ya no se exponen `producto_id`, `producto_nombre`, `producto_tipo` ni `producto_dado_de_baja`.

#### Scenario: MDD-21 El listado incluye los datos del menú del día
- DADO un registro asociado a un `MenuDelDia` activo
- CUANDO un cliente llama a `GET /productos-menu`
- ENTONCES el ítem contiene exactamente `id`, `menu_del_dia_id`, `fecha`, `menu_del_dia_nombre` y `menu_del_dia_dado_de_baja = false`

#### Scenario: MDD-22 El listado incluye menús dados de baja
- DADO un registro de fecha pasada cuyo `MenuDelDia` fue dado de baja
- CUANDO un cliente llama a `GET /productos-menu`
- ENTONCES el ítem aparece con `menu_del_dia_dado_de_baja = true`

#### Scenario: MDD-23 La consulta por id coincide con el listado
- DADO un registro existente
- CUANDO un cliente llama a `GET /productos-menu/{id}`
- ENTONCES 200 y el cuerpo coincide con el ítem correspondiente del listado

### Requirement: Varios registros por MenuDelDia
Un mismo `MenuDelDia` PUEDE tener varios registros en fechas distintas, lo que permite reutilizarlo sin duplicar el producto por fecha.

#### Scenario: MDD-24 Un MenuDelDia con varias fechas
- DADO un `MenuDelDia` activo
- CUANDO un cliente llama a `POST /productos-menu` dos veces con ese menú y fechas distintas
- ENTONCES ambas llamadas devuelven 201 y `MenuDelDia.fechas` contiene los dos registros

## ADDED Requirements

### Requirement: Frontend del menú del día
La pantalla de alta y edición del menú del día (`features/daily-menu/`) DEBE permitir elegir un `MenuDelDia` existente y una fecha, y DEBE enviar `menu_del_dia_id` y `fecha` a `/productos-menu`. El selector DEBE ofrecer únicamente `MenuDelDia` activos (obtenidos de `/productos/menus-del-dia`). Al editar un registro existente solo la fecha es modificable. El listado de menús del día DEBE mostrar el nombre del menú del día y la fecha, e indicar los menús dados de baja. Los errores 409 y 422 del backend DEBEN mostrarse al usuario en español. Los mensajes de interfaz DEBEN estar en español. La lógica DEBE residir en hooks de la feature con un único objeto de estado, sin llamadas directas a `fetch` desde componentes.

#### Scenario: MDD-25 Alta eligiendo un MenuDelDia
- DADO que existen menús del día activos y la pantalla de alta del menú del día
- CUANDO la persona usuaria elige un menú del día, indica una fecha y envía el formulario
- ENTONCES la solicitud a `POST /productos-menu` contiene `menu_del_dia_id` y `fecha` (sin `producto_id`) y la persona regresa al listado con el nuevo registro

#### Scenario: MDD-26 El selector excluye menús dados de baja
- DADO un `MenuDelDia` activo y otro dado de baja
- CUANDO se abre el formulario de alta
- ENTONCES el selector ofrece solo el menú activo

#### Scenario: MDD-27 Fecha ocupada o menú dado de baja se informan
- DADO un alta rechazada por el backend con 409
- CUANDO la persona usuaria envía el formulario
- ENTONCES se muestra un mensaje de error en español y el formulario conserva los valores ingresados

#### Scenario: MDD-28 Edición solo de la fecha
- DADO un registro existente
- CUANDO la persona usuaria abre su edición
- ENTONCES el menú del día se muestra sin posibilidad de cambiarlo y la fecha es editable; el guardado envía solo `fecha` a `PUT /productos-menu/{id}`

#### Scenario: MDD-29 El listado muestra el nombre del menú del día
- DADO registros asociados a menús del día, uno de ellos dado de baja
- CUANDO se abre la pestaña "Menú del día"
- ENTONCES cada fila muestra el nombre del menú del día y la fecha, y la fila del menú dado de baja lo indica
