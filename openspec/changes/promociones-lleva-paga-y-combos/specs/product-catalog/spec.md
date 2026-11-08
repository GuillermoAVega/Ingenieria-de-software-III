# Delta de Catálogo de Productos (product-catalog)

Delta sobre `openspec/specs/product-catalog/spec.md`. Cambia la composición de `ComboPromocion`: las listas `platos_ids`, `bebidas_ids` y `postres_ids` pasan a `platos`, `bebidas` y `postres`, cada una una lista de `{id, cantidad}` con `cantidad` entero `>= 1` y sin máximo. Es un cambio incompatible de la API; no hay migración (las bases se recrean con `poblar_db`). Los códigos de error de los componentes no cambian: `ComponenteInvalido` 422, `ComponenteInactivo` 409. Los escenarios nuevos usan el prefijo `PLC-` (numeración continua con las demás capacidades, desde PLC-54).

## ADDED Requirements

### Requirement: Cantidad por componente de ComboPromocion
Cada elemento de `platos`, `bebidas` y `postres` DEBE ser un objeto `{id: int, cantidad: int}` con `cantidad >= 1`, sin máximo. Una `cantidad` menor que 1, no entera o ausente DEBE devolver 422. La cantidad se persiste en las tablas intermedias `combo_plato`, `combo_bebida` y `combo_postre` (columna `cantidad`, con CHECK `cantidad >= 1`). La respuesta de alta, consulta por id, modificación y listado DEBE devolver las mismas tres listas con la misma forma `{id, cantidad}`, ordenadas por `id` ascendente. La baja lógica de un componente que forma parte de un combo activo conserva el bloqueo vigente (`RESTRICT_POR_TIPO`/`buscar_bloqueantes`), sin cambios de comportamiento.

#### Scenario: PLC-54 Combo con cantidades
- DADO un Plato activo, una Bebida activa y `fecha_hasta >= today`
- CUANDO un cliente hace POST a `/productos/combos` con `platos = [{id: P, cantidad: 2}]` y `bebidas = [{id: B, cantidad: 3}]`
- ENTONCES 201 y la respuesta incluye `platos = [{id: P, cantidad: 2}]`, `bebidas = [{id: B, cantidad: 3}]` y `postres = []`

#### Scenario: PLC-55 Cantidad mínima
- CUANDO un cliente hace POST con un componente de `cantidad = 1`
- ENTONCES 201

#### Scenario: PLC-56 Cantidad inválida
- CUANDO un cliente hace POST con un componente de `cantidad = 0`, `cantidad = -1`, `cantidad = 1.5` o sin `cantidad`
- ENTONCES 422 en cada caso y no se crea el combo

#### Scenario: PLC-57 Cantidad sin máximo
- CUANDO un cliente hace POST con un componente de `cantidad = 1000`
- ENTONCES 201

#### Scenario: PLC-58 Cantidades en la consulta y el listado
- DADO un combo con cantidades
- CUANDO un cliente llama a `GET /productos/combos/{id}` o `GET /productos/combos`
- ENTONCES cada combo devuelve `platos`, `bebidas` y `postres` como `{id, cantidad}` y no devuelve `platos_ids`, `bebidas_ids` ni `postres_ids`

#### Scenario: PLC-59 Modificación de cantidades
- DADO un combo vigente con `platos = [{id: P, cantidad: 1}]`
- CUANDO un cliente hace PUT con `platos = [{id: P, cantidad: 4}]`
- ENTONCES 200 y la respuesta devuelve `cantidad = 4`

#### Scenario: PLC-60 La baja de un componente sigue bloqueada
- DADO un combo activo con un Plato como componente de `cantidad = 3`
- CUANDO un cliente intenta dar de baja ese Plato
- ENTONCES se aplica el bloqueo `RESTRICT_POR_TIPO` vigente (mismo código de error que antes del cambio)

#### Scenario: PLC-61 CHECK de cantidad en la base
- CUANDO se intenta persistir directamente en `combo_plato`, `combo_bebida` o `combo_postre` una fila con `cantidad < 1`
- ENTONCES la base rechaza la escritura

## MODIFIED Requirements

### Requirement: Campos específicos por subtipo
Plato DEBE requerir `cant_personas` (int >= 1). Postre DEBE aceptar solo los campos comunes. Bebida DEBE requerir `es_alcoholica` (bool). MenuEjecutivo DEBE requerir `plato_id` y `postre_id`. ComboPromocion DEBE requerir `fecha_desde`, `fecha_hasta` (con `fecha_desde <= fecha_hasta`) y tres listas de componentes: `platos`, `bebidas` y `postres`, cada una de objetos `{id, cantidad}` (véase "Cantidad por componente de ComboPromocion"). Además, todos los subtipos DEBEN aceptar el campo común opcional `seccion_id` (véase "Asignación de producto a una sección"); este campo NO se considera un campo específico de ningún subtipo ni vuelve obligatorio ningún campo adicional.

### Requirement: Composición de ComboPromocion
El cuerpo de un ComboPromocion DEBE contener tres listas de componentes: `platos`, `bebidas` y `postres`, cada una de elementos `{id, cantidad}` con `cantidad` entero `>= 1`. DEBE haber al menos un componente en total entre las tres listas (de lo contrario, 422) y NO DEBE haber ids duplicados dentro de una misma lista (de lo contrario, 422), aunque tengan cantidades distintas. Los ids referenciados DEBEN existir y ser del tipo correcto de su lista (de lo contrario, 422 `ComponenteInvalido`) y DEBEN estar activos (de lo contrario, 409 `ComponenteInactivo`). La creación DEBE requerir `fecha_hasta >= today` (de lo contrario, 422).

#### Scenario: Combo válido
- DADO componentes activos, cada uno con `cantidad >= 1`, y `fecha_hasta` igual o posterior a hoy
- CUANDO un cliente llama a `POST /productos/combos`
- ENTONCES 201

#### Scenario: Combo vacío
- DADO un cuerpo de combo con `platos`, `bebidas` y `postres` vacías
- CUANDO se crea
- ENTONCES 422

#### Scenario: Combo con un único componente en una sola lista
- DADO un combo con `platos` con un elemento `{id, cantidad}` válido y activo, y `bebidas` y `postres` vacías
- CUANDO se crea
- ENTONCES 201

#### Scenario: Ids de componentes duplicados
- DADO un combo cuya lista `platos` contiene dos elementos con el mismo `id` (con igual o distinta `cantidad`)
- CUANDO se crea
- ENTONCES 422

#### Scenario: Tipo incorrecto o id inexistente
- DADO una lista `bebidas` que contiene el id de un Plato, o un id inexistente
- CUANDO se crea el combo
- ENTONCES 422

#### Scenario: Componente inactivo
- DADO una Bebida dada de baja
- CUANDO se crea un combo que la incluye en `bebidas`
- ENTONCES 409

#### Scenario: Vencido en la creación
- DADO `fecha_hasta` anterior a hoy
- CUANDO se crea un combo
- ENTONCES 422

### Requirement: Rutas ABM por subtipo
Sin cambios de redacción del requisito canónico; solo cambia la forma de los componentes en el escenario CAT-S-20. El resto de sus escenarios permanece como en la especificación canónica.

#### Scenario: CAT-S-20 Prioridad de referencias inexistentes (422) sobre componente inactivo (409) en un combo
- DADO un combo vigente con una Bebida dada de baja en `bebidas` (`[{id, cantidad}]`) y un id inexistente en `platos`
- CUANDO un cliente hace PUT del combo con ambos ids
- ENTONCES 422

## REMOVED Requirements

Ninguno.
