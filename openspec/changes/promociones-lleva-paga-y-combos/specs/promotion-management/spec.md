# Delta de Gestión de Promociones (promotion-management)

Delta sobre la especificación `promotion-management` del cambio `promociones` (todavía no archivado; `promociones` DEBE archivarse antes que este cambio). Se mantienen los ids PRO-xx de los escenarios modificados. Los escenarios nuevos usan el prefijo `PLC-`. Convenciones de errores sin cambios: id propio inexistente, 404; violación de validación de esquema o de negocio, 422; conflicto de estado, 409; producto referenciado inexistente, 422 `producto_inexistente`; producto referenciado dado de baja, 409.

## ADDED Requirements

### Requirement: Tipo de promoción
`Promocion` DEBE tener `tipo`, con valores `porcentaje` o `lleva_paga`.
- `porcentaje` DEBE requerir `descuento` (`0 < descuento <= 100`, como máximo 2 decimales) y NO DEBE aceptar `lleva` ni `paga`.
- `lleva_paga` DEBE requerir `lleva` y `paga` enteros con `lleva > paga >= 1` y NO DEBE aceptar `descuento`.
- En el alta, `tipo` es obligatorio. Cualquier violación DEBE devolver 422 con errores de campo de estilo Pydantic y no persistir nada.
- Toda respuesta DEBE incluir `tipo`, `descuento` (`null` si es `lleva_paga`), `lleva` y `paga` (`null` si es `porcentaje`), además de `en_uso` y `productos_ids`.
- La tabla DEBE imponer CHECK por tipo, de modo que ninguna escritura directa persista una combinación inconsistente (por ejemplo `porcentaje` sin `descuento`, `lleva_paga` con `descuento`, o `lleva <= paga`).
- Una promoción `lleva_paga` actúa solo sobre unidades de un mismo producto (véase `invoice-line-pricing`).

#### Scenario: PLC-01 Alta válida lleva_paga
- DADO un producto activo
- CUANDO un cliente hace POST con `tipo = "lleva_paga"`, `lleva = 3`, `paga = 2`, fechas válidas y `productos_ids = [id]`
- ENTONCES 201, `tipo = "lleva_paga"`, `lleva = 3`, `paga = 2` y `descuento = null`

#### Scenario: PLC-02 Tipo faltante en el alta
- CUANDO un cliente hace POST sin `tipo`
- ENTONCES 422 y no se crea ninguna promoción

#### Scenario: PLC-03 Tipo desconocido
- CUANDO un cliente hace POST con `tipo = "otro"`
- ENTONCES 422

#### Scenario: PLC-04 porcentaje con lleva o paga
- CUANDO un cliente hace POST con `tipo = "porcentaje"`, `descuento = 10` y `lleva = 2` (o `paga = 1`)
- ENTONCES 422 y no se crea ninguna promoción

#### Scenario: PLC-05 porcentaje sin descuento
- CUANDO un cliente hace POST con `tipo = "porcentaje"` y sin `descuento`
- ENTONCES 422

#### Scenario: PLC-06 lleva_paga con descuento
- CUANDO un cliente hace POST con `tipo = "lleva_paga"`, `lleva = 2`, `paga = 1` y `descuento = 10`
- ENTONCES 422 y no se crea ninguna promoción

#### Scenario: PLC-07 lleva_paga con lleva no mayor que paga
- CUANDO un cliente hace POST con `tipo = "lleva_paga"` y `lleva = 2`, `paga = 2` (o `lleva = 2`, `paga = 3`)
- ENTONCES 422 en cada caso

#### Scenario: PLC-08 lleva_paga con paga menor que 1
- CUANDO un cliente hace POST con `tipo = "lleva_paga"`, `lleva = 2` y `paga = 0`
- ENTONCES 422

#### Scenario: PLC-09 lleva_paga sin lleva o sin paga
- CUANDO un cliente hace POST con `tipo = "lleva_paga"` y solo `lleva` (o solo `paga`)
- ENTONCES 422

#### Scenario: PLC-10 lleva y paga no enteros
- CUANDO un cliente hace POST con `tipo = "lleva_paga"`, `lleva = 2.5` y `paga = 1`
- ENTONCES 422

#### Scenario: PLC-11 Respuesta de una promoción porcentaje
- DADO una promoción `porcentaje` con `descuento = 15`
- CUANDO un cliente la consulta
- ENTONCES `tipo = "porcentaje"`, `descuento = 15.0`, `lleva = null` y `paga = null`

#### Scenario: PLC-12 Combo en lleva_paga
- DADO un combo activo
- CUANDO un cliente crea una promoción `lleva_paga` con el combo en `productos_ids`
- ENTONCES 201

### Requirement: Baja automática por vencimiento
Antes de listar promociones, consultar una por id y realizar cualquier cómputo de precios que involucre promociones, el servicio DEBE ejecutar una única sentencia `UPDATE` que establezca `dado_de_baja = true` en toda promoción con `fecha_hasta < hoy`, donde `hoy` proviene de `obtener_hoy`. No DEBE haber tareas programadas. La baja automática es la misma baja lógica de `DELETE` y NO DEBE eliminar filas ni alterar líneas de factura. Las promociones ya referenciadas por líneas de factura siguen siendo candidatas conservadas para las facturas que ya las referencian (véase `invoice-line-pricing`).

#### Scenario: PLC-13 El listado da de baja las vencidas
- DADO una promoción con `fecha_hasta` anterior a hoy y `dado_de_baja = false` en la base
- CUANDO un cliente llama a `GET /promociones`
- ENTONCES la promoción no aparece en el listado por defecto

#### Scenario: PLC-14 El listado con bajas muestra la vencida dada de baja
- DADO la misma promoción vencida
- CUANDO un cliente llama a `GET /promociones?incluir_bajas=true`
- ENTONCES aparece con `dado_de_baja = true`

#### Scenario: PLC-15 La consulta por id da de baja la vencida
- DADO una promoción con `fecha_hasta` anterior a hoy y `dado_de_baja = false` en la base
- CUANDO un cliente llama a `GET /promociones/{id}`
- ENTONCES 200 con `dado_de_baja = true`

#### Scenario: PLC-16 fecha_hasta igual a hoy no se da de baja
- DADO una promoción con `fecha_hasta` igual a hoy
- CUANDO un cliente la consulta
- ENTONCES `dado_de_baja = false`

#### Scenario: PLC-17 Sentencia única
- DADO varias promociones vencidas
- CUANDO se ejecuta la baja automática
- ENTONCES todas quedan con `dado_de_baja = true` mediante una única sentencia `UPDATE`

#### Scenario: PLC-18 La baja automática conserva las líneas
- DADO una promoción vencida referenciada por una línea de factura activa
- CUANDO un cliente consulta la promoción
- ENTONCES `dado_de_baja = true`, `en_uso = true` y la línea conserva `promocion_id` y `precio_final`

## MODIFIED Requirements

### Requirement: Representación de la promoción
`Promocion` DEBE tener `id`, `nombre` (obligatorio), `tipo` (`porcentaje` | `lleva_paga`), `fecha_desde`, `fecha_hasta`, `descuento` (solo `porcentaje`), `lleva` y `paga` (solo `lleva_paga`) y `dado_de_baja` (booleano, por defecto `false`). Toda respuesta DEBE incluir `tipo`, `descuento`, `lleva`, `paga` (los no aplicables en `null`), `en_uso` y `productos_ids`, la lista de ids de los productos asociados ordenada de forma ascendente. La relación con `Producto` es N:M y un producto PUEDE pertenecer a varias promociones a la vez, incluso vigentes y solapadas.

#### Scenario: PRO-01 Respuesta con productos_ids ordenados
- DADO los productos con ids 3, 1 y 2
- CUANDO un cliente crea una promoción de `tipo = "porcentaje"`, `descuento = 10` y `productos_ids = [3, 1, 2]`
- ENTONCES la respuesta incluye `productos_ids = [1, 2, 3]`, `tipo` y los campos `lleva` y `paga` en `null`

### Requirement: Alta de promoción
`POST /promociones` DEBE crear la promoción y devolver 201 con el cuerpo completo. DEBE validar: `nombre` presente y no vacío tras recortar espacios; `tipo` obligatorio; los campos exigidos y prohibidos del tipo (véase "Tipo de promoción"); en `porcentaje`, `0 < descuento <= 100` con como máximo 2 decimales; `fecha_desde <= fecha_hasta`; `fecha_hasta >= today` (no se permite crear una promoción ya vencida); `productos_ids` con al menos un elemento. Cada id de `productos_ids` DEBE existir (si no, 422 con error de campo `loc = ["body", "productos_ids"]`, `type = "producto_inexistente"` e incluyendo los ids inexistentes) y NO DEBE estar dado de baja (si lo está, 409). La validación y la escritura DEBEN ocurrir en una sola transacción: ante cualquier rechazo no se persiste nada.

#### Scenario: PRO-03 Alta válida
- DADO un producto activo
- CUANDO un cliente hace POST con `nombre`, `tipo = "porcentaje"`, `fecha_desde <= fecha_hasta >= today`, `descuento = 15.5` y `productos_ids = [id]`
- ENTONCES 201, `dado_de_baja = false` y los datos enviados se reflejan en la respuesta

#### Scenario: PRO-05 Descuento fuera de rango
- CUANDO un cliente hace POST con `tipo = "porcentaje"` y `descuento = 0`, `descuento = -5` o `descuento = 100.01`
- ENTONCES 422 en cada caso

#### Scenario: PRO-06 Descuento en el límite superior
- CUANDO un cliente hace POST con `tipo = "porcentaje"` y `descuento = 100`
- ENTONCES 201

#### Scenario: PRO-07 Descuento con más de 2 decimales
- CUANDO un cliente hace POST con `tipo = "porcentaje"` y `descuento = 10.555`
- ENTONCES 422

### Requirement: Combos promocionables
Un `ComboPromocion` es un producto más y PUEDE formar parte de una promoción (de cualquier tipo) como cualquier otro subtipo activo. Para que el formulario pueda ofrecerlos, `GET /productos/combos` DEBE devolver 200 con la lista de combos, ocultando los dados de baja por defecto, con el mismo formato de respuesta que `GET /productos/combos/{id}`: componentes como `platos`, `bebidas` y `postres`, cada uno una lista de `{id, cantidad}` (véase `product-catalog`).

#### Scenario: PRO-73 Combo en una promoción
- DADO un combo existente y activo
- CUANDO un cliente hace POST a `/promociones` con el id del combo en `productos_ids`
- ENTONCES 201 y `productos_ids` incluye el combo

#### Scenario: PRO-74 Listado de combos
- DADO un combo activo con `platos = [{id: 1, cantidad: 2}]` y un combo dado de baja
- CUANDO un cliente llama a `GET /productos/combos`
- ENTONCES 200 con una lista que contiene solo el combo activo y cada elemento expone `platos`, `bebidas` y `postres` como listas de `{id, cantidad}` (sin `platos_ids`, `bebidas_ids` ni `postres_ids`)

### Requirement: Consulta de promociones
`GET /promociones/{id}` DEBE devolver 200 con la promoción, incluida una dada de baja (con `dado_de_baja = true` visible), o 404 si no existe. `GET /promociones` DEBE devolver 200 con la lista de promociones ocultando las dadas de baja por defecto; el parámetro de consulta `incluir_bajas=true` DEBE incluirlas. Ambas consultas DEBEN ejecutar antes la baja automática por vencimiento (véase "Baja automática por vencimiento").

#### Scenario: PRO-14 Obtener por id
- DADO una promoción existente
- CUANDO un cliente llama a `GET /promociones/{id}`
- ENTONCES 200 con sus datos, `tipo` y `productos_ids`

#### Scenario: PRO-17 Listado oculta bajas por defecto
- DADO una promoción activa y otra dada de baja (manualmente o por vencimiento)
- CUANDO un cliente llama a `GET /promociones`
- ENTONCES 200 y solo aparece la activa

### Requirement: Modificación de promoción
`PUT /promociones/{id}` DEBE aplicar las mismas validaciones de campos que el alta (incluidas las reglas por `tipo`) sobre el cuerpo completo y devolver 200 con la promoción actualizada, incluidos `productos_ids` reemplazados. Una promoción "en uso" (su id referenciado por al menos un `detalle_factura` en `promocion_id`, esté la línea activa o inactiva) NO DEBE poder modificarse, incluido el cambio de `tipo`: DEBE devolver 409 y no cambiar nada. Una línea `lleva_paga` sin unidades gratis tiene `promocion_id = null` y por lo tanto no cuenta como aplicación. Un id inexistente DEBE devolver 404. Los productos nuevos en `productos_ids` DEBEN existir (si no, 422 `producto_inexistente`) y no estar dados de baja (si lo están, 409); los productos que ya pertenecían a la promoción y se conservan no se revalidan contra la baja. En el PUT se aplica la regla de `fecha_hasta` vencida solo si `fecha_hasta` cambia respecto del valor guardado.

#### Scenario: PRO-19 Modificación válida
- DADO una promoción que ningún detalle de factura referencia
- CUANDO un cliente hace PUT con nuevo `nombre`, `tipo`, los campos de ese tipo y `productos_ids`
- ENTONCES 200 y la respuesta refleja los nuevos datos con `productos_ids` ordenados

#### Scenario: PRO-21 Modificación inválida
- DADO una promoción sin uso
- CUANDO un cliente hace PUT con `tipo = "porcentaje"` y `descuento = 0`
- ENTONCES 422 y la promoción no cambia

#### Scenario: PLC-19 Cambio de tipo sin uso
- DADO una promoción `porcentaje` sin uso
- CUANDO un cliente hace PUT con `tipo = "lleva_paga"`, `lleva = 2` y `paga = 1`
- ENTONCES 200, `tipo = "lleva_paga"` y `descuento = null`

#### Scenario: PLC-20 Cambio de tipo en uso
- DADO una promoción referenciada por una línea de factura
- CUANDO un cliente hace PUT con otro `tipo` y datos válidos
- ENTONCES 409 y la promoción no cambia

#### Scenario: PLC-21 PUT lleva_paga inválido
- DADO una promoción sin uso
- CUANDO un cliente hace PUT con `tipo = "lleva_paga"`, `lleva = 2`, `paga = 2`
- ENTONCES 422 y la promoción no cambia

#### Scenario: PLC-22 lleva_paga sin unidades gratis no cuenta como aplicación
- DADO una promoción `lleva_paga` 3x2 y una única línea de 2 unidades del producto, con `promocion_id = null`
- CUANDO un cliente hace PUT válido sobre la promoción
- ENTONCES 200

### Requirement: Integridad del rango de fechas en la base
La tabla de promociones DEBE imponer una restricción CHECK `fecha_desde <= fecha_hasta`, de modo que ninguna escritura pueda persistir un rango invertido, y las restricciones CHECK por tipo definidas en "Tipo de promoción".

#### Scenario: PRO-28 Escritura directa con rango invertido
- CUANDO se intenta persistir una `Promocion` con `fecha_desde > fecha_hasta` directamente en la base
- ENTONCES la base rechaza la escritura

#### Scenario: PLC-23 Escritura directa con combinación de tipo inconsistente
- CUANDO se intenta persistir directamente en la base una `Promocion` `porcentaje` sin `descuento`, una `lleva_paga` con `descuento`, o una `lleva_paga` con `lleva <= paga` o `paga < 1`
- ENTONCES la base rechaza la escritura en cada caso

## REMOVED Requirements

Ninguno.
