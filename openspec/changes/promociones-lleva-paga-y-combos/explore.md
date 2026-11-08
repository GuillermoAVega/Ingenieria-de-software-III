# Exploración: promociones-lleva-paga-y-combos

Cambio construido sobre `promociones`, que está implementado pero todavía no archivado.

## Decisiones confirmadas por el usuario (2026-11-07)

1. **Combo.** Se mantiene como hoy: varios componentes, fechas y precio cargado a mano. Se agrega `cantidad` (entero `>= 1`) en `combo_plato`, `combo_bebida` y `combo_postre`. La API pasa de `platos_ids` a `platos: [{id, cantidad}]` (y lo mismo para bebidas y postres). Se suma una interfaz de combos dentro de la sección de promociones del frontend, con cantidad por componente.
2. **`Promocion`.** Se agrega `tipo` (`porcentaje` | `lleva_paga`) en una sola tabla, con CHECK según el tipo:
   - `descuento` es obligatorio solo en `porcentaje`.
   - `lleva > paga >= 1` aplica solo en `lleva_paga`.
   - El formulario tiene un selector de tipo.
   - `lleva_paga` aplica solo sobre unidades del mismo producto.
3. **Cálculo agrupado por producto dentro de la factura.**
   - Se suman las unidades de todas las líneas activas del producto.
   - Se elige una sola promoción por producto: la de mayor ahorro total en pesos. Ante empate, la de menor id. No se acumulan promociones.
   - Las unidades bonificadas, `⌊total / lleva⌋ × (lleva − paga)`, se asignan a las líneas de menor `precio_unitario`. Ante empate, a la de menor id.
   - Las líneas sin descuento quedan con `promocion_id = null`.
   - Al dar de alta, modificar o dar de baja una línea se recalculan solo las líneas de ese producto y después `importe_total`.
   - Las promociones ya aplicadas a la factura se conservan como candidatas aunque se den de baja después.
   - La vigencia se evalúa a `factura.fecha_hora_emision.date()`.

4. **Baja automática por vencimiento (baja perezosa).** Antes de listar, consultar o calcular promociones, el servicio marca `dado_de_baja = true`, con una única sentencia `UPDATE`, en toda promoción con `fecha_hasta < hoy`. No hay tareas programadas. Las promociones ya aplicadas a una factura se siguen conservando como candidatas.
5. **Modificación.** Una promoción solo puede modificarse si nunca fue aplicada, es decir, si ninguna línea de factura activa o inactiva la referencia (regla vigente de `promociones`). Una línea de lleva_paga sin unidades gratis queda con `promocion_id = null`, así que no cuenta como aplicación.
6. **Preguntas abiertas 1 a 11:** el usuario aceptó todos los valores por defecto (ver la sección "Preguntas abiertas").

## Estado actual verificado

- **`Backend/src/promociones/`**
  - `Promocion.descuento` es NOT NULL, con el CHECK `0 < descuento <= 100`.
  - `detectar_promocion` elige el mayor `descuento` y, ante empate, el menor id.
  - `calcular_precio_final` calcula por línea y redondea hacia arriba en la mitad.
  - Una promoción en uso no se puede modificar (409). Eso mantiene estables sus parámetros una vez aplicada.
- **`Backend/src/routers/detalles_factura.py`**
  - POST: detecta la promoción y calcula la línea.
  - PUT: vuelve a detectar solo si cambia `detalle_comanda_id`. Un cambio de `cantidad` no vuelve a detectar (PRO-47, PRO-48, PRO-50).
  - DELETE: es baja lógica y recalcula el total.
  - Las columnas de precio son `Float`.
- **Facturas pagadas:** nada impide modificar sus líneas. Solo se rechaza `DELETE /facturas/{id}` cuando la factura tiene comprobantes activos.
- **Combos:**
  - Las tablas intermedias son `Table` usadas como `secondary`, con PK compuesta. Una tabla `secondary` no puede guardar `cantidad`, así que hacen falta objetos de asociación.
  - `registro.py` (`RESTRICT_POR_TIPO`) y `buscar_bloqueantes` dependen de esas tablas.
  - No existe interfaz de combos en el frontend.
- **Migraciones:** no hay framework. El esquema sale de `create_all`, y `poblar_db` hace drop y recreate.

## Motor propuesto

Para recalcular el producto P dentro de la factura F:

1. Se toman las líneas activas de F con producto P y se calcula `total = Σ cantidad`.
2. Candidatas = promociones vigentes, no dadas de baja, que incluyen P, ∪ promociones ya referenciadas por esas líneas.
3. Ahorro en pesos, calculado en Decimal:
   - porcentaje: `Σ (bruto − precio_final)` por línea.
   - lleva_paga: `Σ pu × unidades_gratis`, con la asignación a las líneas más baratas.
4. Gana el mayor ahorro; ante empate, el menor id. Un ahorro de 0 no gana.
5. Resultado por línea:
   - porcentaje: todas las líneas del producto reciben la promoción.
   - lleva_paga: `precio_final = pu × (cantidad − gratis)`, y solo las líneas con unidades gratis reciben `promocion_id`.
6. Se recalcula `importe_total`.

## Escenarios de `promociones` afectados

- **Modificados:**
  - PRO-33 a PRO-36 y PRO-39 (detección y desempate).
  - PRO-42, PRO-47 a PRO-50 y PRO-55 (recálculo del grupo).
  - PRO-01, PRO-03, PRO-05 a PRO-07, PRO-19, PRO-21 y PRO-28 (tipo y CHECK).
  - PRO-73 y PRO-74 (forma de la respuesta del combo).
- **Nuevos:**
  - 2x1 y 3x2.
  - Varias líneas de un mismo producto.
  - Unidades gratis en la línea más barata.
  - Comparación en pesos entre los dos tipos.
  - Promoción conservada tras su baja.
  - Menos unidades que `lleva`.
  - Recálculo en alta, modificación y baja de línea, y al cambiar el detalle de comanda.
  - Cantidades en los combos.

## Preguntas abiertas (con propuesta por defecto)

1. **Porcentaje bajo agrupación:** el `precio_final` se sigue calculando por línea, con el redondeo actual.
2. **Redondeo en lleva_paga:** no requiere una regla extra, porque `pu × unidades` es exacto a 2 decimales.
3. **`unidades_gratis`:** se persiste en `DetalleFactura` (entero, por defecto 0) y se expone en la respuesta.
4. **Combos en lleva_paga:** se permiten; el precio unitario es el precio manual del combo.
5. **Vigencia de una promoción conservada:** no se revalida.
6. **Precios distintos dentro de un mismo producto:** se aplica la regla de "más baratas primero".
7. **Promoción por línea en la UI de facturación:** queda fuera de alcance; la API expone `promocion_id` y `unidades_gratis`.
8. **Baja de una línea:** conserva su `promocion_id` y su `precio_final` como historial; solo se recalculan las activas.
9. **Factura pagada:** se mantiene el comportamiento actual y se documenta.
10. **Cantidad en combos:** entero `>= 1`, sin máximo.
11. **Bases existentes:** sin migración. Se resetea con `poblar_db`, porque SQLite no permite alterar CHECK.

## Riesgos

- **Cambio incompatible de la API de combos:** se reescriben unas 140 referencias en tests.
- **Refactor de las asociaciones de combos:** puede romper `RESTRICT_POR_TIPO` y `buscar_bloqueantes`. Hay que conservar los nombres de tablas y columnas.
- **Semántica ya implementada:** el cambio modifica comportamiento de `promociones`, que todavía no está archivado.
- **Mezcla de `Float` y `Decimal`:** convertir siempre con `Decimal(str(...))`.
- **Tamaño:** grande, entre 45 y 60 tareas y bastante más de 400 líneas.
