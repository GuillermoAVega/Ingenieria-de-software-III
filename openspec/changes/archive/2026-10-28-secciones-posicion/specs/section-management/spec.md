# Especificación Delta de la Gestión de Secciones: posición

Especificación delta para el cambio `secciones-posicion`, aplicada sobre `section-management`. Códigos de estado: 422 = validación de esquema/campos, 404 = id inexistente, 409 = conflicto de regla de negocio.

**Alcance**: se agrega el atributo `posicion` a `Seccion`, que determina el orden de presentación. Quedan FUERA DE ALCANCE y NO DEBEN implementarse: listado ordenado de secciones, reordenamiento masivo, intercambio atómico de posiciones, migraciones y Frontend.

**Efecto sobre los escenarios existentes**: como `posicion` es obligatoria en `POST` y `PUT`, los cuerpos de los escenarios SEC-xx que crean o modifican secciones se interpretan con una `posicion` válida y no repetida, salvo que el escenario indique lo contrario. Sus resultados esperados no cambian.

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Entidad Seccion
Una `Seccion` DEBE tener `id`, `nombre` (obligatorio), `subtitulo` (opcional) y `posicion` (entero obligatorio, único entre todas las secciones). La relación entre `Seccion` y `Producto` DEBE ser bidireccional (`Seccion.productos` / `Producto.seccion`, con `back_populates`) y todos los mappers DEBEN configurarse sin errores. La respuesta de una sección DEBE exponer `id`, `nombre`, `subtitulo` y `posicion`, y NO DEBE exponer una lista de productos ni `dado_de_baja`.

#### Scenario: SEC-01 Los mappers se configuran con la nueva entidad
- DADO que los modelos de sección y de producto están importados
- CUANDO se configuran los mappers de SQLAlchemy
- ENTONCES no se lanza ningún error

#### Scenario: SEC-02 La respuesta no incluye productos ni estado de baja
- DADO una sección con productos asignados
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES la respuesta contiene `id`, `nombre` y `subtitulo`, y no contiene una lista de productos ni `dado_de_baja`

#### Scenario: POS-01 La respuesta de consulta incluye posicion
- DADO una sección con `posicion = 4`
- CUANDO un cliente llama a `GET /secciones/{id}`
- ENTONCES 200 y la respuesta contiene `posicion = 4` junto con `id`, `nombre` y `subtitulo`

### Requirement: Alta de sección
`POST /secciones` DEBE crear la sección y devolver 201 con la sección creada, incluido su `id` y su `posicion`. Cuando falle más de una regla a la vez, la prioridad de los errores DEBE ser: 422 (esquema/campos) → 409 por `nombre` duplicado → 409 por `posicion` duplicada. Si colisionan `nombre` y `posicion` a la vez, DEBE devolverse un único 409 correspondiente al `nombre`; esta prioridad es determinista. Una solicitud rechazada NO DEBE crear ninguna sección.

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

### Requirement: Modificación de sección
`PUT /secciones/{id}` DEBE ser un reemplazo completo: un `subtitulo` omitido DEBE interpretarse como `null` y `posicion` es obligatoria. DEBE devolver 200 con la sección modificada, incluida su `posicion`, y 404 si el id no existe. Cuando fallen varias reglas a la vez, la prioridad de los errores DEBE ser: 422 (esquema/campos) → 404 (id inexistente) → 409 por `nombre` duplicado → 409 por `posicion` duplicada. Si colisionan `nombre` y `posicion` a la vez, DEBE devolverse un único 409 correspondiente al `nombre`; esta prioridad es determinista. Una solicitud rechazada NO DEBE modificar ninguna sección.

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
