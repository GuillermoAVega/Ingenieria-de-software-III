# Especificación de la Gestión de Secciones

Especificación principal de la capacidad, consolidada a partir de los cambios `secciones-backend`, `secciones-posicion` y `secciones-productos-ids`. Códigos de estado: 422 = validación de esquema/campos, 404 = id inexistente, 409 = conflicto de regla de negocio.

**Alcance**: esta capacidad cubre el alta, el listado, la consulta por id, la modificación y el borrado físico de secciones. Quedan explícitamente FUERA DE ALCANCE y NO DEBEN implementarse: listados de productos por sección, endpoints de ordenamiento o reordenamiento (el orden del listado lo determina `posicion`), baja lógica de secciones (`dado_de_baja`) y reactivación. La respuesta de una sección PUEDE y DEBE incluir únicamente los ids de sus productos activos (`productos_ids`), y NO DEBE incluir objetos de producto embebidos.

## ADDED Requirements

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

### Requirement: Validación de campos de la sección
`nombre` es obligatorio. DEBE recortarse (trim) de espacios iniciales y finales antes de validarlo, almacenarlo y comprobar su unicidad. Tras el recorte DEBE tener de 1 a 100 caracteres; un `nombre` ausente, vacío o compuesto solo de espacios DEBE devolver 422, y uno de más de 100 caracteres DEBE devolver 422. `subtitulo` es opcional y DEBE recortarse (trim) de espacios iniciales y finales antes de validarlo y almacenarlo. Un `subtitulo` vacío o compuesto solo de espacios, una vez recortado, DEBE almacenarse como `null`. Tras el recorte DEBE tener como máximo 200 caracteres (de lo contrario, 422).

#### Scenario: SEC-03 nombre vacío
- DADO un cuerpo con `nombre = ""`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422 y no se crea ninguna sección

#### Scenario: SEC-04 nombre compuesto solo de espacios
- DADO un cuerpo con `nombre = "   "`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422

#### Scenario: SEC-05 nombre ausente
- DADO un cuerpo sin el campo `nombre`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422

#### Scenario: SEC-06 nombre se recorta antes de almacenarse
- DADO un cuerpo con `nombre = "  Entradas "`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y el `nombre` devuelto es "Entradas"

#### Scenario: SEC-07 nombre en el límite de 100 caracteres
- DADO un `nombre` de exactamente 100 caracteres
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201

#### Scenario: SEC-08 nombre demasiado largo
- DADO un `nombre` de 101 caracteres
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422

#### Scenario: SEC-09 subtitulo en el límite de 200 caracteres
- DADO un `subtitulo` de exactamente 200 caracteres
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201

#### Scenario: SEC-10 subtitulo demasiado largo
- DADO un `subtitulo` de 201 caracteres
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422

#### Scenario: SEC-39 subtitulo se recorta antes de almacenarse
- DADO un cuerpo con `subtitulo = "  Para comenzar "`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y el `subtitulo` devuelto es "Para comenzar"

#### Scenario: SEC-40 subtitulo vacío se almacena como null
- DADO un cuerpo con `subtitulo = ""`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y el `subtitulo` devuelto es `null`

#### Scenario: SEC-41 subtitulo compuesto solo de espacios se almacena como null
- DADO un cuerpo con `subtitulo = "   "`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y el `subtitulo` devuelto es `null`

#### Scenario: SEC-42 El límite de subtitulo se verifica tras el recorte
- DADO un `subtitulo` de 200 caracteres rodeado de espacios (más de 200 caracteres en total)
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y el `subtitulo` devuelto tiene 200 caracteres

#### Scenario: SEC-43 subtitulo demasiado largo tras el recorte
- DADO un `subtitulo` de 201 caracteres rodeado de espacios
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422

#### Scenario: SEC-44 El PUT también recorta y normaliza subtitulo
- DADO una sección con `subtitulo = "Para comenzar"`
- CUANDO un cliente le hace PUT con `subtitulo = "   "`
- ENTONCES 200 y el `subtitulo` queda en `null`

### Requirement: Unicidad del nombre de la sección
El `nombre` de una sección DEBE ser único entre TODAS las secciones, sin distinguir mayúsculas de minúsculas (case-insensitive) pero distinguiendo tildes ("Entradas" ≠ "Entrádas"), comparando el valor ya recortado. La unicidad DEBE garantizarse mediante una restricción UNIQUE sobre `nombre_normalizado`. Un `nombre` duplicado DEBE devolver 409, tanto en el alta como en la modificación. Modificar una sección conservando su propio `nombre` NO DEBE considerarse un duplicado.

#### Scenario: SEC-11 nombre duplicado en el alta
- DADO una sección llamada "Entradas"
- CUANDO un cliente crea otra sección llamada "Entradas"
- ENTONCES 409 y no se crea ninguna sección

#### Scenario: SEC-12 nombre duplicado sin distinguir mayúsculas
- DADO una sección llamada "Entradas"
- CUANDO un cliente crea otra sección llamada "entradas"
- ENTONCES 409

#### Scenario: SEC-13 nombre duplicado con espacios sobrantes
- DADO una sección llamada "Entradas"
- CUANDO un cliente crea otra sección llamada "  Entradas "
- ENTONCES 409

#### Scenario: SEC-14 Las tildes distinguen nombres
- DADO una sección llamada "Entradas"
- CUANDO un cliente crea otra sección llamada "Entrádas"
- ENTONCES 201

#### Scenario: SEC-15 nombre duplicado en la modificación
- DADO las secciones "Entradas" y "Postres"
- CUANDO un cliente hace PUT de "Postres" con `nombre = "entradas"`
- ENTONCES 409 y "Postres" no cambia

#### Scenario: SEC-16 La modificación conserva el propio nombre
- DADO una sección "Entradas"
- CUANDO un cliente le hace PUT con `nombre = "Entradas"` y un nuevo `subtitulo`
- ENTONCES 200 y el `subtitulo` se actualiza

#### Scenario: SEC-17 La modificación puede cambiar solo mayúsculas del propio nombre
- DADO una sección "Entradas"
- CUANDO un cliente le hace PUT con `nombre = "ENTRADAS"`
- ENTONCES 200 y el `nombre` devuelto es "ENTRADAS"

#### Scenario: SEC-18 Reutilización del nombre tras el borrado
- DADO una sección "Entradas" que fue borrada
- CUANDO un cliente crea una sección llamada "Entradas"
- ENTONCES 201

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
`GET /secciones/{id}` DEBE devolver 200 con la sección, incluido `productos_ids`, y 404 si el id no existe.

#### Scenario: SEC-22 Obtener una sección existente
- DADO una sección con id 3
- CUANDO un cliente llama a `GET /secciones/3`
- ENTONCES 200 con `id`, `nombre`, `subtitulo` y `productos_ids` de la sección

#### Scenario: SEC-23 Obtener una sección inexistente
- DADO que no existe ninguna sección con id 999
- CUANDO un cliente llama a `GET /secciones/999`
- ENTONCES 404

#### Scenario: SEC-24 Listado de secciones ordenado por posición
- DADO las secciones "Postres" con `posicion = 2` y "Entradas" con `posicion = 1`
- CUANDO un cliente llama a `GET /secciones`
- ENTONCES 200 con ambas secciones ordenadas por `posicion` ascendente, cada una con `id`, `nombre`, `subtitulo`, `posicion` y `productos_ids`

#### Scenario: SEC-24b Listado vacío
- DADO que no existe ninguna sección
- CUANDO un cliente llama a `GET /secciones`
- ENTONCES 200 con `[]`

#### Scenario: SEC-24c El listado incluye productos_ids por sección
- DADO una sección con un Plato activo asignado
- CUANDO un cliente llama a `GET /secciones`
- ENTONCES la sección del listado devuelve `productos_ids` con el id del Plato

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

### Requirement: Borrado físico de sección
`DELETE /secciones/{id}` DEBE eliminar físicamente la fila de la sección, devolver 204 sin cuerpo y devolver 404 si el id no existe. Una vez borrada, `GET /secciones/{id}` DEBE devolver 404. El borrado NO DEBE ser idempotente: repetir el DELETE sobre un id ya borrado DEBE devolver 404.

#### Scenario: SEC-31 Borrar una sección
- DADO una sección con id 3
- CUANDO un cliente llama a `DELETE /secciones/3`
- ENTONCES 204 sin cuerpo y `GET /secciones/3` devuelve 404

#### Scenario: SEC-32 Borrar una sección inexistente
- DADO que no existe ninguna sección con id 999
- CUANDO un cliente llama a `DELETE /secciones/999`
- ENTONCES 404

#### Scenario: SEC-33 Borrado repetido
- DADO una sección que ya fue borrada
- CUANDO un cliente llama a `DELETE` nuevamente sobre su id
- ENTONCES 404

### Requirement: Desvinculación de productos al borrar la sección
Al borrar una sección, todos los productos que la referenciaban DEBEN conservarse y quedar con `seccion_id = null`. La desvinculación DEBE realizarla la base de datos mediante `ON DELETE SET NULL` sobre la clave foránea `producto.seccion_id`, con las claves foráneas activadas en SQLite. El borrado NO DEBE eliminar ni modificar ningún otro campo de los productos, incluidos los combos vencidos y los productos dados de baja.

#### Scenario: SEC-34 Los productos se conservan sin sección
- DADO una sección con un Plato y una Bebida asignados
- CUANDO un cliente borra la sección
- ENTONCES el Plato y la Bebida siguen existiendo y `GET /productos/platos/{id}` y `GET /productos/bebidas/{id}` devuelven `seccion_id = null`

#### Scenario: SEC-35 Solo se desvinculan los productos de la sección borrada
- DADO las secciones A y B, un Plato en A y un Postre en B
- CUANDO un cliente borra la sección A
- ENTONCES el Plato queda con `seccion_id = null` y el Postre conserva `seccion_id` de B

#### Scenario: SEC-36 Se desvinculan los cinco subtipos
- DADO una sección con un Plato, una Bebida, un Postre, un MenuEjecutivo y un ComboPromocion asignados
- CUANDO un cliente borra la sección
- ENTONCES los cinco productos siguen existiendo con `seccion_id = null`

#### Scenario: SEC-37 Un combo vencido también se desvincula
- DADO un combo con `fecha_hasta` de ayer asignado a una sección
- CUANDO un cliente borra la sección
- ENTONCES el combo sigue existiendo, con `seccion_id = null` y sin otros cambios

#### Scenario: SEC-38 Un producto dado de baja también se desvincula
- DADO un Postre dado de baja asignado a una sección
- CUANDO un cliente borra la sección
- ENTONCES el Postre sigue existiendo, dado de baja, con `seccion_id = null`
### Requirement: Validación de la posición de la sección
`posicion` es obligatoria en `POST /secciones` y en `PUT /secciones/{id}` (reemplazo completo). DEBE ser un número entero mayor o igual a 1. Una `posicion` ausente DEBE devolver 422; una `posicion` igual a cero o negativa DEBE devolver 422; una `posicion` que no sea un entero (por ejemplo, un decimal con parte fraccionaria o un texto no numérico) DEBE devolver 422. Se acepta el modo laxo, igual que `cant_personas`: un texto numérico entero (`"3"`) o un decimal sin parte fraccionaria (`3.0`) DEBE interpretarse como el entero `3`. Una solicitud rechazada por validación NO DEBE crear ni modificar ninguna sección.

#### Scenario: POS-02 posicion ausente en el alta
- DADO un cuerpo con `nombre = "Entradas"` y sin el campo `posicion`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422 y no se crea ninguna sección

#### Scenario: POS-03 posicion ausente en la modificación
- DADO una sección "Entradas" con `posicion = 1`
- CUANDO un cliente le hace PUT con `nombre = "Entradas"` y sin el campo `posicion`
- ENTONCES 422

#### Scenario: POS-04 posicion igual a cero en el alta
- DADO un cuerpo con `posicion = 0`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422 y no se crea ninguna sección

#### Scenario: POS-05 posicion negativa en el alta
- DADO un cuerpo con `posicion = -1`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422 y no se crea ninguna sección

#### Scenario: POS-06 posicion igual a cero en la modificación
- DADO una sección "Entradas" con `posicion = 1`
- CUANDO un cliente le hace PUT con `posicion = 0`
- ENTONCES 422

#### Scenario: POS-07 posicion con texto no numérico
- DADO un cuerpo con `posicion = "abc"`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422 y no se crea ninguna sección

#### Scenario: POS-08 posicion decimal
- DADO un cuerpo con `posicion = 1.5`
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 422 y no se crea ninguna sección

#### Scenario: POS-09 posicion en el límite inferior
- DADO un cuerpo con `posicion = 1` y ninguna otra sección con esa posición
- CUANDO un cliente llama a `POST /secciones`
- ENTONCES 201 y la `posicion` devuelta es 1

#### Scenario: POS-10 Una modificación rechazada por validación no cambia la sección
- DADO una sección "Entradas" con `posicion = 1` y `subtitulo = "Para comenzar"`
- CUANDO un cliente le hace PUT con `nombre = "Aperitivos"`, `subtitulo = "Para compartir"` y `posicion = -3`
- ENTONCES 422 y la sección conserva `nombre = "Entradas"`, `subtitulo = "Para comenzar"` y `posicion = 1`

#### Scenario: POS-29 posicion como texto numérico o decimal sin parte fraccionaria
- DADO un cuerpo con `posicion = "3"` (texto numérico) y otro cuerpo con `posicion = 3.0` (decimal sin parte fraccionaria), enviados en solicitudes separadas y sin otra sección en la posición 3
- CUANDO un cliente llama a `POST /secciones` con cada cuerpo (liberando la posición 3 entre ambas solicitudes)
- ENTONCES cada solicitud devuelve 201 y la `posicion` devuelta es el entero 3

### Requirement: Unicidad de la posición de la sección
La `posicion` de una sección DEBE ser única entre TODAS las secciones. La unicidad DEBE garantizarse mediante el índice único `ux_seccion_posicion`. Una `posicion` repetida DEBE devolver 409, tanto en el alta como en la modificación, con un cuerpo `{"detail": ...}` igual en forma al 409 por `nombre` duplicado. Ante una colisión NO DEBE desplazarse ni renumerarse ninguna otra sección, y una solicitud rechazada NO DEBE crear ni modificar ninguna sección. Modificar una sección conservando su propia `posicion` NO DEBE considerarse una colisión. Mover una sección a una posición libre DEBE ser válido.

#### Scenario: POS-11 posicion duplicada en el alta
- DADO una sección "Entradas" con `posicion = 1`
- CUANDO un cliente crea la sección "Postres" con `posicion = 1`
- ENTONCES 409 y no se crea ninguna sección

#### Scenario: POS-12 El 409 por posicion usa el cuerpo estándar
- DADO una sección "Entradas" con `posicion = 1`
- CUANDO un cliente crea la sección "Postres" con `posicion = 1`
- ENTONCES el cuerpo de la respuesta es un objeto con la clave `detail`

#### Scenario: POS-13 posicion duplicada en la modificación
- DADO las secciones "Entradas" con `posicion = 1` y "Postres" con `posicion = 2`
- CUANDO un cliente hace PUT de "Postres" con `nombre = "Postres"` y `posicion = 1`
- ENTONCES 409 y ambas secciones conservan su `nombre` y su `posicion`

#### Scenario: POS-14 La modificación conserva la propia posicion
- DADO una sección "Entradas" con `posicion = 3`
- CUANDO un cliente le hace PUT con `nombre = "Entradas"`, un nuevo `subtitulo` y `posicion = 3`
- ENTONCES 200, el `subtitulo` se actualiza y la `posicion` sigue siendo 3

#### Scenario: POS-15 Mover una sección a una posición libre
- DADO una sección "Entradas" con `posicion = 1` y ninguna sección con `posicion = 5`
- CUANDO un cliente le hace PUT con `nombre = "Entradas"` y `posicion = 5`
- ENTONCES 200 y la `posicion` devuelta es 5

#### Scenario: POS-16 Una colisión no desplaza a otras secciones
- DADO las secciones "Entradas" con `posicion = 1`, "Postres" con `posicion = 2` y "Bebidas" con `posicion = 3`
- CUANDO un cliente crea la sección "Sopas" con `posicion = 2`
- ENTONCES 409 y "Entradas", "Postres" y "Bebidas" conservan las posiciones 1, 2 y 3

### Requirement: Liberación y reutilización de posiciones
Se PERMITEN huecos en las posiciones. Borrar una sección DEBE liberar su `posicion` para que pueda ser reutilizada, y NO DEBE modificar la `posicion` de ninguna otra sección (no hay renumeración). Una posición libre, con o sin secciones en posiciones menores, DEBE aceptarse siempre que sea un entero mayor o igual a 1.

#### Scenario: POS-17 Reutilización de la posicion tras el borrado
- DADO una sección "Entradas" con `posicion = 1` que fue borrada
- CUANDO un cliente crea la sección "Postres" con `posicion = 1`
- ENTONCES 201 y la `posicion` devuelta es 1

#### Scenario: POS-18 El borrado no renumera las demás secciones
- DADO las secciones "Entradas" con `posicion = 1`, "Postres" con `posicion = 2` y "Bebidas" con `posicion = 3`
- CUANDO un cliente borra "Postres"
- ENTONCES "Entradas" conserva `posicion = 1` y "Bebidas" conserva `posicion = 3`

#### Scenario: POS-19 Se permiten huecos en las posiciones
- DADO que no existe ninguna sección
- CUANDO un cliente crea una sección con `posicion = 10`
- ENTONCES 201 y la `posicion` devuelta es 10

### Requirement: Intercambio de posiciones mediante modificaciones sucesivas
El sistema NO DEBE ofrecer una operación de intercambio atómico. Intercambiar las posiciones de dos secciones DEBE lograrse con tres `PUT`, pasando una de las secciones por una posición temporal libre; cada `PUT` DEBE ser exitoso cuando la posición de destino está libre. Un `PUT` que lleve una sección directamente a la posición ocupada por otra DEBE devolver 409 sin modificar ninguna sección.

#### Scenario: POS-20 Intercambio de dos secciones en tres PUT
- DADO las secciones A con `posicion = 1` y B con `posicion = 2`, y ninguna sección con `posicion = 99`
- CUANDO un cliente hace PUT de A con `posicion = 99`, luego PUT de B con `posicion = 1` y luego PUT de A con `posicion = 2`
- ENTONCES las tres solicitudes devuelven 200 y al final A tiene `posicion = 2` y B tiene `posicion = 1`

#### Scenario: POS-21 El intercambio directo es rechazado
- DADO las secciones A con `posicion = 1` y B con `posicion = 2`
- CUANDO un cliente hace PUT de A con `posicion = 2`
- ENTONCES 409 y A conserva `posicion = 1` y B conserva `posicion = 2`

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
