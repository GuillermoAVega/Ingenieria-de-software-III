# Exploración: promociones

## Alcance confirmado

- Nueva entidad `Promocion` en `Backend/src/promociones/` con `fecha_desde`, `fecha_hasta`, `descuento` (porcentaje) y `dado_de_baja` (booleano, misma convención que `Producto.dado_de_baja`).
- Relación N:M `Promocion` ↔ `Producto` (al menos un producto por promoción).
- `DetalleFactura.promocion_id` pasa a ser FK opcional a `promocion.id`.
- `DetalleFactura.detalle_comanda_id` pasa a ser obligatorio; el producto de la línea se obtiene de `DetalleComanda.producto_id`.
- `DetalleComanda.producto_id` pasa a ser FK a `producto.id`.
- El backend toma `precio_unitario` de `Producto.precio` (snapshot al crear la línea) y calcula `precio_final = precio_unitario * cantidad * (1 - descuento / 100)`.
- La promoción se valida al asignarla: no dada de baja, incluye el producto de la línea y vigente a la fecha de `Factura.fecha_hora_emision`.
- `ComboPromocion` queda fuera de alcance.

## Hallazgos de backend

- El esquema se crea con `ModeloBase.metadata.create_all` en el lifespan de `Backend/src/main.py`; no hay Alembic. Las migraciones existentes son funciones ad hoc `migrar_*_legacy` en `Backend/src/database.py`.
- `create_all` no altera tablas existentes. Las tablas `promocion` y de asociación se crean solas; las FK nuevas y el `NOT NULL` de `detalle_comanda_id` requieren reconstruir tablas en SQLite o resetear la base.
- `configurar_sqlite` activa `PRAGMA foreign_keys=ON`: las FK nuevas se hacen cumplir.
- Los modelos de facturación están en `Backend/src/models/`, `Backend/src/routers/` y `Backend/src/schemas/` (estilo legado, no entity-per-folder).
- `Promocion` debe seguir el patrón de `secciones` / `productos_menu`: `models`, `schemas`, `exceptions`, `constants`, `services`, `router`, con `MANEJADORES_EXCEPCIONES` registrados en `main.py` y el modelo importado antes de `create_all`.
- `Producto.precio` es `Numeric` (Decimal) y `DetalleFactura.precio_*` es `Float`: conviene calcular en Decimal y redondear a 2 decimales.
- `Factura.fecha_hora_emision` es `DateTime` y las fechas de la promoción son `Date`: comparar con `.date()`.
- `Backend/src/routers/detalles_factura.py`:
  - `crear_detalle_factura` recibe hoy `precio_unitario` y `precio_final` del cliente; deben derivarse en el servidor.
  - `_validar_detalle_comanda` acepta `None`; debe exigirse.
  - `modificar_detalle_factura` debe revalidar la promoción y recalcular el precio si cambian `promocion_id`, `cantidad` o `detalle_comanda_id`.
  - `_recalcular_total` no requiere cambios.
- `Backend/src/schemas/detalle_factura.py`: `Create` y `Update` dejan de aceptar `precio_unitario` y `precio_final`.
- `DetalleComanda.producto_id` como FK: `routers/comandas.py` y `routers/detalles_comanda.py` no validan el producto; un id inexistente provocaría `IntegrityError` (500). Falta validación con respuesta 404/422.

## Hallazgos de tests

- `Backend/tests/test_flujo_facturacion.py` ya falla antes de este cambio: usa el fixture `client`, que no existe (`conftest.py` solo define `cliente`), e ids ficticios de producto, mozo, mesa y cliente.
- El resto de los tests no toca estas tablas.
- Hacen falta fixtures `crear_promocion`, de comanda y de factura. Los tests de integración usan `cliente` con `HOY_FIJO = 2026-06-15`.

## Hallazgos de frontend

- La UI activa es `App.tsx` → `app/routes.tsx` → `features/*`. `Frontend/src/pages/*` y `Frontend/src/api.ts` son código legado sin ruta: el "Ítem manual" de `pages/FacturaDetalle.tsx` no está en uso.
- El flujo vivo de facturación es `features/orders/useOrderDetail.ts` (`generateInvoice`): pide `precio_unitario` por ítem y llama a `createInvoiceLine`. Ese paso debe eliminarse.
- `features/orders/types.ts` (`InvoiceLinePayload`) cambia: `detalle_comanda_id` obligatorio y sin `precio_unitario`.
- No hay pantalla de edición de líneas de factura en `features`; solo `BillingListPage`.
- `features/promotions` es demo (`types.ts`, `demo.ts`, `PromotionsListPage.tsx`, `PromotionFormPage.tsx`) con campos que no existen en el modelo (`name`, `appliesTo`, `discountType`).
- No existe `GET /productos` genérico; los productos se listan por tipo.

## Preguntas abiertas (con propuesta por defecto)

1. **P1. Baja de una promoción usada**: baja lógica siempre permitida; las líneas existentes conservan `promocion_id` y precio guardado.
2. **P2. Edición de una promoción usada**: se permite editar descuento y fechas; no recalcula líneas ya guardadas.
3. **P3. Asignación de promoción a una línea**: se permite en alta y en modificación, revalidando y recalculando; en la UI, selector de promociones válidas por línea al generar la factura.
4. **P4. Límites del descuento**: `0 < descuento <= 100`, hasta 2 decimales.
5. **P5. Solapamiento**: se permiten promociones solapadas para un mismo producto.
6. **P6. Rango de fechas**: `fecha_desde <= fecha_hasta` con CHECK; se rechaza crear con `fecha_hasta` ya vencida, como `ComboPromocion`.
7. **P7. Productos dados de baja**: las comandas nuevas rechazan productos dados de baja; dar de baja un producto no se bloquea por promociones.
8. **P8. Datos y tests**: reset de la base de desarrollo sin migración de datos; reescribir `test_flujo_facturacion.py` dentro de este cambio.
9. **P9. Listado**: `GET /promociones` oculta las dadas de baja por defecto, con filtro opcional para incluirlas.
10. **P10. Representación**: la respuesta incluye `productos_ids`; sin campo `nombre`.

## Decisiones confirmadas por el usuario (2026-11-07)

Estas decisiones reemplazan las propuestas por defecto anteriores.

- **P1**: aceptada. La baja lógica siempre está permitida y las líneas existentes conservan `promocion_id` y precio.
- **P2**: una promoción ya utilizada en al menos una línea **no se puede modificar**, para no romper la coherencia entre la línea y el descuento aplicado. La baja sigue permitida.
- **P3**: **detección automática**. El cliente no envía `promocion_id`. Al crear la línea, el backend toma las promociones no dadas de baja que incluyen el producto y están vigentes a la fecha de emisión de la factura, y aplica la de **mayor descuento**. Si hay empate, gana el **menor id**. Al modificar la línea, se vuelve a detectar solo si cambia `detalle_comanda_id`. Una promoción creada después no afecta líneas existentes.
- **P4**: aceptada. `0 < descuento <= 100`, hasta 2 decimales.
- **P5**: se **permite** que un producto esté en varias promociones activas y vigentes a la vez; el desempate es el de P3.
- **P6**: aceptada. `fecha_desde <= fecha_hasta` con CHECK, y se rechaza crear una promoción con `fecha_hasta` vencida.
- **P7**: aceptada. Las comandas nuevas rechazan productos dados de baja, y las promociones no bloquean la baja de un producto.
- **P8**: aceptada. Reset de la base de desarrollo sin migración de datos, y reescritura de `test_flujo_facturacion.py` en este cambio.
- **P9**: aceptada. `GET /promociones` oculta las dadas de baja por defecto, con un filtro para incluirlas.
- **P10**: se **agrega** el atributo obligatorio `nombre` a `Promocion`; la respuesta incluye `productos_ids`.

## Riesgos

- Sin migraciones: las FK y el `NOT NULL` no se aplican a bases existentes.
- Filas huérfanas en `detalle_comanda` y `detalle_factura` impiden migrar datos existentes.
- `IntegrityError` (500) si no se valida `producto_id`.
- Mezcla de Decimal y float en el cálculo de precios.
- Selector de productos sin endpoint genérico de listado.
