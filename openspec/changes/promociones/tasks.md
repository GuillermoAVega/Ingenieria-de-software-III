# Tareas: Promociones

## Review Workload Forecast

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | ~1420 (PR1 380, PR2 180, PR3 350, PR4 390, PR5 120) |
| Riesgo de presupuesto de 400 líneas | High (total); cada PR individual Medium/Low |
| PRs encadenados recomendados | Sí |
| División sugerida | PR 1 → PR 2 → PR 3 → PR 4 → PR 5 |
| Estrategia de entrega | ask-on-risk |
| Estrategia de cadena | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Unidades de trabajo sugeridas

| Unidad | Objetivo | PR | Comando de prueba | Harness de ejecución | Límite de rollback |
|--------|----------|----|-------------------|----------------------|--------------------|
| 1 | CRUD de promociones | PR 1 | `cd Backend && python -m pytest tests/promociones` | `uvicorn` + `POST /promociones` | `src/promociones/`, `main.py`, FK `promocion_id` |
| 2 | FK y validación `DetalleComanda.producto_id` | PR 2 | `cd Backend && python -m pytest tests/test_detalles_comanda*.py tests/test_comandas*.py` | `POST /detalles-comanda` con producto inexistente | modelo, helper y routers de comanda |
| 3 | Precios de línea de factura + flujo | PR 3 | `cd Backend && python -m pytest tests/test_flujo_facturacion.py tests/promociones` | `POST /detalles-factura` con promoción vigente | esquemas y router de `detalles_factura` |
| 4 | Frontend de promociones | PR 4 | `cd Frontend && npm run lint && npx tsc -b` | Alta de promoción en navegador | `features/promotions/`, `products/api.ts` |
| 5 | Facturación sin precios manuales | PR 5 | `cd Frontend && npm run lint && npx tsc -b` | Facturar una comanda en navegador | `features/orders/` |

## Fase 1: Backend CRUD de promociones (PR 1)

Nota: se agrega `DetalleFactura.promocion_id` (FK nullable) en este PR porque PRO-20, PRO-25 y PRO-70 lo necesitan. Reset de BD de desarrollo: borrar el archivo SQLite de `DB_URL` antes de arrancar el backend (`create_all` recrea el esquema). Documentarlo en la descripción del PR.

- [x] 1.1 RED: `Backend/tests/promociones/test_modelo.py`: CHECK de fechas y de descuento en base (PRO-28).
- [x] 1.2 RED: `Backend/tests/promociones/test_alta.py`: representación, alta y validaciones, 422/409 sin persistir (PRO-01 a PRO-13).
- [x] 1.3 RED: `Backend/tests/promociones/test_consulta.py`: GET por id y listado con `incluir_bajas` (PRO-14 a PRO-18).
- [x] 1.4 RED: `Backend/tests/promociones/test_modificacion.py`: PUT, en uso (inserción directa de `DetalleFactura`), productos nuevos y conservados (PRO-19 a PRO-23, PRO-69 a PRO-71).
- [x] 1.5 RED: `Backend/tests/promociones/test_baja.py`: DELETE idempotente, baja en uso (PRO-24 a PRO-27); baja de producto con promoción (PRO-65, PRO-66).
- [x] 1.6 GREEN: crear `Backend/src/promociones/{constants,exceptions,models,schemas}.py` con tabla `promocion_producto` y CHECKs (PRO-28).
- [x] 1.7 GREEN: modificar `Backend/src/models/detalle_factura.py` con `promocion_id` FK y relación `promocion`.
- [x] 1.8 GREEN: `Backend/src/promociones/services.py` con `promocion_en_uso` (PRO-20, PRO-70).
- [x] 1.9 GREEN: `Backend/src/promociones/router.py` con las 5 rutas; registrar modelo, router y manejadores en `Backend/src/main.py` (PRO-01 a PRO-27, PRO-69 a PRO-71).
- [x] 1.10 Agregar fixture `crear_promocion` en `Backend/tests/conftest.py`; ejecutar `cd Backend && python -m pytest`.

## Fase 2: FK y validación de `DetalleComanda.producto_id` (PR 2)

Reset de BD de desarrollo: borrar el SQLite de `DB_URL` (cambia una tabla existente).

- [x] 2.1 RED: `Backend/tests/test_validacion_producto_comanda.py`: 422 inexistente, 409 baja, `null`, PUT sin cambio, caso válido (PRO-57 a PRO-64, PRO-72).
- [x] 2.2 RED: mismo archivo: baja de producto no altera líneas existentes y comanda nueva con producto dado de baja (PRO-67, PRO-68 parte comanda).
- [x] 2.3 GREEN: clases `Conflict` y producto inválido en `Backend/src/exceptions.py`; helper `exigir_producto_activo` en `Backend/src/utils.py`.
- [x] 2.4 GREEN: `Backend/src/models/detalle_comanda.py` con `producto_id` FK y relación `producto`.
- [x] 2.5 GREEN: validar en `Backend/src/routers/comandas.py` (cada detalle anidado, atómico) y `Backend/src/routers/detalles_comanda.py` (POST y PUT; `null` rechazado) (PRO-57 a PRO-64, PRO-72).
- [x] 2.6 Fixture `crear_comanda_facturable` en `Backend/tests/conftest.py`; ejecutar suite completa.

## Fase 3: Precios de línea de factura y flujo (PR 3)

Reset de BD de desarrollo: borrar el SQLite de `DB_URL` (`detalle_comanda_id` pasa a NOT NULL).

- [x] 3.1 RED: `Backend/tests/promociones/test_calculo.py`: `calcular_precio_final` (PRO-43 a PRO-45) y `detectar_promocion` (PRO-33 a PRO-40).
- [x] 3.2 RED: `Backend/tests/promociones/test_lineas_factura.py`: POST (PRO-29 a PRO-32, PRO-41, PRO-42, PRO-46) y PUT (PRO-47 a PRO-52).
- [x] 3.3 RED: mismo archivo: totales y baja de promoción (PRO-53 a PRO-56); líneas conservan precios tras baja de producto (PRO-68, PRO-25).
- [x] 3.4 GREEN: `detectar_promocion` y `calcular_precio_final` en `Backend/src/promociones/services.py` (`Decimal`, half-up).
- [x] 3.5 GREEN: `Backend/src/schemas/detalle_factura.py` sin campos de precio de entrada; `detalle_comanda_id` obligatorio; `Backend/src/models/detalle_factura.py` NOT NULL (PRO-29, PRO-30).
- [x] 3.6 GREEN: `Backend/src/routers/detalles_factura.py`: snapshot, detección con `obtener_hoy`/fecha de emisión, PUT y `_recalcular_total` (PRO-31 a PRO-56).
- [x] 3.7 Reescribir `Backend/tests/test_flujo_facturacion.py` con fixture `cliente` y productos reales; ejecutar suite completa.

## Fase 4: Frontend de promociones (PR 4)

- [x] 4.1 `Frontend/src/features/promotions/types.ts` y `api.ts` con `apiFetch` sobre `/promociones`.
- [x] 4.2 `Frontend/src/features/products/api.ts`: `getMenusEjecutivos`, `getCombos`.
- [x] 4.3 `usePromotionsList.ts` y `usePromotionForm.ts` (objeto de estado único, selector de productos combinado).
- [x] 4.4 `PromotionsListPage.tsx` y `PromotionFormPage.tsx` solo render; eliminar `demo.ts`.
- [x] 4.5 Verificar `cd Frontend && npm run lint && npx tsc -b`.

## Fase 5: Facturación sin precios manuales (PR 5)

- [x] 5.1 `Frontend/src/features/orders/types.ts` y `useOrderDetail.ts`: eliminar `invoicePrices`/`setInvoicePrice`; payload `{factura_id, detalle_comanda_id, cantidad}`; total = suma de `precio_final`.
- [x] 5.2 `Frontend/src/features/orders/OrderDetailPage.tsx`: quitar entradas de precio.
- [x] 5.3 Verificar `npm run lint` y `npx tsc -b`.
- [ ] 5.4 (Pendiente al final, después de la fase 6) Verificación manual en navegador (usuario): crear promoción con productos, comanda, facturar y comprobar descuento y total; editar promoción en uso (409); baja de promoción.

## Fase 6: Combos en promociones (decisión del usuario, 2026-11-07)

- [x] 6.1 Tests primero: PRO-74 en `Backend/tests/productos/combos/` (`GET /productos/combos` lista solo activos) y PRO-73 en `Backend/tests/promociones/` (alta con un combo → 201).
- [x] 6.2 `Backend/src/productos/combos/router.py` y `services.py`: endpoint de listado `GET /productos/combos`, siguiendo el patrón de listado de los otros subtipos.
- [x] 6.3 Confirmar que `getCombos` de `Frontend/src/features/products/api.ts` coincide con la respuesta real y que el selector muestra los combos. Verificar `npx tsc -b` y `npm run lint`.

## Fase 7: Ajustes de UX de promociones (pedido del usuario, 2026-11-07)

- [x] 7.1 Tests primero (PRO-75, PRO-76): `en_uso` en las respuestas de alta, consulta, listado y modificación; `true` también con una línea inactiva.
- [x] 7.2 `Backend/src/promociones/schemas.py` y `services.py`: exponer `en_uso` reutilizando el criterio de `promocion_en_uso`, sin una consulta por fila en el listado.
- [x] 7.3 Frontend, edición bloqueada: en el listado no se ofrece "Editar" para promociones con `en_uso` (y se indica "En uso" con su motivo). Si se entra directo a `/promociones/:id/editar` con una promoción en uso, se muestra un aviso en español y el formulario no se habilita, con un enlace de vuelta al listado.
- [x] 7.4 Frontend, selector de productos: reemplazar la lista larga por un selector con barra de búsqueda (filtra por nombre, sin distinguir mayúsculas ni tildes) y casillas de verificación; muestra el tipo de cada producto, la cantidad seleccionada y los seleccionados aunque no coincidan con el filtro. Lógica de filtrado en el hook, componente solo render (AGENTS.md).
- [x] 7.5 Verificar `pytest`, `npx tsc -b` y `npm run lint`.

## Anexo: cobertura PRO → tarea

| PRO | Tarea | PRO | Tarea | PRO | Tarea |
|-----|-------|-----|-------|-----|-------|
| 01-13 | 1.2, 1.6, 1.9 | 33-40 | 3.1, 3.4 | 57-64 | 2.1, 2.5 |
| 14-18 | 1.3, 1.9 | 41, 42, 46 | 3.2, 3.6 | 65, 66 | 1.5 |
| 19-23 | 1.4, 1.9 | 43-45 | 3.1, 3.4 | 67 | 2.2 |
| 20, 70 | 1.4, 1.8 | 47-52 | 3.2, 3.6 | 68 | 2.2, 3.3 |
| 24-27 | 1.5, 1.9 | 53-56 | 3.3, 3.6 | 69, 71 | 1.4, 1.9 |
| 28 | 1.1, 1.6 | 29-32 | 3.2, 3.5, 3.6 | 72 | 2.1, 2.5 |
