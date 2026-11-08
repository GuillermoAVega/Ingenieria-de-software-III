# Propuesta: Promociones

## Intención

Las líneas de factura reciben hoy el precio desde el cliente y `promocion_id` no referencia nada. Se necesita una entidad `Promocion` con descuento porcentual aplicado automáticamente por el backend.

## Alcance

### Incluido
- `Promocion(nombre, fecha_desde, fecha_hasta, descuento, dado_de_baja)` en `Backend/src/promociones/` (convención entity-per-folder), N:M con `Producto` (al menos uno). CRUD con baja lógica.
- `DetalleFactura`: `promocion_id` FK opcional asignada automáticamente; `detalle_comanda_id` obligatorio; precios calculados en el servidor.
- `DetalleComanda.producto_id` como FK con validación de servicio (404/422).
- Reescritura de `Backend/tests/test_flujo_facturacion.py`.
- Frontend: `features/promotions` conectado a la API; `generateInvoice` sin carga manual de precios.

### Excluido
- `ComboPromocion`, migración de datos (se resetea la base), `Frontend/src/pages/*` y `Frontend/src/api.ts` (legado sin ruta).

## Capacidades

### Nuevas
- `promotion-management`: CRUD de promociones, validaciones, filtro de bajas, bloqueo de modificación si está en uso.
- `invoice-line-pricing`: detección automática de promoción y cálculo de precios de `DetalleFactura`.
- `order-line-product-validation`: validación de `DetalleComanda.producto_id`.

### Modificadas
- `product-logical-delete`: las promociones no bloquean la baja; las líneas de comanda nuevas rechazan productos dados de baja.

## Enfoque

- Detección: promociones no dadas de baja, con el producto, vigentes a `Factura.fecha_hora_emision.date()`; mayor descuento, empate por menor id. Se redetecta solo si cambia `detalle_comanda_id`.
- `precio_unitario` = snapshot de `Producto.precio`; `precio_final = pu * cantidad * (1 - d/100)` en `Decimal`, redondeado a 2 decimales.
- `0 < descuento <= 100`; CHECK `fecha_desde <= fecha_hasta`; alta con `fecha_hasta` vencida rechazada; solapamientos permitidos.
- Promoción usada en una línea: modificación 409, baja permitida.
- `GET /promociones` oculta bajas por defecto.
- Decisión para diseño: cómo listar productos en el selector (no existe `GET /productos` genérico).

## Áreas afectadas

| Área | Impacto |
|------|---------|
| `Backend/src/promociones/` | Nuevo |
| `Backend/src/main.py` | Router, manejadores, import previo a `create_all` |
| `Backend/src/models/`, `schemas/detalle_factura.py`, `routers/detalles_factura.py` | Modificado |
| `Backend/src/routers/comandas.py`, `detalles_comanda.py` | Validación de producto |
| `Backend/tests/` | Nuevos tests y fixtures |
| `Frontend/src/features/promotions/` | Reemplaza demo |
| `Frontend/src/features/orders/useOrderDetail.ts`, `types.ts` | Modificado |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Sin migraciones: FK y `NOT NULL` no se aplican a bases existentes | Alta | Reset documentado de la base de desarrollo |
| Mezcla `Decimal`/`float` | Media | Calcular en `Decimal`, persistir redondeado |
| `IntegrityError` 500 por FK | Media | Validar en servicio antes de escribir |
| Tamaño estimado 1500-1800 líneas, supera el presupuesto de 400 | Alta | PRs encadenados: CRUD promociones; FK comanda; precios de factura; frontend promociones; frontend facturación |

## Plan de reversión

Revertir los commits por PR en orden inverso y resetear la base de desarrollo; `create_all` recrea el esquema anterior.

## Dependencias

- Ninguna externa.

## Criterios de éxito

- [ ] `cd Backend && python -m pytest` pasa, incluido el flujo de facturación reescrito.
- [ ] Una línea toma la promoción vigente de mayor descuento sin que el cliente envíe precios.
- [ ] Ningún `producto_id` inválido produce 500.
- [ ] `npm run lint` y `tsc -b` pasan en Frontend.
