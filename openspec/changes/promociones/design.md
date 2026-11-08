# Diseño: Promociones

## Enfoque técnico

Nuevo paquete `Backend/src/promociones/` (patrón `secciones`/`productos_menu`). La detección y el cálculo de precio viven en `promociones/services.py` y los consume el router legado `routers/detalles_factura.py`. `DetalleComanda.producto_id` pasa a FK con validación previa en los routers de comanda. El frontend reemplaza el demo de `features/promotions` y elimina la carga manual de precios en `generateInvoice`.

## Decisiones de arquitectura

| Tema | Opción elegida | Alternativa descartada | Motivo |
|------|----------------|------------------------|--------|
| Paquete | `promociones/{models,schemas,exceptions,constants,services,router}.py`; `MANEJADORES_EXCEPCIONES` en `main.py`; `from src.promociones import models` antes de `create_all` | Modelo en `src/models/` legado | Convención entity-per-folder de `config.yaml` |
| Asociación | Tabla `promocion_producto(promocion_id FK, producto_id FK)`, PK compuesta, definida en `promociones/models.py`; `relationship("Producto", secondary=...)` por cadena | Columna JSON de ids | Integridad referencial; `productos_ids` como propiedad, igual que `Seccion` |
| Restricciones | CHECK `fecha_desde <= fecha_hasta` y `descuento > 0 AND descuento <= 100`; `descuento Numeric(5,2)` | Solo validación Pydantic | Respaldo en base, como `ck_producto_precio_positivo` |
| Ubicación del cálculo | `promociones/services.py`: `detectar_promocion`, `calcular_precio_final`, `promocion_en_uso` | Lógica en el router legado | Testeable en unidad; sin ciclos: `promociones` importa `src.models.DetalleFactura` y `src.productos.models`, y ninguno de ellos importa `promociones` |
| Aritmética | `Decimal`; `quantize(Decimal("0.01"), ROUND_HALF_UP)`; se persiste `float(...)` en las columnas `Float` existentes | Cambiar columnas a `Numeric` | Evita tocar `Factura.importe_total` y los esquemas `Out` |
| "En uso" | `exists(DetalleFactura.promocion_id == id)` sin filtrar `activo` | Solo líneas activas | Conservador: una línea dada de baja conserva el descuento aplicado |
| Fecha de referencia | `obtener_hoy` de `productos.services` como dependencia | `date.today()` directo | El fixture `cliente` ya lo sobrescribe con `HOY_FIJO` |
| Producto de comanda | Helper `exigir_producto_activo(db, producto_id)` en `src/utils.py`: inexistente 422, dado de baja 409 (nuevas clases en `src/exceptions.py`) | Capturar `IntegrityError` | Mismos códigos que `productos_menu`; evita 500 |
| Selector de productos | Hook del frontend que combina `GET /productos/{platos,bebidas,postres,menus-ejecutivos,combos}` | Nuevo `GET /productos` agregado | `Producto` es abstracto por decisión del paquete `productos` (de otro grupo); no amplía el backend |
| Payload extra | `DetalleFacturaCreate/Update` con la configuración por defecto de Pydantic: `precio_unitario`, `precio_final` y `promocion_id` enviados por el cliente se ignoran | `extra="forbid"` (422) | Convención del repositorio; el payload actual del frontend sigue funcionando y recibe precios calculados por el servidor. `detalle_comanda_id` pasa a obligatorio, y el frontend vivo ya lo envía |
| `fecha_hasta` vencida | Se rechaza (422) en el alta y en `PUT` solo si `fecha_hasta` cambia respecto del valor guardado | Validar siempre en `PUT` | Permite editar una promoción no usada ya vencida sin tocar su fin |
| Productos en `PUT` | Solo los ids nuevos se validan (inexistente 422, dado de baja 409); los conservados no se revalidan por baja | Revalidar todos | Una baja posterior del producto no bloquea editar la promoción |

## Flujo de datos

    POST /detalles-factura {factura_id, detalle_comanda_id, cantidad}
      -> Factura (404) -> DetalleComanda activo y de la misma comanda (404/400)
      -> producto = detalle_comanda.producto
      -> promocion = detectar_promocion(producto.id, factura.fecha_hora_emision.date())
           WHERE no dada de baja AND producto en promocion AND desde <= fecha <= hasta
           ORDER BY descuento DESC, id ASC LIMIT 1
      -> precio_unitario = producto.precio ; precio_final = calcular(pu, cantidad, d)
      -> _recalcular_total(factura) -> commit

`PUT`: si cambia `detalle_comanda_id` se toma nuevo snapshot y se redetecta; si solo cambia `cantidad` se recalcula con `precio_unitario` y la promoción guardados (su descuento es inmutable porque una promoción usada no se modifica).

## Cambios de archivos

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `Backend/src/promociones/*` (7 archivos) | Crear | Entidad, CRUD, detección y cálculo |
| `Backend/src/main.py` | Modificar | Import del modelo, router y manejadores |
| `Backend/src/models/detalle_factura.py` | Modificar | `promocion_id` FK; `detalle_comanda_id` NOT NULL; relación `promocion` |
| `Backend/src/models/detalle_comanda.py` | Modificar | `producto_id` FK; relación `producto` |
| `Backend/src/schemas/detalle_factura.py` | Modificar | Create `{factura_id, detalle_comanda_id: int, cantidad}` y Update `{detalle_comanda_id?, cantidad?}`; campos extra ignorados; Out con `detalle_comanda_id: int` |
| `Backend/src/routers/detalles_factura.py`, `comandas.py`, `detalles_comanda.py` | Modificar | Precios del servidor; validación de producto (también en cada detalle anidado); `producto_id: null` en PUT se rechaza |
| `Backend/src/utils.py`, `Backend/src/exceptions.py` | Modificar | Helper y clases `Conflict` / producto inválido |
| `Backend/tests/conftest.py` | Modificar | Fixtures `crear_promocion`, `crear_comanda_facturable` |
| `Backend/tests/promociones/*`, `tests/test_flujo_facturacion.py` | Crear / Reescribir | Ver estrategia |
| `Frontend/src/features/promotions/{types,api,usePromotionsList,usePromotionForm}.ts` | Crear/Reescribir | API real y lógica fuera de las páginas |
| `Frontend/src/features/promotions/Promotion{sList,Form}Page.tsx` | Modificar | Solo render |
| `Frontend/src/features/promotions/demo.ts` | Eliminar | Datos falsos |
| `Frontend/src/features/products/api.ts` | Modificar | `getMenusEjecutivos`, `getCombos` |
| `Frontend/src/features/orders/{types,useOrderDetail}.ts`, `OrderDetailPage.tsx` | Modificar | Sin `invoicePrices`/`setInvoicePrice`; total = suma de `precio_final` devueltos |

## Interfaces

```python
# promociones/schemas.py
class PromocionCrear(BaseModel):  # también PromocionActualizar (reemplazo completo)
    nombre: str  # 1..NOMBRE_MAX, recortado
    fecha_desde: date
    fecha_hasta: date          # model_validator: desde <= hasta -> 422
    descuento: Decimal = Field(gt=0, le=100, decimal_places=2)
    productos_ids: list[int] = Field(min_length=1)  # sin duplicados
class PromocionRespuesta(...): id, nombre, fecha_desde, fecha_hasta, descuento, dado_de_baja, productos_ids
```

Rutas `/promociones`: `POST` 201 (422 `fecha_hasta` vencida o producto inexistente; 409 producto dado de baja), `GET ?incluir_bajas=false`, `GET /{id}` (404), `PUT /{id}` (409 `PromocionEnUso`; 422 `fecha_hasta` vencida solo si cambia; 422/409 solo para ids nuevos), `DELETE /{id}` 204 (baja lógica idempotente, permitida aunque esté en uso).

```ts
type Promotion = { id: number; nombre: string; fecha_desde: string; fecha_hasta: string;
  descuento: string; dado_de_baja: boolean; productos_ids: number[] }
type InvoiceLinePayload = { factura_id: number; detalle_comanda_id: number; cantidad: number }
```

## Estrategia de pruebas

| Capa | Qué | Cómo |
|------|-----|------|
| Unidad | `calcular_precio_final` (redondeo, 100 %), `detectar_promocion` (vigencia inclusiva, baja, empate por id) | `sesion` + `persistir` |
| Integración | CRUD, 409 en uso, filtro de bajas, 422/409 de comanda, `PUT` de línea | `cliente`, `HOY_FIJO`; factura con `fecha_hora_emision` explícita |
| Flujo | `test_flujo_facturacion.py` con fixture `cliente` y productos reales | Reescritura completa |
| Frontend | `npm run lint`, `tsc -b` | Sin runner |

## Matriz de amenazas

N/A: no hay enrutamiento de shell, subprocesos, automatización de VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

Sin migración de datos. Antes de iniciar el backend tras el PR 2, borrar el archivo SQLite indicado por `DB_URL`; `create_all` recrea el esquema. Se documenta en la descripción de cada PR que cambia tablas.

PRs encadenados (presupuesto 400 líneas):

| PR | Alcance | Líneas aprox. |
|----|---------|---------------|
| 1 | Backend CRUD de promociones + tests | 380 |
| 2 | FK y validación de `DetalleComanda.producto_id` + tests | 180 |
| 3 | Precios de factura, esquemas, reescritura del flujo | 350 |
| 4 | Frontend promociones (+ getters de productos) | 390 |
| 5 | Frontend facturación sin precios manuales | 120 |

El subtipo sin versionar `productos/menus_del_dia` queda fuera de este cambio; si se integra, el selector necesitará un getter adicional.

## Preguntas abiertas

Ninguna. Decisiones cerradas: producto referenciado inexistente 422 y dado de baja 409 (también en `productos_ids`); "en uso" incluye cualquier `DetalleFactura`, activa o no.
