# Especificación de la Gestión de Secciones

Especificación delta para el cambio `secciones-backend`. Códigos de estado: 422 = validación de esquema/campos, 404 = id inexistente, 409 = conflicto de regla de negocio.

**Alcance**: este cambio cubre únicamente el alta, la consulta por id, la modificación y el borrado físico de secciones. Quedan explícitamente FUERA DE ALCANCE y NO DEBEN implementarse: listados de secciones, listados de productos por sección, ordenamiento, baja lógica de secciones (`dado_de_baja`) y reactivación. La respuesta de una sección NO DEBE incluir la lista de sus productos.

## ADDED Requirements

### Requirement: Entidad Seccion
Una `Seccion` DEBE tener `id`, `nombre` (obligatorio) y `subtitulo` (opcional). La relación entre `Seccion` y `Producto` DEBE ser bidireccional (`Seccion.productos` / `Producto.seccion`, con `back_populates`) y todos los mappers DEBEN configurarse sin errores. La respuesta de una sección DEBE exponer `id`, `nombre` y `subtitulo`, y NO DEBE exponer una lista de productos ni `dado_de_baja`.

#### Scenario: SEC-01 Los mappers se configuran con la nueva entidad
- DADO que los modelos de sección y de producto están importados
- CUANDO se configuran los mappers de SQLAlchemy
- ENTONCES no se lanza ningún error

#### Scenario: SEC-02 La respuesta no incluye productos ni estado de baja
- DADO una sección con productos asignados
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES la respuesta contiene `id`, `nombre` y `subtitulo`, y no contiene una lista de productos ni `dado_de_baja`

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
`POST /secciones` DEBE crear la sección y devolver 201 con la sección creada, incluido su `id`. Cuando falle más de una regla a la vez, la prioridad de los errores DEBE ser: 422 (esquema/campos) → 409 (`nombre` duplicado).

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

### Requirement: Consulta de sección por id
`GET /secciones/{id}` DEBE devolver 200 con la sección y 404 si el id no existe. NO DEBE existir `GET /secciones` (listado).

#### Scenario: SEC-22 Obtener una sección existente
- DADO una sección con id 3
- CUANDO un cliente llama a `GET /secciones/3`
- ENTONCES 200 con `id`, `nombre` y `subtitulo` de la sección

#### Scenario: SEC-23 Obtener una sección inexistente
- DADO que no existe ninguna sección con id 999
- CUANDO un cliente llama a `GET /secciones/999`
- ENTONCES 404

#### Scenario: SEC-24 No existe el listado de secciones
- DADO que la API está en ejecución
- CUANDO un cliente llama a `GET /secciones`
- ENTONCES la respuesta es 405 Method Not Allowed

### Requirement: Modificación de sección
`PUT /secciones/{id}` DEBE ser un reemplazo completo: un `subtitulo` omitido DEBE interpretarse como `null`. DEBE devolver 200 con la sección modificada y 404 si el id no existe. Cuando fallen varias reglas a la vez, la prioridad de los errores DEBE ser: 422 (esquema/campos) → 404 (id inexistente) → 409 (`nombre` duplicado).

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
- ENTONCES el Plato conserva su `seccion_id`

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
