# Especificación delta: Gestión del Menú del Día

Capacidad modificada por el cambio `menus-frontend`. Se agregan el listado y la consulta por id; el alta, la modificación de fecha y el borrado no cambian.

## ADDED Requirements

### Requirement: Listado de menús del día
`GET /productos-menu` DEBE devolver 200 con la lista de todos los registros `ProductoMenu`, ordenados por `fecha` descendente, sin filtros ni paginación. Cada ítem DEBE exponer exactamente `id`, `producto_id`, `fecha`, `producto_nombre`, `producto_tipo` y `producto_dado_de_baja`, resueltos desde el producto asociado, que PUEDE ser de cualquiera de los cinco subtipos. El listado DEBE incluir los menús cuyo producto fue dado de baja, como historial. Las respuestas de alta y modificación conservan el contrato de `{id, producto_id, fecha}`.

#### Scenario: PMD-41 Listado vacío
- DADO que no existe ningún registro `ProductoMenu`
- CUANDO un cliente llama a `GET /productos-menu`
- ENTONCES 200 y el cuerpo es una lista vacía

#### Scenario: PMD-42 Orden por fecha descendente
- DADO menús del día en tres fechas distintas
- CUANDO un cliente llama a `GET /productos-menu`
- ENTONCES los ítems aparecen de la fecha más reciente a la más antigua

#### Scenario: PMD-43 El listado incluye los datos del producto
- DADO un menú del día asociado a un Plato activo
- CUANDO un cliente llama a `GET /productos-menu`
- ENTONCES el ítem contiene el `producto_id` y `producto_nombre`, `producto_tipo` y `producto_dado_de_baja` del Plato

#### Scenario: PMD-44 El listado incluye productos dados de baja
- DADO un menú del día cuyo producto fue dado de baja
- CUANDO un cliente llama a `GET /productos-menu`
- ENTONCES el ítem aparece con `producto_dado_de_baja = true`

#### Scenario: PMD-45 El ítem expone exactamente seis claves
- DADO un menú del día existente
- CUANDO un cliente llama a `GET /productos-menu`
- ENTONCES cada ítem contiene exactamente `id`, `producto_id`, `fecha`, `producto_nombre`, `producto_tipo` y `producto_dado_de_baja`

### Requirement: Consulta de un menú del día
`GET /productos-menu/{id}` DEBE devolver 200 con el mismo detalle enriquecido del listado. Un `id` inexistente DEBE devolver 404.

#### Scenario: PMD-46 Consulta de un menú existente
- DADO un menú del día existente
- CUANDO un cliente llama a `GET /productos-menu/{id}`
- ENTONCES 200 y el cuerpo coincide con el ítem correspondiente del listado

#### Scenario: PMD-47 Consulta de un id inexistente
- DADO un `id` que no corresponde a ningún registro
- CUANDO un cliente llama a `GET /productos-menu/{id}`
- ENTONCES 404
