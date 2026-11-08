# Especificación de Gestión de Promociones

Especificación nueva para el cambio `promociones`. La entidad `Promocion` vive en `Backend/src/promociones/` (convención entity-per-folder) y se expone bajo `/promociones`. Convenciones de errores (alineadas con `Backend/src/productos_menu/router.py`): id inexistente de la propia promoción, 404; violación de reglas de validación del esquema o de negocio sobre los datos enviados (incluido un producto referenciado que no existe), 422; conflicto de estado (promoción en uso, producto referenciado dado de baja), 409.

## ADDED Requirements

### Requirement: Representación de la promoción
`Promocion` DEBE tener `id`, `nombre` (obligatorio), `fecha_desde`, `fecha_hasta`, `descuento` y `dado_de_baja` (booleano, por defecto `false`). Toda respuesta DEBE incluir `productos_ids`, la lista de ids de los productos asociados ordenada de forma ascendente. La relación con `Producto` es N:M y un producto PUEDE pertenecer a varias promociones a la vez, incluso vigentes y solapadas.

#### Scenario: PRO-01 Respuesta con productos_ids ordenados
- DADO los productos con ids 3, 1 y 2
- CUANDO un cliente crea una promoción con `productos_ids = [3, 1, 2]`
- ENTONCES la respuesta incluye `productos_ids = [1, 2, 3]`

#### Scenario: PRO-02 Producto en varias promociones
- DADO un producto asociado a una promoción vigente
- CUANDO un cliente crea otra promoción vigente con el mismo producto
- ENTONCES 201 y ambas promociones coexisten

### Requirement: Indicador de promoción en uso
Toda respuesta de promoción (alta, consulta por id, listado y modificación) DEBE incluir `en_uso`, un booleano que vale `true` cuando al menos un `detalle_factura`, activo o no, referencia la promoción. Es el mismo criterio que bloquea la modificación con 409. El frontend DEBE usar este indicador para no ofrecer la edición de una promoción en uso.

#### Scenario: PRO-75 Promoción sin uso
- DADO una promoción que ninguna línea de factura referencia
- CUANDO un cliente la consulta por id o en el listado
- ENTONCES `en_uso = false`

#### Scenario: PRO-76 Promoción en uso
- DADO una promoción referenciada por una línea de factura, incluso inactiva
- CUANDO un cliente la consulta por id o en el listado
- ENTONCES `en_uso = true`

### Requirement: Alta de promoción
`POST /promociones` DEBE crear la promoción y devolver 201 con el cuerpo completo. DEBE validar: `nombre` presente y no vacío tras recortar espacios; `0 < descuento <= 100` con como máximo 2 decimales; `fecha_desde <= fecha_hasta`; `fecha_hasta >= today` (no se permite crear una promoción ya vencida); `productos_ids` con al menos un elemento. Cada id de `productos_ids` DEBE existir (si no, 422 con error de campo `loc = ["body", "productos_ids"]`, `type = "producto_inexistente"` e incluyendo los ids inexistentes) y NO DEBE estar dado de baja (si lo está, 409). La validación y la escritura DEBEN ocurrir en una sola transacción: ante cualquier rechazo no se persiste nada.

#### Scenario: PRO-03 Alta válida
- DADO un producto activo
- CUANDO un cliente hace POST con `nombre`, `fecha_desde <= fecha_hasta >= today`, `descuento = 15.5` y `productos_ids = [id]`
- ENTONCES 201, `dado_de_baja = false` y los datos enviados se reflejan en la respuesta

#### Scenario: PRO-04 Nombre faltante o vacío
- CUANDO un cliente hace POST sin `nombre` o con `nombre = "  "`
- ENTONCES 422 y no se crea ninguna promoción

#### Scenario: PRO-05 Descuento fuera de rango
- CUANDO un cliente hace POST con `descuento = 0`, `descuento = -5` o `descuento = 100.01`
- ENTONCES 422 en cada caso

#### Scenario: PRO-06 Descuento en el límite superior
- CUANDO un cliente hace POST con `descuento = 100`
- ENTONCES 201

#### Scenario: PRO-07 Descuento con más de 2 decimales
- CUANDO un cliente hace POST con `descuento = 10.555`
- ENTONCES 422

#### Scenario: PRO-08 Rango de fechas invertido
- CUANDO un cliente hace POST con `fecha_desde` posterior a `fecha_hasta`
- ENTONCES 422

#### Scenario: PRO-09 Fechas iguales
- CUANDO un cliente hace POST con `fecha_desde = fecha_hasta = today`
- ENTONCES 201

#### Scenario: PRO-10 Alta con fecha_hasta vencida
- CUANDO un cliente hace POST con `fecha_hasta` anterior a hoy
- ENTONCES 422 y no se crea ninguna promoción

#### Scenario: PRO-11 Sin productos
- CUANDO un cliente hace POST con `productos_ids = []` o sin el campo
- ENTONCES 422

#### Scenario: PRO-12 Producto inexistente
- CUANDO un cliente hace POST con un id de producto que no existe
- ENTONCES 422 con error `type = "producto_inexistente"`, `loc = ["body", "productos_ids"]` e ids, y no se crea ninguna promoción

#### Scenario: PRO-13 Producto dado de baja
- DADO un producto dado de baja
- CUANDO un cliente hace POST con ese producto en `productos_ids`
- ENTONCES 409 y no se crea ninguna promoción

### Requirement: Combos promocionables
Un `ComboPromocion` es un producto más y PUEDE formar parte de una promoción como cualquier otro subtipo activo. Para que el formulario pueda ofrecerlos, `GET /productos/combos` DEBE devolver 200 con la lista de combos, ocultando los dados de baja por defecto, con el mismo formato de respuesta que `GET /productos/combos/{id}`.

#### Scenario: PRO-73 Combo en una promoción
- DADO un combo existente y activo
- CUANDO un cliente hace POST a `/promociones` con el id del combo en `productos_ids`
- ENTONCES 201 y `productos_ids` incluye el combo

#### Scenario: PRO-74 Listado de combos
- DADO un combo activo y un combo dado de baja
- CUANDO un cliente llama a `GET /productos/combos`
- ENTONCES 200 con una lista que contiene solo el combo activo

### Requirement: Consulta de promociones
`GET /promociones/{id}` DEBE devolver 200 con la promoción, incluida una dada de baja (con `dado_de_baja = true` visible), o 404 si no existe. `GET /promociones` DEBE devolver 200 con la lista de promociones ocultando las dadas de baja por defecto; el parámetro de consulta `incluir_bajas=true` DEBE incluirlas.

#### Scenario: PRO-14 Obtener por id
- DADO una promoción existente
- CUANDO un cliente llama a `GET /promociones/{id}`
- ENTONCES 200 con sus datos y `productos_ids`

#### Scenario: PRO-15 Id desconocido
- CUANDO un cliente llama a `GET /promociones/999` y no existe
- ENTONCES 404

#### Scenario: PRO-16 Obtener una promoción dada de baja
- DADO una promoción dada de baja
- CUANDO un cliente llama a `GET /promociones/{id}`
- ENTONCES 200 con `dado_de_baja = true`

#### Scenario: PRO-17 Listado oculta bajas por defecto
- DADO una promoción activa y otra dada de baja
- CUANDO un cliente llama a `GET /promociones`
- ENTONCES 200 y solo aparece la activa

#### Scenario: PRO-18 Listado con bajas
- DADO una promoción activa y otra dada de baja
- CUANDO un cliente llama a `GET /promociones?incluir_bajas=true`
- ENTONCES 200 y aparecen ambas

### Requirement: Modificación de promoción
`PUT /promociones/{id}` DEBE aplicar las mismas validaciones de campos que el alta sobre el cuerpo completo y devolver 200 con la promoción actualizada, incluidos `productos_ids` reemplazados. Una promoción "en uso" (su id referenciado por al menos un `detalle_factura` en `promocion_id`, esté la línea activa o inactiva) NO DEBE poder modificarse: DEBE devolver 409 y no cambiar nada. Un id inexistente DEBE devolver 404. Los productos nuevos en `productos_ids` DEBEN existir (si no, 422 `producto_inexistente`) y no estar dados de baja (si lo están, 409); los productos que ya pertenecían a la promoción y se conservan no se revalidan contra la baja. En el PUT se aplica la regla de `fecha_hasta` vencida solo si `fecha_hasta` cambia respecto del valor guardado.

#### Scenario: PRO-19 Modificación válida
- DADO una promoción que ningún detalle de factura referencia
- CUANDO un cliente hace PUT con nuevo `nombre`, `descuento` y `productos_ids`
- ENTONCES 200 y la respuesta refleja los nuevos datos con `productos_ids` ordenados

#### Scenario: PRO-20 Modificación de promoción en uso
- DADO una promoción referenciada por al menos un `detalle_factura`
- CUANDO un cliente hace PUT con un cuerpo válido
- ENTONCES 409 y la promoción no cambia

#### Scenario: PRO-21 Modificación inválida
- DADO una promoción sin uso
- CUANDO un cliente hace PUT con `descuento = 0`
- ENTONCES 422 y la promoción no cambia

#### Scenario: PRO-22 Modificación de id desconocido
- CUANDO un cliente hace PUT a `/promociones/999` y no existe
- ENTONCES 404

#### Scenario: PRO-23 Producto nuevo dado de baja en la modificación
- DADO una promoción sin uso y un producto dado de baja
- CUANDO un cliente hace PUT agregando ese producto a `productos_ids`
- ENTONCES 409 y la promoción no cambia

#### Scenario: PRO-69 Producto nuevo inexistente en la modificación
- DADO una promoción sin uso
- CUANDO un cliente hace PUT agregando un id de producto que no existe
- ENTONCES 422 con `type = "producto_inexistente"` y la promoción no cambia

#### Scenario: PRO-70 Promoción referenciada solo por una línea inactiva
- DADO una promoción referenciada únicamente por un `detalle_factura` con `activo = false`
- CUANDO un cliente hace PUT con un cuerpo válido
- ENTONCES 409 y la promoción no cambia

#### Scenario: PRO-71 Productos conservados no se revalidan
- DADO una promoción sin uso cuyo producto fue dado de baja después
- CUANDO un cliente hace PUT conservando ese producto y cambiando el `nombre`
- ENTONCES 200

### Requirement: Baja lógica de promoción
`DELETE /promociones/{id}` DEBE establecer `dado_de_baja = true` sin eliminar físicamente la fila y devolver 204 sin cuerpo; 404 si el id no existe. La baja DEBE estar permitida siempre, incluso si la promoción está referenciada por líneas de factura, las cuales conservan su `promocion_id` y sus precios. DELETE repetido DEBE ser idempotente (204). Una promoción dada de baja NO DEBE ser candidata en la detección automática de nuevas líneas.

#### Scenario: PRO-24 Baja de una promoción sin uso
- DADO una promoción activa
- CUANDO un cliente llama a `DELETE /promociones/{id}`
- ENTONCES 204 sin cuerpo y `GET /promociones/{id}` muestra `dado_de_baja = true`

#### Scenario: PRO-25 Baja de una promoción en uso
- DADO una promoción referenciada por una línea de factura
- CUANDO un cliente llama a `DELETE /promociones/{id}`
- ENTONCES 204 y la línea conserva `promocion_id` y `precio_final`

#### Scenario: PRO-26 DELETE repetido
- DADO una promoción ya dada de baja
- CUANDO un cliente llama a DELETE nuevamente
- ENTONCES 204 y el estado no cambia

#### Scenario: PRO-27 Baja de id desconocido
- CUANDO un cliente llama a `DELETE /promociones/999` y no existe
- ENTONCES 404

### Requirement: Integridad del rango de fechas en la base
La tabla de promociones DEBE imponer una restricción CHECK `fecha_desde <= fecha_hasta`, de modo que ninguna escritura pueda persistir un rango invertido.

#### Scenario: PRO-28 Escritura directa con rango invertido
- CUANDO se intenta persistir una `Promocion` con `fecha_desde > fecha_hasta` directamente en la base
- ENTONCES la base rechaza la escritura
