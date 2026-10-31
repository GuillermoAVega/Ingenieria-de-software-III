# Especificación del Catálogo de Productos

Especificación delta para el cambio `secciones-backend`. Códigos de estado: 422 = validación de esquema/campos y referencias inexistentes, 404 = id inexistente, 409 = conflicto de regla de negocio. Este cambio agrega la asignación opcional de un producto a una `Seccion` mediante `seccion_id` y actualiza la prioridad de los errores para reflejar el orden real de las validaciones.

## ADDED Requirements

### Requirement: Asignación de producto a una sección
Los cinco subtipos (Plato, Bebida, Postre, MenuEjecutivo y ComboPromocion) DEBEN aceptar un campo opcional `seccion_id` (entero) en el POST y en el PUT, y sus respuestas DEBEN exponerlo (`null` si no tiene sección). Un `seccion_id` que no corresponde a ninguna sección existente DEBE devolver 422 y no modificar nada. El PUT es un reemplazo completo: si se omite `seccion_id`, DEBE quedar en `null`. Un producto PUEDE asignarse a una sección sin importar su `dado_de_baja`. Asignar o cambiar la sección NO DEBE alterar ningún otro campo del producto ni la unicidad de su `nombre`.

#### Scenario: CAT-S-01 Crear producto con sección
- DADO una sección con id 2
- CUANDO un cliente llama a `POST /productos/platos` con un cuerpo válido y `seccion_id = 2`
- ENTONCES 201 y la respuesta incluye `seccion_id = 2`

#### Scenario: CAT-S-02 Crear producto sin sección
- DADO un cuerpo de Plato válido sin `seccion_id`
- CUANDO un cliente llama a `POST /productos/platos`
- ENTONCES 201 y la respuesta incluye `seccion_id = null`

#### Scenario: CAT-S-03 Crear producto con sección inexistente
- DADO que no existe ninguna sección con id 999
- CUANDO un cliente llama a `POST /productos/platos` con un cuerpo válido y `seccion_id = 999`
- ENTONCES 422 y no se crea ningún producto

#### Scenario: CAT-S-04 Todos los subtipos aceptan seccion_id en el alta
- DADO una sección con id 2 y cuerpos válidos de Bebida, Postre, MenuEjecutivo y ComboPromocion con `seccion_id = 2`
- CUANDO un cliente los envía a sus rutas `POST` respectivas
- ENTONCES cada respuesta es 201 e incluye `seccion_id = 2`

#### Scenario: CAT-S-05 Todos los subtipos rechazan una sección inexistente en el alta
- DADO que no existe ninguna sección con id 999 y cuerpos válidos de Bebida, Postre, MenuEjecutivo y ComboPromocion con `seccion_id = 999`
- CUANDO un cliente los envía a sus rutas `POST` respectivas
- ENTONCES cada respuesta es 422

#### Scenario: CAT-S-06 Modificar la sección de un producto
- DADO un Plato en la sección 2 y una sección con id 3
- CUANDO un cliente le hace PUT con un cuerpo válido y `seccion_id = 3`
- ENTONCES 200 y la respuesta incluye `seccion_id = 3`

#### Scenario: CAT-S-07 PUT sin seccion_id desasigna la sección
- DADO un Plato asignado a la sección 2
- CUANDO un cliente le hace PUT con un cuerpo válido y sin `seccion_id`
- ENTONCES 200 y `seccion_id` queda en `null`

#### Scenario: CAT-S-08 PUT con sección inexistente
- DADO un Plato asignado a la sección 2 y que no existe ninguna sección con id 999
- CUANDO un cliente le hace PUT con un cuerpo válido y `seccion_id = 999`
- ENTONCES 422 y el Plato conserva `seccion_id = 2`

#### Scenario: CAT-S-09 Todos los subtipos aceptan y rechazan seccion_id en el PUT
- DADO un Plato, una Bebida, un Postre, un MenuEjecutivo y un ComboPromocion vigente
- CUANDO un cliente hace PUT de cada uno con un cuerpo válido y `seccion_id` de una sección existente, y luego con `seccion_id = 999`
- ENTONCES el primer PUT devuelve 200 con ese `seccion_id` y el segundo devuelve 422

#### Scenario: CAT-S-10 La consulta por id expone seccion_id
- DADO un Postre asignado a la sección 2
- CUANDO un cliente llama a `GET /productos/postres/{id}`
- ENTONCES 200 con `seccion_id = 2`

#### Scenario: CAT-S-11 Asignar sección a un producto dado de baja
- DADO un Postre dado de baja
- CUANDO un cliente le hace PUT con un cuerpo válido, `dado_de_baja = true` y `seccion_id` de una sección existente
- ENTONCES 200, el Postre sigue dado de baja y tiene esa sección

#### Scenario: CAT-S-12 La sección no afecta la unicidad del nombre
- DADO un Plato activo "Milanesa" en la sección 2
- CUANDO un cliente crea otro producto llamado "Milanesa" en la sección 3
- ENTONCES 409

#### Scenario: CAT-S-13 seccion_id de tipo inválido
- DADO un cuerpo de Plato válido con `seccion_id = "abc"`
- CUANDO un cliente llama a `POST /productos/platos`
- ENTONCES 422

## MODIFIED Requirements

### Requirement: Rutas ABM por subtipo
La API DEBE exponer `/productos/platos`, `/productos/bebidas`, `/productos/postres`, `/productos/menus-ejecutivos`, `/productos/combos`, cada una con alta (POST), obtención por id (`GET /productos/<subtype>/{id}`), modificación (PUT) y baja lógica (DELETE, véase product-logical-delete). La API NO DEBE exponer listados (`GET /productos`, `GET /productos/<subtype>`), consulta polimórfica por id (`GET /productos/{id}`) ni el parámetro `?incluir_bajas`. POST DEBE devolver 201. `GET /productos/<subtype>/{id}` DEBE devolver el producto aunque esté dado de baja (con `dado_de_baja` visible) y DEBE devolver 404 si el id no existe o pertenece a otro subtipo. El PUT DEBE ser un reemplazo completo: un campo opcional omitido (incluido `seccion_id`) DEBE interpretarse como `null`, salvo `dado_de_baja`, que, si se omite, DEBE conservar el estado actual del producto. Cuando fallen varias reglas a la vez, la prioridad de los errores DEBE ser, en este orden: 422 (esquema/campos) → 404 (id inexistente) → 409 (combo vencido) → 422 (referencias inexistentes o de tipo incorrecto: ids de componentes y `seccion_id`) → 409 (componentes inactivos) → 409 (`nombre` duplicado). Las reglas que no aplican a un subtipo se omiten sin alterar el orden relativo de las restantes. En el alta, el orden es el mismo sin el paso 404 y con el rechazo por `fecha_hasta` vencida (422) en el paso de referencias.

#### Scenario: Crear plato
- DADO un cuerpo de Plato válido
- CUANDO un cliente llama a `POST /productos/platos`
- ENTONCES 201 y se devuelve el Plato creado con un id

#### Scenario: Id de subtipo incorrecto
- DADO una Bebida con id 3
- CUANDO un cliente llama a `GET /productos/platos/3`
- ENTONCES 404

#### Scenario: Obtener por id un producto dado de baja
- DADO un Postre dado de baja con id 5
- CUANDO un cliente llama a `GET /productos/postres/5`
- ENTONCES 200 con `dado_de_baja = true`

#### Scenario: Actualizar un id desconocido
- DADO que no existe ningún Plato con id 999
- CUANDO un cliente llama a `PUT /productos/platos/999`
- ENTONCES 404

#### Scenario: PUT sin dado_de_baja conserva el estado actual
- DADO un Plato dado de baja
- CUANDO un cliente le hace PUT con una nueva `descripcion` válida y sin el campo `dado_de_baja`
- ENTONCES 200 y el Plato sigue dado de baja

#### Scenario: PUT como reemplazo completo
- DADO un Plato con `descripcion` e `imagen` definidas
- CUANDO un cliente le hace PUT sin `descripcion` ni `imagen`
- ENTONCES 200 y ambos campos quedan en `null`

#### Scenario: Prioridad de errores 422 sobre 404
- DADO que no existe ningún Plato con id 999
- CUANDO un cliente hace PUT a `/productos/platos/999` con `precio = 0`
- ENTONCES 422

#### Scenario: CAT-S-14 Prioridad de 404 sobre 422 por sección inexistente
- DADO que no existe ningún Plato con id 999 ni ninguna sección con id 888
- CUANDO un cliente hace PUT a `/productos/platos/999` con un cuerpo válido y `seccion_id = 888`
- ENTONCES 404

#### Scenario: CAT-S-15 Prioridad de 422 de esquema sobre 422 de sección
- DADO un Plato existente
- CUANDO un cliente le hace PUT con `precio = 0` y `seccion_id` inexistente
- ENTONCES 422 por la validación de campos y el Plato no cambia

#### Scenario: CAT-S-16 Prioridad de combo vencido (409) sobre sección inexistente (422)
- DADO un combo con `fecha_hasta` de ayer y que no existe ninguna sección con id 999
- CUANDO un cliente le hace PUT con `seccion_id = 999`
- ENTONCES 409

#### Scenario: CAT-S-17 Prioridad de sección inexistente (422) sobre componente inactivo (409)
- DADO un menú activo, un Postre dado de baja y que no existe ninguna sección con id 999
- CUANDO un cliente le hace PUT con ese `postre_id` y `seccion_id = 999`
- ENTONCES 422

#### Scenario: CAT-S-18 Prioridad de sección inexistente (422) sobre nombre duplicado (409)
- DADO dos Platos activos "Milanesa" y "Tarta", y que no existe ninguna sección con id 999
- CUANDO un cliente hace PUT de "Tarta" con `nombre = "Milanesa"` y `seccion_id = 999`
- ENTONCES 422

#### Scenario: CAT-S-19 Prioridad de componente inactivo (409) sobre nombre duplicado (409)
- DADO un menú activo "Menú A", otro producto activo "Menú B" y un Postre dado de baja
- CUANDO un cliente hace PUT del menú "Menú A" con `nombre = "Menú B"` y ese `postre_id`
- ENTONCES 409 por el componente inactivo, no por el nombre duplicado

#### Scenario: CAT-S-20 Prioridad de referencias inexistentes (422) sobre componente inactivo (409) en un combo
- DADO un combo vigente con una Bebida dada de baja en `bebidas_ids` y un id inexistente en `platos_ids`
- CUANDO un cliente hace PUT del combo con ambos ids
- ENTONCES 422

### Requirement: Campos específicos por subtipo
Plato DEBE requerir `cant_personas` (int >= 1). Postre DEBE aceptar solo los campos comunes. Bebida DEBE requerir `es_alcoholica` (bool). MenuEjecutivo DEBE requerir `plato_id` y `postre_id`. ComboPromocion DEBE requerir `fecha_desde`, `fecha_hasta` (con `fecha_desde <= fecha_hasta`) y tres listas de componentes: `platos_ids`, `bebidas_ids` y `postres_ids`. Además, todos los subtipos DEBEN aceptar el campo común opcional `seccion_id` (véase "Asignación de producto a una sección"); este campo NO se considera un campo específico de ningún subtipo ni vuelve obligatorio ningún campo adicional.

#### Scenario: Bebida sin es_alcoholica
- DADO un cuerpo de Bebida sin `es_alcoholica`
- CUANDO un cliente llama a `POST /productos/bebidas`
- ENTONCES 422

#### Scenario: cant_personas inválido
- DADO un cuerpo de Plato con `cant_personas = 0`
- CUANDO un cliente llama a `POST /productos/platos`
- ENTONCES 422

#### Scenario: Rango de fechas invertido
- DADO un combo con `fecha_desde` posterior a `fecha_hasta`
- CUANDO se crea
- ENTONCES 422

#### Scenario: CAT-S-21 El Postre acepta seccion_id además de los campos comunes
- DADO un cuerpo de Postre con los campos comunes y `seccion_id` de una sección existente
- CUANDO un cliente llama a `POST /productos/postres`
- ENTONCES 201 y la respuesta incluye ese `seccion_id`

### Requirement: Los combos vencidos son inmutables
Cualquier PUT sobre un ComboPromocion cuya `fecha_hasta < today` (edición, reactivación o cambio de `seccion_id`) DEBE devolver 409 y no cambiar nada. Única excepción: un PUT que establece `dado_de_baja = true` sin modificar ningún otro campo sobre un combo vencido DEBE aceptarse (equivale al DELETE lógico, que está permitido y es idempotente). A estos efectos, `seccion_id` forma parte de los campos comparados para determinar que no hay "otros cambios": el PUT DEBE enviar el mismo `seccion_id` que el combo tiene persistido (o `null` si no tiene sección); omitirlo o enviar uno distinto cuando el combo tiene sección constituye un cambio y DEBE devolver 409. Si el combo vencido está activo, queda dado de baja; si ya está dado de baja, DEBE devolver 200 sin ningún cambio (idempotente, coherente con DELETE repetido → 204). Cualquier otro cambio sobre un combo vencido sigue devolviendo 409. La inmutabilidad NO impide que el borrado de la sección deje el `seccion_id` del combo en `null` (véase section-management).

#### Scenario: Editar un combo vencido
- DADO un combo con `fecha_hasta` de ayer
- CUANDO un cliente hace PUT con una nueva `descripcion`
- ENTONCES 409

#### Scenario: Reactivar un combo vencido
- DADO un combo dado de baja con `fecha_hasta` de ayer
- CUANDO un cliente hace PUT con `dado_de_baja = false`
- ENTONCES 409

#### Scenario: Dar de baja un combo vencido vía PUT
- DADO un combo activo con `fecha_hasta` de ayer
- CUANDO un cliente hace PUT con `dado_de_baja = true` y el resto de los campos sin cambios
- ENTONCES 200 y el combo queda dado de baja

#### Scenario: Dar de baja de nuevo un combo vencido ya dado de baja vía PUT
- DADO un combo dado de baja con `fecha_hasta` de ayer
- CUANDO un cliente hace PUT con `dado_de_baja = true` y el resto de los campos sin cambios
- ENTONCES 200 y el combo no cambia (idempotente)

#### Scenario: Dar de baja un combo vencido vía PUT modificando otros campos
- DADO un combo activo con `fecha_hasta` de ayer
- CUANDO un cliente hace PUT con `dado_de_baja = true` y un nuevo `precio`
- ENTONCES 409 y el combo no cambia

#### Scenario: CAT-S-22 Cambiar seccion_id en un combo vencido
- DADO un combo con `fecha_hasta` de ayer asignado a la sección 2 y una sección con id 3
- CUANDO un cliente hace PUT con el resto de los campos sin cambios y `seccion_id = 3`
- ENTONCES 409 y el combo conserva `seccion_id = 2`

#### Scenario: CAT-S-23 Asignar sección a un combo vencido sin sección
- DADO un combo con `fecha_hasta` de ayer sin sección y una sección con id 3
- CUANDO un cliente hace PUT con `seccion_id = 3` y el resto de los campos sin cambios
- ENTONCES 409 y el combo conserva `seccion_id = null`

#### Scenario: CAT-S-24 Dar de baja un combo vencido conservando su seccion_id
- DADO un combo activo con `fecha_hasta` de ayer asignado a la sección 2
- CUANDO un cliente hace PUT con `dado_de_baja = true`, `seccion_id = 2` y el resto de los campos sin cambios
- ENTONCES 200, el combo queda dado de baja y conserva `seccion_id = 2`

#### Scenario: CAT-S-25 Dar de baja un combo vencido omitiendo seccion_id
- DADO un combo activo con `fecha_hasta` de ayer asignado a la sección 2
- CUANDO un cliente hace PUT con `dado_de_baja = true`, sin `seccion_id` y el resto de los campos sin cambios
- ENTONCES 409 y el combo sigue activo con `seccion_id = 2`

#### Scenario: CAT-S-26 Dar de baja un combo vencido sin sección
- DADO un combo activo con `fecha_hasta` de ayer sin sección
- CUANDO un cliente hace PUT con `dado_de_baja = true`, sin `seccion_id` y el resto de los campos sin cambios
- ENTONCES 200 y el combo queda dado de baja con `seccion_id = null`

#### Scenario: CAT-S-27 Dar de baja un combo vencido vía DELETE no altera la sección
- DADO un combo activo con `fecha_hasta` de ayer asignado a la sección 2
- CUANDO un cliente llama a `DELETE /productos/combos/{id}`
- ENTONCES 204 y el combo conserva `seccion_id = 2`

#### Scenario: CAT-S-28 Un combo vigente puede cambiar de sección
- DADO un combo vigente asignado a la sección 2 y una sección con id 3
- CUANDO un cliente le hace PUT con un cuerpo válido y `seccion_id = 3`
- ENTONCES 200 y el combo tiene `seccion_id = 3`
