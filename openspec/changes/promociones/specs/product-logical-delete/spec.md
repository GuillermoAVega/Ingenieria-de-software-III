# Delta: Baja Lógica de Productos

Especificación delta para el cambio `promociones` sobre `openspec/specs/product-logical-delete/spec.md`.

## ADDED Requirements

### Requirement: Las promociones no bloquean la baja de un producto
Un Plato, Bebida o Postre que pertenezca a una o más `Promocion` (activas, vigentes, futuras, vencidas o dadas de baja) NO DEBE verse impedido de darse de baja, ni por DELETE ni por PUT con `dado_de_baja = true`. La restricción RESTRICT de componentes sigue limitada a MenuEjecutivo y ComboPromocion. Al darse de baja el producto, sus promociones conservan la asociación; la detección automática de líneas nuevas depende del producto de la línea de comanda, que ya no puede ser un producto dado de baja.

#### Scenario: PRO-65 Baja de un producto con promoción vigente
- DADO un Plato activo incluido en una promoción vigente y que no está en ningún compuesto
- CUANDO un cliente llama a `DELETE /productos/platos/{id}`
- ENTONCES 204 y la promoción conserva el producto en `productos_ids`

#### Scenario: PRO-66 Baja vía PUT de un producto con promoción
- DADO una Bebida activa incluida en una promoción
- CUANDO un cliente hace PUT con `dado_de_baja = true`
- ENTONCES 200 y la Bebida queda dada de baja

### Requirement: Productos dados de baja en líneas de comanda nuevas
Un producto dado de baja NO DEBE poder usarse en líneas de comanda nuevas (véase order-line-product-validation). La baja de un producto no modifica líneas de comanda ni de factura ya existentes.

#### Scenario: PRO-67 Producto dado de baja rechazado en comanda nueva
- DADO un Postre dado de baja mediante DELETE
- CUANDO un cliente crea una línea de comanda con ese producto
- ENTONCES 409

#### Scenario: PRO-68 Líneas existentes no cambian por la baja
- DADO una línea de comanda con un Plato activo
- CUANDO el Plato se da de baja
- ENTONCES la línea y las líneas de factura derivadas conservan `producto_id` y precios

## MODIFIED Requirements

### Requirement: RESTRICT en la baja de componentes
Un Plato, Bebida o Postre NO DEBE darse de baja (mediante DELETE o mediante PUT con `dado_de_baja = true`) mientras sea componente de un MenuEjecutivo activo o de un ComboPromocion activo y no vencido (`fecha_hasta >= today`, incluidos los combos futuros). Un combo vencido (`fecha_hasta < today`) que sigue activo NO DEBE bloquear la baja de sus componentes. La pertenencia a una `Promocion` NO DEBE bloquear la baja. La respuesta DEBE ser 409 e incluir los ids de todos los compuestos bloqueantes. La verificación y la escritura DEBEN ocurrir en una sola transacción.

(Los escenarios existentes de este requisito se mantienen sin cambios; la regla añadida está cubierta por PRO-65 y PRO-66.)
