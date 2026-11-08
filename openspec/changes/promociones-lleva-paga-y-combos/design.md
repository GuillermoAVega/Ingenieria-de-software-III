# Diseño: Promociones "lleva X paga Y" y cantidades en combos

## Enfoque técnico

Se extienden los paquetes existentes `promociones/` y `productos/combos/` (patrón entity-per-folder). El motor se separa en una función pura de cálculo y una orquestación con base de datos, ambas en `promociones/services.py`. El router legado `routers/detalles_factura.py` deja de detectar promociones por línea y recalcula el grupo de cada producto afectado. El frontend agrega el selector de tipo y una feature `combos`.

## Decisiones de arquitectura

| Tema | Elegida | Descartada | Motivo |
|------|---------|------------|--------|
| Asociación de combos | Clases `ComboPlato/ComboBebida/ComboPostre` con `__tablename__` `combo_plato`, etc., PK `(combo_id, <tipo>_id)`, `cantidad` NOT NULL `server_default "1"`, CHECK `ck_combo_<tipo>_cantidad_minima`. Alias de módulo `combo_plato = ComboPlato.__table__` | `Table` + `secondary` | Una `secondary` no guarda columnas; el alias mantiene `RESTRICT_POR_TIPO`, `buscar_bloqueantes` y `test_registro` sin cambios |
| Nombres ORM | `ComboPromocion.componentes_platos` (asociación, `cascade="all, delete-orphan"`, `order_by` id del componente); propiedades `platos/bebidas/postres` → `[{"id", "cantidad"}]` ordenadas por id | Alias de validación Pydantic | `ComboRespuesta` lee las propiedades sin alias |
| Relación inversa | `Plato.combos = relationship("ComboPromocion", secondary="combo_plato", viewonly=True)` (igual en bebida y postre) | Eliminarla | `plato.combos == [combo]` sigue valiendo; la escritura solo pasa por la asociación |
| Actualización de componentes | `_sincronizar(actuales, nuevos)`: reutiliza el objeto existente (cambia `cantidad`), crea los nuevos y quita los ausentes; se pasa como `componentes_platos=` a `actualizar_producto` | Reemplazar la lista completa | Evita conflictos de identidad con PK compuesta |
| `Promocion.tipo` | `String(20)` NOT NULL; `descuento` nullable; `lleva`, `paga` `Integer` nullable. `ck_promocion_tipo` (IN) y `ck_promocion_parametros` (disyunción por tipo) reemplazan `ck_promocion_descuento_rango` | Tablas por subtipo | Decisión 2 |
| Payload | Modelo plano con `tipo: Literal[...]`, `descuento: Decimal \| None`, `lleva/paga: StrictInt \| None`; `model_validator` por tipo (422). `null` equivale a ausente | Unión discriminada | Respuesta plana; `PromocionActualizar = PromocionCrear` se mantiene |
| Baja perezosa | `dar_de_baja_vencidas(sesion, hoy)`: un `update(Promocion)` con `fecha_hasta < hoy` y `dado_de_baja` falso, `synchronize_session=False` y `commit`. Se invoca primero en `listar_promociones`, en `GET /{id}` y en POST/PUT/DELETE de detalles de factura, antes de cualquier mutación | Tarea programada | Decisión 4; la invocación previa evita confirmar cambios a medias |
| `hoy` | `Depends(obtener_hoy)` en los GET de promociones y en los tres endpoints de detalles | `date.today()` | Las pruebas fijan `HOY_FIJO` |
| Conversión | `a_decimal(valor) = Decimal(str(valor))` en `src/utils.py` | Conversión local | Código compartido en la raíz (`rules.design`) |
| UI de combos | `Frontend/src/features/combos/`, rutas `/promociones/combos`, `/nuevo`, `/:id/editar`; botón "Combos" en el listado de promociones, sin ítem de navegación | Subcarpeta de `promotions` | Precedente de `executive-menus`; un ítem bajo `/promociones` se marcaría activo dos veces |
| Selector | `features/promotions/ProductPicker.tsx` presentacional; `quantityOf` y `onQuantityChange` opcionales muestran un input numérico (mín. 1) por seleccionado | Duplicar el JSX | Lo usan los dos formularios |

## Motor

```python
@dataclass(frozen=True)
class LineaGrupo: id: int; precio_unitario: Decimal; cantidad: int
@dataclass(frozen=True)
class Candidata: id: int; tipo: str; descuento: Decimal | None; lleva: int | None; paga: int | None
@dataclass(frozen=True)
class Asignacion: promocion_id: int | None; precio_final: Decimal; unidades_gratis: int

def calcular_grupo(lineas, candidatas) -> dict[int, Asignacion]: ...       # pura
def recalcular_producto(sesion, factura, producto_id) -> None: ...          # base de datos
```

Se aplica exactamente "Motor propuesto" de `explore.md`. Las líneas se ordenan por `(precio_unitario, id)` y las candidatas por `id`. El porcentaje reutiliza `calcular_precio_final`. `recalcular_producto` carga las líneas activas de la factura (`join DetalleComanda`, `producto_id`, `ORDER BY id`) y busca candidatas con `(vigente AND no dada de baja AND incluye P) OR id IN (promocion_id de esas líneas)` a `fecha_hora_emision.date()`. Escribe `float(...)`. Se elimina `detectar_promocion`.

## Flujo de datos

    POST  -> baja perezosa -> snapshot pu -> add+flush -> recalcular(P) -> total -> commit
    PUT   -> baja perezosa -> [dc cambia: P_viejo, snapshot nuevo] -> cantidad -> flush
             -> recalcular(P) para cada P en sorted({P_viejo, P_nuevo}) -> total -> commit
    DELETE-> baja perezosa -> activo=False -> flush -> recalcular(P) -> total -> commit

La línea dada de baja conserva su `promocion_id` y su `precio_final`. `DetalleFactura.unidades_gratis` es `Integer` NOT NULL, `default=0`, `server_default "0"`, y se expone en `DetalleFacturaOut`.

## Cambios de archivos

| Archivo | Acción |
|---------|--------|
| `Backend/src/productos/combos/{models,schemas,services}.py`, `platos|bebidas|postres/models.py` | Modificar: asociación, `ComponenteCombo{id, cantidad>=1}`, ids duplicados 422, `campo` `platos|bebidas|postres`, `_sin_otros_cambios` compara `{id: cantidad}` |
| `Backend/src/promociones/{models,schemas,services,router}.py` | Modificar: tipo, CHECK, motor y baja perezosa |
| `Backend/src/models/detalle_factura.py`, `schemas/detalle_factura.py`, `routers/detalles_factura.py`, `src/utils.py` | Modificar |
| `Backend/scripts/poblar_db.py`, `scripts/seed.py` | Modificar: combos con cantidades; promociones con `tipo` (agrega 2x1 y 3x2 y un caso en el que 10 % y 2x1 compiten); `_facturar` usa `recalcular_producto` |
| `Backend/tests/...` | Ver estrategia |
| `Frontend/src/features/promotions/{types,usePromotionForm,PromotionFormPage,PromotionsListPage}` | Modificar: `tipo`, campos condicionales y columna "Beneficio" |
| `Frontend/src/features/promotions/{format.ts,ProductPicker.tsx}` | Crear: `formatBenefit` devuelve `"10%"`; `"NxM"` si `lleva - paga = 1`; si no, `"Lleva N paga M"` |
| `Frontend/src/features/combos/{types,api,useCombosList,useComboForm}.ts`, `{CombosListPage,ComboFormPage}.tsx` | Crear. Fuentes: platos, bebidas y postres |
| `Frontend/src/features/products/api.ts`, `app/routes.tsx` | Modificar: forma de `ComboListado` y rutas de combos antes de `/promociones/:id/editar` |

## Estrategia de pruebas (TDD estricto)

| Capa | Qué |
|------|-----|
| Unidad | `calcular_grupo`: 2x1 y 3x2, varias líneas, líneas más baratas primero, menos unidades que `lleva`, comparación en pesos, empates por id, ahorro 0 |
| Modelo | CHECK de `promocion` y `cantidad` de combos (`IntegrityError`), `server_default` |
| Integración | Matriz 422 del payload; baja perezosa en list, get y facturación; recálculo en POST, PUT (grupo viejo y nuevo) y DELETE; promoción conservada; `unidades_gratis`; CRUD de combos con cantidades; baja RESTRICT (`test_registro` y bloqueantes sin cambios) |
| Script | `test_poblar_db.py` actualizado |
| Frontend | `npm run lint`, `tsc -b` |

## Matriz de amenazas

N/A: no hay enrutamiento de shell, subprocesos, automatización de VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

No hay migración. Después de los PR 1 y 3 se ejecuta `poblar_db`. PRs encadenados (presupuesto de 400 líneas):

| PR | Alcance | Líneas |
|----|---------|--------|
| 1 | Backend combos con cantidad, seed, tests | ~400 (riesgo) |
| 2 | Frontend combos y `ProductPicker` | ~380 |
| 3 | `Promocion.tipo`, CHECK, baja perezosa, tests | ~300 |
| 4 | Motor, `unidades_gratis`, router, `poblar_db`, tests | ~390 |
| 5 | Frontend: selector de tipo y etiqueta | ~180 |

Dependencias: 1→2 y 3→4→5. Las cadenas 1-2 y 3-5 son independientes.

## Preguntas abiertas

Ninguna bloqueante.
