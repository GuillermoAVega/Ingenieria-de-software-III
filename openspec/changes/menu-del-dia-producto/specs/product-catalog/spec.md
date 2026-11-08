# Especificación Delta del Catálogo de Productos: subtipo MenuDelDia

Especificación delta para el cambio `menu-del-dia-producto`, aplicada sobre `product-catalog`. Códigos de estado: 422 = validación de esquema/campos, 404 = id inexistente, 409 = conflicto de regla de negocio.

**Alcance**: se agrega el sexto subtipo `MenuDelDia`, distinto de `MenuEjecutivo` y coexistente con él, con su ABM y listado en `/productos/menus-del-dia`. Este delta reemplaza en la especificación principal: "Los subtipos DEBEN ser Plato, Bebida, Postre, MenuEjecutivo, ComboPromocion" por "Plato, Bebida, Postre, MenuEjecutivo, ComboPromocion y MenuDelDia"; las referencias a "los cinco subtipos" pasan a ser seis, salvo en los requisitos de composición (`MenuEjecutivo`, `ComboPromocion`), cuyos componentes siguen siendo Plato, Bebida y Postre. El resto de los requisitos genéricos (campos comunes, `seccion_id`, prioridades de error, PUT como reemplazo completo) aplica a `MenuDelDia` sin cambios. Siguen FUERA DE ALCANCE: campos propios del `MenuDelDia`, `GET /productos` polimórfico y `?incluir_bajas`.

## MODIFIED Requirements

### Requirement: Jerarquía abstracta Producto
`Producto` DEBE ser abstracto con herencia de tablas unidas y discriminador `tipo`. Los subtipos DEBEN ser Plato, Bebida, Postre, MenuEjecutivo, ComboPromocion y MenuDelDia (`tipo = "menu_del_dia"`, tabla `menu_del_dia`). `POST /productos` sigue devolviendo 405 y `Producto` no puede instanciarse directamente. Toda relación entre modelos DEBE ser bidireccional y todos los mappers DEBEN configurarse sin errores.

#### Scenario: MDD-30 El registro de tipos contiene seis subtipos
- DADO el registro de modelos por tipo de producto
- CUANDO se consulta
- ENTONCES contiene seis tipos, incluido `menu_del_dia`, y los mappers se configuran sin errores

#### Scenario: MDD-31 MenuDelDia y MenuEjecutivo son tipos distintos
- DADO un `MenuDelDia` y un `MenuEjecutivo` existentes
- CUANDO se consultan por sus rutas
- ENTONCES cada uno responde únicamente en su ruta (`/productos/menus-del-dia/{id}` y `/productos/menus-ejecutivos/{id}`) con su `tipo` propio, y la ruta del otro devuelve 404

### Requirement: Asignación de producto a una sección
Los seis subtipos (Plato, Bebida, Postre, MenuEjecutivo, ComboPromocion y MenuDelDia) DEBEN aceptar y exponer `seccion_id` con las mismas reglas que los cinco originales (422 si la sección no existe, PUT como reemplazo completo).

#### Scenario: MDD-43 El MenuDelDia acepta y rechaza seccion_id en el PUT
- DADO un `MenuDelDia` y una sección existente
- CUANDO un cliente hace PUT con esa sección y luego con `seccion_id = 999`
- ENTONCES el primer PUT devuelve 200 con esa sección y el segundo devuelve 422

## ADDED Requirements

### Requirement: Rutas ABM del subtipo MenuDelDia
La API DEBE exponer `/productos/menus-del-dia` con alta (`POST`, 201), listado (`GET /productos/menus-del-dia`, solo activos, `id` ascendente), obtención por id (`GET /productos/menus-del-dia/{id}`, 200 aunque esté dado de baja con `dado_de_baja` visible; 404 si el id no existe o es de otro subtipo), modificación (`PUT`, reemplazo completo) y baja lógica (`DELETE`, véase product-logical-delete). El `MenuDelDia` DEBE aceptar solo los campos comunes (`nombre`, `precio`, `descripcion`, `imagen`, `seccion_id`) y, en el PUT, `dado_de_baja`. La respuesta DEBE exponer los campos comunes y `tipo = "menu_del_dia"`. Las reglas de validación, unicidad de `nombre` entre productos activos, prioridad de errores y reactivación son las genéricas de producto.

#### Scenario: MDD-32 Crear un MenuDelDia
- DADO un cuerpo con los campos comunes válidos
- CUANDO un cliente llama a `POST /productos/menus-del-dia`
- ENTONCES 201 y se devuelve el menú del día con un `id` y `tipo = "menu_del_dia"`

#### Scenario: MDD-33 Crear con seccion_id
- DADO una sección existente
- CUANDO un cliente llama a `POST /productos/menus-del-dia` con `seccion_id` de esa sección
- ENTONCES 201 y la respuesta incluye ese `seccion_id`

#### Scenario: MDD-34 Validación de campos comunes
- DADO un cuerpo con `nombre = ""`, o `precio = 0`, o `descripcion` de 501 caracteres, o `seccion_id` inexistente
- CUANDO un cliente llama a `POST /productos/menus-del-dia`
- ENTONCES 422 y no se crea ningún producto

#### Scenario: MDD-35 Nombre activo duplicado
- DADO un producto activo llamado "Milanesa" (de cualquier subtipo)
- CUANDO un cliente crea un `MenuDelDia` llamado "milanesa"
- ENTONCES 409

#### Scenario: MDD-36 Listar solo activos
- DADO dos `MenuDelDia` activos y uno dado de baja
- CUANDO un cliente llama a `GET /productos/menus-del-dia`
- ENTONCES 200 con los dos activos ordenados por id ascendente, sin el dado de baja

#### Scenario: MDD-37 Listado vacío y sin mezcla de subtipos
- DADO que existen platos y menús ejecutivos pero ningún `MenuDelDia`
- CUANDO un cliente llama a `GET /productos/menus-del-dia`
- ENTONCES 200 con `[]`

#### Scenario: MDD-38 Obtener por id un MenuDelDia dado de baja
- DADO un `MenuDelDia` dado de baja
- CUANDO un cliente llama a `GET /productos/menus-del-dia/{id}`
- ENTONCES 200 con `dado_de_baja = true`

#### Scenario: MDD-39 Id de otro subtipo o inexistente
- DADO un Plato con id 3 y ningún `MenuDelDia` con id 999
- CUANDO un cliente llama a `GET /productos/menus-del-dia/3` y a `GET /productos/menus-del-dia/999`
- ENTONCES ambas respuestas son 404

#### Scenario: MDD-40 PUT como reemplazo completo
- DADO un `MenuDelDia` con `descripcion`, `imagen` y `seccion_id` definidos
- CUANDO un cliente le hace PUT con un cuerpo válido sin esos campos
- ENTONCES 200 y los tres campos quedan en `null`

#### Scenario: MDD-41 Prioridad 422 sobre 404 en el PUT
- DADO que no existe ningún `MenuDelDia` con id 999
- CUANDO un cliente hace PUT a `/productos/menus-del-dia/999` con `precio = 0`
- ENTONCES 422

#### Scenario: MDD-42 PUT sobre un id inexistente
- DADO que no existe ningún `MenuDelDia` con id 999
- CUANDO un cliente hace PUT a `/productos/menus-del-dia/999` con un cuerpo válido
- ENTONCES 404

### Requirement: Frontend del catálogo con MenuDelDia
La interfaz de productos (`features/products/`) DEBE permitir el ABM de `MenuDelDia` como un tipo más del catálogo (nueva pestaña o tipo seleccionable): listado de activos, alta, edición y baja con confirmación, consumiendo `/productos/menus-del-dia`. El formulario DEBE ofrecer solo los campos comunes (`nombre`, `precio`, `descripcion`, `imagen`, sección). La etiqueta del tipo `menu_del_dia` en `features/menus/format.ts` DEBE mostrarse en español y ser distinta de la de `menu_ejecutivo`. Un 409 por baja bloqueada (véase product-logical-delete) o por nombre duplicado DEBE mostrarse como mensaje de error en español sin cerrar la pantalla. La lógica DEBE residir en hooks de la feature con un único objeto de estado y llamadas mediante `apiFetch`.

#### Scenario: MDD-44 Alta de un MenuDelDia desde la interfaz de productos
- DADO la pantalla de productos
- CUANDO la persona usuaria selecciona el tipo menú del día, completa nombre y precio y envía
- ENTONCES se llama a `POST /productos/menus-del-dia` con los campos comunes y el nuevo menú aparece en el listado

#### Scenario: MDD-45 Listado de menús del día
- DADO `MenuDelDia` activos y uno dado de baja
- CUANDO se abre la pestaña o el tipo de menús del día
- ENTONCES se listan solo los activos

#### Scenario: MDD-46 Edición de un MenuDelDia
- DADO un `MenuDelDia` existente
- CUANDO la persona usuaria modifica su precio y guarda
- ENTONCES se llama a `PUT /productos/menus-del-dia/{id}` con el cuerpo completo y el listado refleja el cambio

#### Scenario: MDD-47 Baja bloqueada informada
- DADO un `MenuDelDia` con alguna fecha `>= hoy` y la persona usuaria confirma su baja
- CUANDO el backend responde 409
- ENTONCES se muestra un mensaje de error en español indicando que tiene fechas asignadas y el menú permanece en el listado

#### Scenario: MDD-48 Etiqueta del tipo menu_del_dia
- DADO un producto con `tipo = "menu_del_dia"`
- CUANDO la interfaz formatea su tipo
- ENTONCES muestra la etiqueta en español definida para `menu_del_dia`, distinta de la de `menu_ejecutivo`
