# Tareas: Promociones "lleva X paga Y" y cantidades en combos

## Review Workload Forecast

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | ~1650 (PR1 ~400, PR2 ~380, PR3 ~300, PR4 ~390, PR5 ~180) |
| Riesgo de presupuesto de 400 líneas | High (PR1 y PR4 en el límite) |
| PRs encadenados recomendados | Sí |
| División sugerida | PR1→PR2 y PR3→PR4→PR5 (cadenas independientes) |
| Estrategia de entrega | ask-on-risk |
| Estrategia de cadena | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Unidades de trabajo sugeridas

| Unidad | Objetivo | PR | Comando de prueba | Harness | Límite de rollback |
|--------|----------|----|-------------------|---------|--------------------|
| 1 | Backend combos con cantidad | PR 1 | `cd Backend && venv/bin/python -m pytest tests/productos/combos tests/test_poblar_db.py` | `poblar_db` sobre BD nueva | `productos/combos`, modelos de componentes, `poblar_db` |
| 2 | Frontend combos | PR 2 (base PR 1) | `cd Frontend && npx tsc -b && npm run lint` | navegador, `/promociones/combos` | `features/combos`, `ProductPicker`, rutas |
| 3 | `Promocion.tipo`, CHECK, baja perezosa | PR 3 | `cd Backend && venv/bin/python -m pytest tests/promociones` | `poblar_db` sobre BD nueva | `promociones/{models,schemas,services,router}` |
| 4 | Motor, `unidades_gratis`, router, `poblar_db` | PR 4 (base PR 3) | `cd Backend && venv/bin/python -m pytest --ignore=tests/productos/menus_del_dia` | facturar 2x1 vía API | `detalle_factura`, router de detalles, `calcular_grupo` |
| 5 | Frontend selector de tipo y etiqueta | PR 5 (base PR 4) | `cd Frontend && npx tsc -b && npm run lint` | navegador, formulario de promoción | `features/promotions` |

Notas: `Backend/scripts/seed.py` está en `.gitignore` y roto (importa módulos inexistentes): fuera de alcance. Tras PR 1 y PR 3 (y PR 4) borrar la BD de desarrollo y ejecutar `poblar_db` (las tablas cambian; no hay migración).

## Fase 1: Backend combos con cantidad (PR 1)

- [x] 1.1 RED: `Backend/tests/productos/combos/test_router.py`: alta/consulta/PUT/listado con `{id, cantidad}`, cantidad 0/-1/1.5/ausente, 1000, duplicados, vacío, CAT-S-20 (PLC-54..59, PRO-74).
- [x] 1.2 RED: `Backend/tests/productos/combos/test_models.py`: CHECK de cantidad y `server_default` (PLC-61); baja RESTRICT del componente (PLC-60).
- [x] 1.3 GREEN: `Backend/src/productos/combos/models.py`: `ComboPlato/Bebida/Postre`, alias `combo_plato`, propiedades; `relationship viewonly` en `platos|bebidas|postres/models.py`.
- [x] 1.4 GREEN: `Backend/src/productos/combos/schemas.py`: `ComponenteCombo{id, cantidad>=1}`, listas nuevas, ids duplicados 422.
- [x] 1.5 GREEN: `Backend/src/productos/combos/services.py` y `router.py`: `_sincronizar`, `_sin_otros_cambios`, listado `GET /productos/combos`.
- [x] 1.6 `Backend/scripts/poblar_db.py`: combos con cantidades; actualizar `Backend/tests/test_poblar_db.py`; correr suite completa.

## Fase 2: Frontend combos (PR 2)

- [x] 2.1 Crear `Frontend/src/features/promotions/ProductPicker.tsx` (cantidad opcional, mín. 1) y adaptar `Frontend/src/features/products/api.ts` (`ComboListado`) (PLC-73, PLC-76, PLC-81).
- [x] 2.2 Crear `Frontend/src/features/combos/{types,api,useCombosList,useComboForm}.ts` con estado único y validación (PLC-74, PLC-75, PLC-80).
- [x] 2.3 Crear `CombosListPage.tsx` y `ComboFormPage.tsx`; rutas en `Frontend/src/app/routes.tsx` antes de `/promociones/:id/editar`; botón "Combos" en `PromotionsListPage.tsx` (PLC-72, PLC-77..79).
- [x] 2.4 Verificar `npx tsc -b` y `npm run lint`.

## Fase 3: Promocion.tipo, CHECK y baja perezosa (PR 3)

- [x] 3.1 RED: `Backend/tests/promociones/`: matriz 422 (PLC-02..10), alta/respuesta (PLC-01, PLC-11, PLC-12, PRO-01, PRO-03, PRO-05..07), PUT (PRO-19, PRO-21, PLC-19..22), CHECK (PRO-28, PLC-23).
- [x] 3.2 RED: baja perezosa en listado, GET por id, límite y sentencia única (PLC-13..18, PRO-14, PRO-17, PRO-73).
- [x] 3.3 GREEN: `Backend/src/promociones/models.py` y `schemas.py`: `tipo`, `lleva`, `paga`, `ck_promocion_tipo`, `ck_promocion_parametros`, validador por tipo.
- [x] 3.4 GREEN: `Backend/src/promociones/services.py` y `router.py`: `dar_de_baja_vencidas`, `obtener_hoy`; `a_decimal` en `Backend/src/utils.py`.
- [x] 3.5 Actualizar `poblar_db` con `tipo`; reiniciar BD de desarrollo.

## Fase 4: Motor y facturación (PR 4)

- [x] 4.1 RED unidad: `calcular_grupo` (PLC-24..27, 29..31, 33..36, 40, 50).
- [x] 4.2 RED integración: POST/PUT/DELETE de líneas, grupo viejo y nuevo, conservadas, baja previa, `unidades_gratis` (PLC-28, 32, 37..39, 41..49, 51..53, PRO-33..36, 39, 42, 47..50, 55).
- [x] 4.3 GREEN: `Backend/src/models/detalle_factura.py` y `schemas/detalle_factura.py`: `unidades_gratis` NOT NULL, default 0.
- [x] 4.4 GREEN: `Backend/src/promociones/services.py`: `calcular_grupo`, `recalcular_producto`; quitar `detectar_promocion`.
- [x] 4.5 GREEN: `Backend/src/routers/detalles_factura.py`: flujo del diseño con baja perezosa primero.
- [x] 4.6 `poblar_db`: 2x1, 3x2, caso 10 % vs 2x1, `_facturar` con `recalcular_producto`; actualizar `test_poblar_db.py`; reiniciar BD.

## Fase 5: Frontend tipo de promoción (PR 5)

- [x] 5.1 `Frontend/src/features/promotions/types.ts` y `format.ts` (`formatBenefit`: "10%", "NxM", "Lleva N paga M").
- [x] 5.2 `usePromotionForm.ts` y `PromotionFormPage.tsx`: selector, campos condicionales, validación, errores (PLC-62..67, PLC-69).
- [x] 5.3 `PromotionsListPage.tsx` y `usePromotionsList.ts`: columna "Beneficio", en uso no editable, vencida dada de baja (PLC-68, 70, 71).
- [x] 5.4 Verificar `npx tsc -b` y `npm run lint`.
- [ ] 5.5 Chequeo manual en navegador (usuario): combos con cantidades, promoción 2x1 y 3x2, facturar y ver `unidades_gratis`.

## Fase 6: Ajustes de UI pedidos por el usuario (2026-11-07)

- [x] 6.1 `PromotionFormPage.tsx`: la opción `lleva_paga` del selector de tipo dice "Por cantidad (2x1, 3x2…)".
- [x] 6.2 Combos en Productos: pestaña "Combos" en `ProductsListPage` (junto a Platos, Bebidas y Postres) con el listado de combos; rutas `/productos/combos/nuevo` y `/productos/combos/:id/editar` declaradas antes de `/productos/:tipo/...`; navegación de vuelta del formulario de combos a la pestaña Combos; eliminar las rutas `/promociones/combos*` y el botón "Combos" del listado de promociones.
- [x] 6.3 Verificar `npx tsc -b` y `npm run lint`.

## Anexo: cobertura

- PLC-01..12: 3.1, 3.3. PLC-13..18: 3.2, 3.4. PLC-19..23: 3.1, 3.3.
- PLC-24..53: 4.1..4.5. PLC-54..61: 1.1..1.5. PLC-62..71: 5.2, 5.3. PLC-72..81: 2.1..2.3.
- PRO-01, 03, 05..07, 19, 21, 28: 3.1. PRO-14, 17, 73: 3.2. PRO-74: 1.1, 1.5.
- PRO-33..36, 39, 42, 47..50, 55: 4.2. CAT-S-20: 1.1.
