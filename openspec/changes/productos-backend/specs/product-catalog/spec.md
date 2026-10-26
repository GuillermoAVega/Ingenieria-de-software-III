# Especificación del Catálogo de Productos

Especificación delta para el cambio `productos-backend`. Códigos de estado: 422 = validación de esquema/campos, 404 = id inexistente, 409 = conflicto de regla de negocio. Los ids de componentes referenciados en los cuerpos de menú/combo que no existen o son del tipo incorrecto devuelven **422**; los componentes que existen con el tipo correcto pero están inactivos devuelven **409**.

## ADDED Requirements

### Requirement: Jerarquía abstracta Producto
`Producto` DEBE ser abstracto con herencia de tablas unidas y discriminador `tipo`. Los subtipos DEBEN ser Plato, Bebida, Postre, MenuEjecutivo, ComboPromocion. NO DEBE existir ningún endpoint que cree un `Producto` genérico (`POST /productos` DEBE devolver 405 Method Not Allowed), y `Producto` NO DEBE poder instanciarse directamente. Toda relación entre modelos DEBE ser bidireccional (`back_populates`), y todos los mappers DEBEN configurarse sin errores.

#### Scenario: La creación genérica no es posible
- DADO que la API está en ejecución
- CUANDO un cliente envía `POST /productos`
- ENTONCES la respuesta es 405 Method Not Allowed y no se crea ningún producto

#### Scenario: Instanciación directa rechazada
- DADO el módulo de modelos
- CUANDO el código instancia `Producto` directamente
- ENTONCES se lanza un error

#### Scenario: Los mappers se configuran
- DADO que todos los modelos de producto están importados
- CUANDO se configuran los mappers de SQLAlchemy
- ENTONCES no se lanza ningún error (incluido `AmbiguousForeignKeysError`)

### Requirement: Endpoints de lectura polimórficos
`GET /productos` y `GET /productos/{id}` DEBEN ser de solo lectura y devolver productos de cualquier subtipo, incluido el discriminador `tipo`. `GET /productos` DEBE excluir por defecto los productos dados de baja e incluirlos cuando se use `?incluir_bajas=true`. `GET /productos/{id}` DEBE devolver el producto aunque esté dado de baja, con `dado_de_baja` visible, y 404 si el id no existe.

#### Scenario: Listado mixto
- DADO un Plato activo y una Bebida activa
- CUANDO un cliente llama a `GET /productos`
- ENTONCES 200 y ambos se devuelven con su `tipo`

#### Scenario: Obtener por id un producto dado de baja
- DADO un Plato dado de baja con id 7
- CUANDO un cliente llama a `GET /productos/7`
- ENTONCES 200 y el cuerpo tiene `dado_de_baja = true`

#### Scenario: Id desconocido
- DADO que no existe ningún producto con id 999
- CUANDO un cliente llama a `GET /productos/999`
- ENTONCES 404

### Requirement: Rutas CRUD por subtipo
La API DEBE exponer `/productos/platos`, `/productos/bebidas`, `/productos/postres`, `/productos/menus-ejecutivos`, `/productos/combos`, cada una con listado, obtención por id, creación (POST) y actualización (PUT). POST DEBE devolver 201. `GET /productos/<subtype>/{id}` DEBE devolver el producto aunque esté dado de baja y DEBE devolver 404 si el id no existe o pertenece a otro subtipo. `?incluir_bajas=true` DEBE aplicarse solo a los listados. El PUT DEBE ser un reemplazo completo: un campo opcional omitido DEBE interpretarse como `null`, salvo `dado_de_baja`, que, si se omite, DEBE conservar el estado actual del producto. Cuando fallen varias reglas a la vez, la prioridad de los errores DEBE ser: 422 (esquema/campos) → 404 (id inexistente) → combo vencido (409) → componentes (409) → `nombre` duplicado (409).

#### Scenario: Crear plato
- DADO un cuerpo de Plato válido
- CUANDO un cliente llama a `POST /productos/platos`
- ENTONCES 201 y se devuelve el Plato creado con un id

#### Scenario: Id de subtipo incorrecto
- DADO una Bebida con id 3
- CUANDO un cliente llama a `GET /productos/platos/3`
- ENTONCES 404

#### Scenario: El listado por subtipo excluye las bajas por defecto
- DADO un Postre activo y uno dado de baja
- CUANDO un cliente llama a `GET /productos/postres`
- ENTONCES solo se devuelve el Postre activo
- Y con `?incluir_bajas=true` se devuelven ambos

#### Scenario: incluir_bajas se ignora en la obtención por id
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

### Requirement: Validación de campos comunes
Todos los productos DEBEN cumplir: `nombre` obligatorio; se DEBE recortar (trim) de espacios iniciales y finales antes de validarlo, almacenarlo y comprobar su unicidad; tras el recorte DEBE tener de 1 a 100 caracteres (un `nombre` vacío o compuesto solo de espacios DEBE devolver 422) y DEBE ser único entre los productos activos sin distinguir mayúsculas de minúsculas (case-insensitive), pero distinguiendo tildes ("Milanesa" ≠ "Milanésa"); `precio` obligatorio, > 0, `Numeric(10,2)`; `descripcion` opcional, <= 500 caracteres; `imagen` string opcional. Las violaciones de las reglas de esquema DEBEN devolver 422; un `nombre` activo duplicado DEBE devolver 409. El `nombre` de un producto dado de baja NO DEBE impedir la reutilización de ese nombre.

#### Scenario: nombre vacío
- DADO un cuerpo con `nombre = ""`
- CUANDO un cliente llama a `POST /productos/platos`
- ENTONCES 422

#### Scenario: nombre compuesto solo de espacios
- DADO un cuerpo con `nombre = "   "`
- CUANDO un cliente llama a `POST /productos/platos`
- ENTONCES 422

#### Scenario: nombre se recorta antes de almacenarse
- DADO un cuerpo de Plato válido con `nombre = "  Milanesa "`
- CUANDO un cliente llama a `POST /productos/platos`
- ENTONCES 201 y el `nombre` devuelto es "Milanesa"

#### Scenario: nombre demasiado largo
- DADO un `nombre` de 101 caracteres
- CUANDO se crea cualquier producto
- ENTONCES 422

#### Scenario: precio no positivo
- DADO `precio = 0`
- CUANDO se crea cualquier producto
- ENTONCES 422

#### Scenario: descripcion demasiado larga
- DADO una `descripcion` de 501 caracteres
- CUANDO se crea cualquier producto
- ENTONCES 422

#### Scenario: nombre activo duplicado
- DADO un producto activo llamado "Milanesa"
- CUANDO un cliente crea otro producto llamado "Milanesa"
- ENTONCES 409

#### Scenario: nombre activo duplicado sin distinguir mayúsculas
- DADO un producto activo llamado "Milanesa"
- CUANDO un cliente crea otro producto llamado "milanesa"
- ENTONCES 409

#### Scenario: nombre activo duplicado con espacios sobrantes
- DADO un producto activo llamado "Milanesa"
- CUANDO un cliente crea otro producto llamado "  Milanesa "
- ENTONCES 409

#### Scenario: Las tildes distinguen nombres
- DADO un producto activo llamado "Milanesa"
- CUANDO un cliente crea otro producto llamado "Milanésa"
- ENTONCES 201

#### Scenario: Reutilización del nombre tras la baja
- DADO un producto dado de baja llamado "Milanesa"
- CUANDO un cliente crea un producto activo llamado "Milanesa"
- ENTONCES 201

#### Scenario: La actualización conserva el propio nombre
- DADO un Plato activo "Milanesa"
- CUANDO un cliente le hace PUT con el mismo nombre y una nueva descripcion
- ENTONCES 200

### Requirement: Campos específicos por subtipo
Plato DEBE requerir `cant_personas` (int >= 1). Postre DEBE aceptar solo los campos comunes. Bebida DEBE requerir `es_alcoholica` (bool). MenuEjecutivo DEBE requerir `plato_id` y `postre_id`. ComboPromocion DEBE requerir `fecha_desde`, `fecha_hasta` (con `fecha_desde <= fecha_hasta`) y tres listas de componentes: `platos_ids`, `bebidas_ids` y `postres_ids`.

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

### Requirement: Composición de MenuEjecutivo
Un MenuEjecutivo DEBE referenciar un Plato existente y activo mediante `plato_id` y un Postre existente y activo mediante `postre_id`. Un id inexistente o de tipo incorrecto DEBE devolver 422. Un componente existente pero inactivo DEBE devolver 409. La verificación de los componentes y la escritura DEBEN ocurrir en una sola transacción.

#### Scenario: Menú válido
- DADO un Plato activo y un Postre activo
- CUANDO un cliente crea un menú con sus ids
- ENTONCES 201

#### Scenario: plato_id es una Bebida
- DADO que el id 4 es una Bebida
- CUANDO se crea un menú con `plato_id = 4`
- ENTONCES 422

#### Scenario: postre_id inexistente
- DADO que no existe ningún Postre con id 999
- CUANDO se crea un menú con `postre_id = 999`
- ENTONCES 422

#### Scenario: Plato inactivo
- DADO un Plato dado de baja
- CUANDO se crea un menú que lo referencia
- ENTONCES 409

### Requirement: Composición de ComboPromocion
El cuerpo de un ComboPromocion DEBE contener tres listas de componentes: `platos_ids`, `bebidas_ids` y `postres_ids`. DEBE haber al menos un id en total entre las tres listas (de lo contrario, 422) y NO DEBE haber ids duplicados dentro de una misma lista (de lo contrario, 422). Los ids referenciados DEBEN existir y ser del tipo correcto de su lista (de lo contrario, 422) y DEBEN estar activos (de lo contrario, 409). La creación DEBE requerir `fecha_hasta >= today` (de lo contrario, 422).

#### Scenario: Combo válido
- DADO componentes activos y `fecha_hasta` igual o posterior a hoy
- CUANDO un cliente llama a `POST /productos/combos`
- ENTONCES 201

#### Scenario: Combo vacío
- DADO un cuerpo de combo con `platos_ids`, `bebidas_ids` y `postres_ids` vacías
- CUANDO se crea
- ENTONCES 422

#### Scenario: Combo con un único componente en una sola lista
- DADO un combo con `platos_ids` con un id válido y activo, y `bebidas_ids` y `postres_ids` vacías
- CUANDO se crea
- ENTONCES 201

#### Scenario: Ids de componentes duplicados
- DADO un combo cuya lista `platos_ids` contiene dos veces el mismo id
- CUANDO se crea
- ENTONCES 422

#### Scenario: Tipo incorrecto o id inexistente
- DADO una lista `bebidas_ids` que contiene un id de Plato, o un id inexistente
- CUANDO se crea el combo
- ENTONCES 422

#### Scenario: Componente inactivo
- DADO una Bebida dada de baja
- CUANDO se crea un combo que la incluye en `bebidas_ids`
- ENTONCES 409

#### Scenario: Vencido en la creación
- DADO `fecha_hasta` anterior a hoy
- CUANDO se crea un combo
- ENTONCES 422

### Requirement: Precios manuales de los compuestos
El `precio` de MenuEjecutivo y ComboPromocion DEBE ser proporcionado por el cliente e independiente de los precios de los componentes. Cambiar el precio de un componente NO DEBE cambiar el precio de ningún compuesto.

#### Scenario: Cambio de precio de un componente
- DADO un menú con `precio = 1000` que contiene un Plato con precio 800
- CUANDO el Plato se actualiza a `precio = 900`
- ENTONCES el menú sigue teniendo `precio = 1000`

### Requirement: Las actualizaciones de compuestos revalidan los componentes
El PUT sobre un MenuEjecutivo o ComboPromocion DEBE volver a ejecutar las validaciones de campos y las verificaciones de existencia y tipo de los ids de componentes (422), siempre, de forma atómica con la escritura. La verificación de que todos los componentes estén activos (409 si alguno está inactivo) DEBE ejecutarse únicamente si el compuesto queda activo tras la edición (es decir, si el `dado_de_baja` resultante es `false`); si el compuesto queda dado de baja, NO DEBE aplicarse.

#### Scenario: Actualizar un menú con un componente inactivo
- DADO un menú activo y un Postre dado de baja
- CUANDO se hace PUT del menú con ese `postre_id`
- ENTONCES 409 y el menú no cambia

#### Scenario: Editar un menú dado de baja cuyo componente está inactivo
- DADO un menú dado de baja cuyo Plato también está dado de baja
- CUANDO un cliente le hace PUT con una nueva `descripcion` válida manteniéndolo dado de baja (`dado_de_baja = true` o sin el campo)
- ENTONCES 200 y el menú sigue dado de baja

#### Scenario: Un id de componente inexistente se rechaza aunque el compuesto quede dado de baja
- DADO un menú dado de baja
- CUANDO un cliente le hace PUT con `postre_id = 999` inexistente manteniéndolo dado de baja
- ENTONCES 422

### Requirement: Los combos vencidos son inmutables
Cualquier PUT sobre un ComboPromocion cuya `fecha_hasta < today` (edición o reactivación) DEBE devolver 409 y no cambiar nada. Única excepción: un PUT que establece `dado_de_baja = true` sin modificar ningún otro campo sobre un combo vencido DEBE aceptarse (equivale al DELETE lógico, que está permitido y es idempotente). Si el combo vencido está activo, queda dado de baja; si ya está dado de baja, DEBE devolver 200 sin ningún cambio (idempotente, coherente con DELETE repetido → 204). Cualquier otro cambio sobre un combo vencido sigue devolviendo 409.

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

### Requirement: Infraestructura de pruebas
El Backend DEBE proveer pytest, un comando de pruebas definido y fixtures de `TestClient` que usen una base de datos SQLite aislada, con `get_db` y las variables de entorno requeridas (`DB_URL`, `ENV`) sobrescritas.

#### Scenario: La suite se ejecuta de forma aislada
- DADO que no hay variables de entorno externas
- CUANDO se ejecuta el comando de pruebas del Backend
- ENTONCES las pruebas se ejecutan contra una base de datos aislada sin tocar el archivo SQLite real
