# Propuesta: Promociones "lleva X paga Y" y cantidades en combos

## Intención

Hoy una promoción solo aplica un porcentaje por línea, y un combo no puede incluir varias unidades de un mismo componente. El negocio necesita promociones 2x1/3x2 por producto y combos con cantidades. Las decisiones están confirmadas en `explore.md` (puntos 1 a 6 y valores por defecto 1 a 11).

## Alcance

### Incluido
- `cantidad >= 1` en `combo_plato`, `combo_bebida` y `combo_postre`. La API pasa a `platos|bebidas|postres: [{id, cantidad}]`.
- `Promocion.tipo` (`porcentaje` | `lleva_paga`) con CHECK por tipo.
- Motor agrupado por producto dentro de la factura: una promoción por producto (mayor ahorro en pesos, desempate por menor id), unidades gratis a las líneas más baratas, `DetalleFactura.unidades_gratis`.
- Baja perezosa por vencimiento (un único `UPDATE`).
- Frontend: selector de tipo en el formulario de promociones y pantalla de combos con cantidades.

### Excluido
- Mostrar la promoción por línea en la UI de facturación.
- Migraciones: las bases se resetean con `poblar_db`.
- Bloquear la edición de facturas pagadas (comportamiento actual, documentado).
- Tareas programadas.

## Capacidades

### Nuevas
- `promotions-ui`: selector de tipo en promociones y alta, edición y baja de combos con cantidad por componente.

### Modificadas
- `promotion-management` (de `promociones`): tipo, CHECK y baja perezosa (PRO-01, 03, 05-07, 19, 21, 28). Forma del combo (PRO-73, PRO-74).
- `invoice-line-pricing` (de `promociones`): detección y recálculo por grupo (PRO-33 a 36, 39, 42, 47 a 50, 55), `unidades_gratis`.
- `product-catalog`: requisito "Composición de ComboPromocion" y escenarios con `*_ids` (por ejemplo, CAT-S-20).

## Enfoque

- Objetos de asociación para las tablas de combo, conservando los nombres de tablas y columnas para `RESTRICT_POR_TIPO` y `buscar_bloqueantes`.
- Motor en `Backend/src/promociones/services.py`, calculado en `Decimal` con conversión `Decimal(str(...))`.
- Se respeta la convención de una carpeta por entidad.
- TDD estricto en el backend.

## Áreas afectadas

| Área | Impacto |
|------|---------|
| `Backend/src/productos/combos/` | Modificada |
| `Backend/src/promociones/` | Modificada |
| `Backend/src/models/detalle_factura.py`, `Backend/src/routers/detalles_factura.py` | Modificada |
| `Backend/scripts/` (`poblar_db`) | Modificada |
| `Frontend/src/features/promotions/` | Modificada/Nueva |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Cambio incompatible de la API de combos (unas 140 referencias en tests) | Alta | Un slice dedicado y actualizar el frontend en el mismo cambio |
| El refactor de las asociaciones rompe `RESTRICT_POR_TIPO`/`buscar_bloqueantes` | Media | Mismos nombres; tests de baja RESTRICT primero |
| Bases sin migración (SQLite no altera CHECK) | Alta | Reset con `poblar_db`, documentado |
| Mezcla de `Float` y `Decimal` | Media | Conversión centralizada |
| Se modifica semántica no archivada de `promociones` | Media | Deltas explícitos sobre PRO-xx |

## Rollback

Revertir los commits del cambio y ejecutar `poblar_db` para recrear el esquema anterior.

## Dependencias

- `promociones` DEBE archivarse (specs sincronizadas a `openspec/specs/`) antes de archivar este cambio, cuyos deltas modifican esas capacidades.

## Tamaño y slices

Grande: entre 45 y 60 tareas, más de 400 líneas. Slices sugeridos:
1. Cantidad en combos (backend + UI de combos).
2. `Promocion.tipo` + motor + baja perezosa.
3. Selector de tipo en el frontend de promociones.

## Criterios de éxito

- [ ] 2x1 y 3x2 correctos con varias líneas y precios distintos.
- [ ] Se aplica una sola promoción por producto, la de mayor ahorro en pesos.
- [ ] Los combos guardan y devuelven cantidades; la baja RESTRICT sigue funcionando.
- [ ] Las promociones vencidas quedan dadas de baja al consultarlas.
- [ ] `pytest`, `npm run lint` y `tsc -b` en verde.
