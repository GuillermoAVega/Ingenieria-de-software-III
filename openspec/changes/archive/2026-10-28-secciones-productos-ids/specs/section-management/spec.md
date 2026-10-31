# Especificación Delta de la Gestión de Secciones: ids de productos

Especificación delta para el cambio `secciones-productos-ids`, aplicada sobre `section-management`. Códigos de estado: 422 = validación de esquema/campos, 404 = id inexistente, 409 = conflicto de regla de negocio.

**Alcance**: se agrega `productos_ids` a la respuesta de una sección. Este delta reemplaza la frase del encabezado de alcance de la especificación principal "La respuesta de una sección NO DEBE incluir la lista de sus productos" por: la respuesta de una sección PUEDE y DEBE incluir únicamente los ids de sus productos activos (`productos_ids`), y NO DEBE incluir objetos de producto embebidos. Siguen FUERA DE ALCANCE y NO DEBEN implementarse: listados de secciones, listados de productos por sección (cualquier endpoint que devuelva productos de una sección), objetos de producto embebidos, paginación, ordenamiento, baja lógica de secciones (`dado_de_baja`), reactivación, cambios en los cuerpos de entrada (la asignación de productos a una sección sigue haciéndose desde el producto), migraciones y Frontend.

**Efecto sobre los escenarios existentes**: todo escenario SEC-xx o POS-xx que verifique el cuerpo de una respuesta de sección se interpreta con la presencia adicional del campo `productos_ids`, sin que cambien sus demás resultados esperados. Los escenarios que se repiten a continuación conservan su texto salvo SEC-02, SEC-22 y SEC-30, que se actualizan.

## MODIFIED Requirements

### Requirement: Entidad Seccion
Una `Seccion` DEBE tener `id`, `nombre` (obligatorio), `subtitulo` (opcional) y `posicion` (entero obligatorio, único entre todas las secciones). La relación entre `Seccion` y `Producto` DEBE ser bidireccional (`Seccion.productos` / `Producto.seccion`, con `back_populates`) y todos los mappers DEBEN configurarse sin errores. La respuesta de una sección DEBE exponer `id`, `nombre`, `subtitulo`, `posicion` y `productos_ids`. `productos_ids` DEBE ser una lista de enteros (ids de producto) y NO DEBE contener objetos de producto. La respuesta NO DEBE exponer `dado_de_baja` ni ningún otro dato de los productos.

#### Scenario: SEC-01 Los mappers se configuran con la nueva entidad
- DADO que los modelos de sección y de producto están importados
- CUANDO se configuran los mappers de SQLAlchemy
- ENTONCES no se lanza ningún error

#### Scenario: SEC-02 La respuesta incluye los ids de productos y no el estado de baja
- DADO una sección con un Plato activo asignado
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES la respuesta contiene `id`, `nombre`, `subtitulo` y `productos_ids` con el id del Plato, y no contiene `dado_de_baja` ni objetos de producto

#### Scenario: POS-01 La respuesta de consulta incluye posicion
- DADO una sección con `posicion = 4`
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES 200 y la respuesta contiene `posicion = 4` junto con `id`, `nombre` y `subtitulo`

#### Scenario: IDS-01 productos_ids es una lista de enteros
- DADO una sección con dos productos activos asignados
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES `productos_ids` es una lista cuyos elementos son enteros, y la respuesta no contiene claves de producto como `nombre` de producto, `precio` ni `dado_de_baja`

### Requirement: Alta de sección
`POST /secciones` DEBE crear la sección y devolver 201 con la sección creada, incluido su `id`, su `posicion` y `productos_ids`. Una sección recién creada DEBE devolver `productos_ids = []`. Cuando falle más de una regla a la vez, la prioridad de los errores DEBE ser: 422 (esquema/campos) → 409 por `nombre` duplicado → 409 por `posicion` duplicada. Si colisionan `nombre` y `posicion` a la vez, DEBE devolverse un único 409 correspondiente al `nombre`; esta prioridad es determinista. Una solicitud rechazada NO DEBE crear ninguna sección.

#### Scenario: SEC-19 Crear sección con todos los campos
- DADO un cuerpo con `nombre = "Entradas"` y `subtitulo = "Para comenzar"`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y se devuelve la sección con un `id`, el `nombre` y el `subtitulo` informados

#### Scenario: SEC-20 Crear sección sin subtitulo
- DADO un cuerpo con `nombre = "Entradas"` y sin `subtitulo`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y el `subtitulo` devuelto es `null`

#### Scenario: SEC-21 Prioridad de 422 sobre 409 en el alta
- DADO una sección llamada "Entradas"
- CUANDO un cliente llama a `POST /secciones` con `nombre = "Entradas"` y un `subtitulo` de 201 caracteres
- ENTONCES 422

#### Scenario: POS-22 El alta devuelve la posicion informada
- DADO un cuerpo con `nombre = "Entradas"` y `posicion = 2`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y la respuesta contiene `posicion = 2`

#### Scenario: POS-23 Doble colisión en el alta devuelve el 409 de nombre
- DADO una sección "Entradas" con `posicion = 1`
- CUANDO un cliente llama a `POST /secciones` con `nombre = "Entradas"` y `posicion = 1`
- ENTONCES un único 409 cuyo `detail` corresponde al `nombre` duplicado y no se crea ninguna sección

#### Scenario: POS-24 Prioridad de 422 sobre 409 por posicion en el alta
- DADO una sección con `posicion = 1`
- CUANDO un cliente llama a `POST /secciones` con `posicion = 1` y un `subtitulo` de 201 caracteres
- ENTONCES 422

#### Scenario: IDS-02 El alta devuelve productos_ids vacío
- DADO un cuerpo válido con `nombre = "Entradas"` y `posicion = 1`, aunque existan productos con `seccion_id = null` o asignados a otras secciones
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y la respuesta contiene `productos_ids = []`

### Requirement: Consulta de sección por id
`GET /secciones/{id}` DEBE devolver 200 con la sección, incluido `productos_ids`, y 404 si el id no existe. NO DEBE existir `GET /secciones` (listado).

#### Scenario: SEC-22 Obtener una sección existente
- DADO una sección con id 3
- CUANDO un cliente llama a `GET /secciones/3`
- ENTONCES 200 con `id`, `nombre`, `subtitulo` y `productos_ids` de la sección

#### Scenario: SEC-23 Obtener una sección inexistente
- DADO que no existe ninguna sección con id 999
- CUANDO un cliente llama a `GET /secciones/999`
- ENTONCES 404

#### Scenario: SEC-24 No existe el listado de secciones
- DADO que la API está en ejecución
- CUANDO un cliente llama a `GET /secciones`
- ENTONCES la respuesta es 405 Method Not Allowed

#### Scenario: IDS-03 La consulta devuelve los ids de los productos activos
- DADO una sección con id 3 y un Plato activo con id 10 asignado a ella
- CUANDO un cliente llama a `GET /secciones/3`
- ENTONCES 200 y `productos_ids = [10]`

### Requirement: Modificación de sección
`PUT /secciones/{id}` DEBE ser un reemplazo completo: un `subtitulo` omitido DEBE interpretarse como `null` y `posicion` es obligatoria. DEBE devolver 200 con la sección modificada, incluida su `posicion` y `productos_ids`, y 404 si el id no existe. La modificación NO DEBE alterar la asignación de productos a la sección, y `productos_ids` en la respuesta DEBE reflejar el estado persistido de dicha asignación. `productos_ids` es de solo lectura: un cliente NO DEBE poder asignar ni desasignar productos enviándolo en el cuerpo, y un valor enviado no tiene efecto sobre la asignación. Cuando fallen varias reglas a la vez, la prioridad de los errores DEBE ser: 422 (esquema/campos) → 404 (id inexistente) → 409 por `nombre` duplicado → 409 por `posicion` duplicada. Si colisionan `nombre` y `posicion` a la vez, DEBE devolverse un único 409 correspondiente al `nombre`; esta prioridad es determinista. Una solicitud rechazada NO DEBE modificar ninguna sección.

#### Scenario: SEC-25 Modificar una sección
- DADO una sección "Entradas" con `subtitulo = "Para comenzar"`
- CUANDO un cliente le hace PUT con `nombre = "Aperitivos"` y `subtitulo = "Para compartir"`
- ENTONCES 200 y la sección devuelve los nuevos valores

#### Scenario: SEC-26 PUT como reemplazo completo
- DADO una sección con `subtitulo = "Para comenzar"`
- CUANDO un cliente le hace PUT sin `subtitulo`
- ENTONCES 200 y el `subtitulo` queda en `null`

#### Scenario: SEC-27 Actualizar una sección inexistente
- DADO que no existe ninguna sección con id 999
- CUANDO un cliente llama a `PUT /secciones/999` con un cuerpo válido
- ENTONCES 404

#### Scenario: SEC-28 Prioridad de 422 sobre 404 en la modificación
- DADO que no existe ninguna sección con id 999
- CUANDO un cliente hace PUT a `/secciones/999` con `nombre = ""`
- ENTONCES 422

#### Scenario: SEC-29 Prioridad de 404 sobre 409 en la modificación
- DADO una sección llamada "Entradas" y que no existe ninguna sección con id 999
- CUANDO un cliente hace PUT a `/secciones/999` con `nombre = "Entradas"`
- ENTONCES 404

#### Scenario: SEC-30 La modificación no altera los productos asignados
- DADO una sección con un Plato asignado
- CUANDO un cliente modifica la sección
- ENTONCES el Plato conserva su `seccion_id` y su id sigue figurando en `productos_ids` de la respuesta

#### Scenario: POS-25 La modificación devuelve la nueva posicion
- DADO una sección "Entradas" con `posicion = 1` y ninguna sección con `posicion = 7`
- CUANDO un cliente le hace PUT con `nombre = "Entradas"` y `posicion = 7`
- ENTONCES 200 y la respuesta contiene `posicion = 7`

#### Scenario: POS-26 Doble colisión en la modificación devuelve el 409 de nombre
- DADO las secciones "Entradas" con `posicion = 1` y "Postres" con `posicion = 2`
- CUANDO un cliente hace PUT de "Postres" con `nombre = "entradas"` y `posicion = 1`
- ENTONCES un único 409 cuyo `detail` corresponde al `nombre` duplicado y "Postres" conserva `nombre = "Postres"` y `posicion = 2`

#### Scenario: POS-27 Prioridad de 404 sobre 409 por posicion en la modificación
- DADO una sección con `posicion = 1` y que no existe ninguna sección con id 999
- CUANDO un cliente hace PUT a `/secciones/999` con un `nombre` válido y `posicion = 1`
- ENTONCES 404

#### Scenario: POS-28 Prioridad de 422 sobre 409 por posicion en la modificación
- DADO las secciones A con `posicion = 1` y B con `posicion = 2`
- CUANDO un cliente hace PUT de B con `posicion = 1` y un `subtitulo` de 201 caracteres
- ENTONCES 422 y B conserva `posicion = 2`

#### Scenario: IDS-04 La respuesta del PUT refleja el estado persistido
- DADO una sección con un Plato activo (id 10) y un Postre dado de baja (id 11) asignados
- CUANDO un cliente le hace PUT con un cuerpo válido
- ENTONCES 200, `productos_ids = [10]` en la respuesta y un `GET /secciones/{id}` posterior devuelve el mismo `productos_ids`

#### Scenario: IDS-05 Enviar productos_ids en el PUT no cambia la asignación
- DADO una sección con un Plato activo (id 10) asignado y un Postre activo (id 11) sin sección
- CUANDO un cliente le hace PUT con un cuerpo válido que además incluye `productos_ids = [11]`
- ENTONCES 200, `productos_ids = [10]` en la respuesta, el Plato conserva su `seccion_id` y el Postre conserva `seccion_id = null`

## ADDED Requirements

### Requirement: Ids de productos activos en la respuesta de la sección
La respuesta de toda sección (`POST /secciones`, `GET /secciones/{id}` y `PUT /secciones/{id}`) DEBE incluir `productos_ids`: la lista de ids de los productos cuyo `seccion_id` es el de la sección y cuyo `dado_de_baja` es `false`. Los productos dados de baja (`dado_de_baja = true`) NO DEBEN figurar, aunque sigan asignados a la sección. La lista DEBE estar en orden ascendente de id, sin repetidos, y DEBE ser `[]` cuando la sección no tiene productos activos. DEBEN contar los cinco subtipos de producto (Plato, Bebida, Postre, MenuEjecutivo y ComboPromocion). Un combo cuya vigencia (`fecha_hasta`) ya venció pero que no está dado de baja DEBE figurar, porque solo `dado_de_baja` define si un producto está activo. `productos_ids` DEBE calcularse a partir del estado persistido en cada respuesta: dar de baja o reactivar un producto, o cambiar su `seccion_id`, DEBE reflejarse en la siguiente respuesta sin ninguna acción sobre la sección. Esta capacidad NO DEBE agregar endpoints ni listados de productos por sección, y NO DEBE modificar la asignación de productos.

#### Scenario: IDS-06 Solo figuran los productos activos cuando hay activos y dados de baja
- DADO una sección con un Plato activo (id 10), una Bebida dada de baja (id 11) y un Postre activo (id 12) asignados
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES `productos_ids = [10, 12]`

#### Scenario: IDS-07 Una sección con solo productos dados de baja devuelve lista vacía
- DADO una sección con un Plato dado de baja asignado
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES `productos_ids = []`

#### Scenario: IDS-08 Los ids se devuelven en orden ascendente
- DADO tres productos activos con ids 10, 11 y 12, asignados a la sección en el orden 12, 10 y 11
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES `productos_ids = [10, 11, 12]`

#### Scenario: IDS-09 Cuentan los cinco subtipos
- DADO una sección con un Plato, una Bebida, un Postre, un MenuEjecutivo y un ComboPromocion activos asignados
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES `productos_ids` contiene los ids de los cinco productos, en orden ascendente

#### Scenario: IDS-10 Un combo vencido pero activo figura
- DADO un ComboPromocion con `fecha_hasta` de ayer y `dado_de_baja = false` asignado a una sección
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES `productos_ids` contiene el id del combo

#### Scenario: IDS-11 Dar de baja un producto lo hace desaparecer
- DADO una sección con un Plato activo (id 10) y una Bebida activa (id 11) asignados
- CUANDO un cliente da de baja el Plato y luego llama a `GET /secciones/{id}`
- ENTONCES `productos_ids = [11]` y el Plato conserva su `seccion_id`

#### Scenario: IDS-12 Reactivar un producto lo hace reaparecer
- DADO una sección con un Plato dado de baja (id 10) y una Bebida activa (id 11) asignados
- CUANDO un cliente reactiva el Plato y luego llama a `GET /secciones/{id}`
- ENTONCES `productos_ids = [10, 11]`

#### Scenario: IDS-13 Cambiar la sección de un producto lo mueve entre secciones
- DADO las secciones A y B, y un Plato activo (id 10) asignado a A
- CUANDO un cliente cambia el `seccion_id` del Plato a la sección B
- ENTONCES `GET` de A devuelve `productos_ids = []` y `GET` de B devuelve `productos_ids = [10]`

#### Scenario: IDS-14 Desasignar un producto lo quita de la sección
- DADO una sección con un Plato activo (id 10) asignado
- CUANDO un cliente deja el `seccion_id` del Plato en `null`
- ENTONCES `GET /secciones/{id}` devuelve `productos_ids = []`

#### Scenario: IDS-15 No figuran productos de otras secciones ni sin sección
- DADO las secciones A y B, un Plato activo (id 10) en A, un Postre activo (id 11) en B y una Bebida activa (id 12) sin sección
- CUANDO un cliente llama a `GET` de A
- ENTONCES `productos_ids = [10]`

#### Scenario: IDS-16 No quedan ids obsoletos tras borrar y crear una sección
- DADO una sección con un Plato activo (id 10) asignado que es borrada, y luego se crea una nueva sección
- CUANDO un cliente llama a `GET` de la nueva sección
- ENTONCES `productos_ids = []` y el Plato sigue existiendo con `seccion_id = null`

#### Scenario: IDS-17 No existe un listado de productos por sección
- DADO una sección con productos activos asignados
- CUANDO un cliente llama a `GET /secciones/{id}/productos`
- ENTONCES la respuesta es 404 porque la ruta no existe
