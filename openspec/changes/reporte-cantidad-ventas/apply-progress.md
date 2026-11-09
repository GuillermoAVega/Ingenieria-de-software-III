# Progreso de implementación: reporte-cantidad-ventas

## Estado

Tareas 1.1 a 2.7 completas. La tarea 2.8 queda pendiente de la verificación manual en el navegador por parte del usuario; su parte automática (build y eslint) se ejecutó.

Modo: Strict TDD (Backend). El Frontend no tiene runner de tests; se verifica con `tsc`, `build` y `eslint`.

### TDD Cycle Evidence

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 1.1 | `Backend/tests/reportes/test_cantidad_ventas.py` | Unit | N/A (new) | ✅ Written (falla en la colección: `src.reportes` no existía) | ✅ Passed (1.6) | ✅ 4 casos: vacío, huecos, lunes/domingo, totales iguales | ➖ None needed |
| 1.2 | `Backend/tests/reportes/test_cantidad_ventas.py` | Integration | N/A (new) | ✅ Written | ✅ Passed (1.5, 1.8) | ✅ 422 parametrizado: sin `anio`, `abc`, `999`, `10000`; más el límite `9999` válido | ➖ None needed |
| 1.3 | `Backend/tests/reportes/test_cantidad_ventas.py` | Integration | N/A (new) | ✅ Written | ✅ Passed (1.7) | ✅ 5 casos: 1 comprobante, 2 comprobantes, factura anulada, sin comprobantes, comprobantes inactivos | ➖ None needed |
| 1.4 | `Backend/tests/reportes/test_cantidad_ventas.py` | Integration | N/A (new) | ✅ Written | ✅ Passed (1.7) | ✅ 1 test (`test_bordes_del_anio`) con 4 instantes de borde | ➖ None needed |
| 1.5–1.8 | (implementación de 1.1–1.4) | — | `pytest -q` sobre la base: 72 failed / 1101 passed / 10 errors (preexistentes) | — | ✅ `tests/reportes`: 16 passed | — | ✅ Clean |
| 1.9 | Suite completa | — | — | — | ✅ 72 failed / 1117 passed / 10 errors: +16 passed, sin fallos nuevos | — | — |

### Test Summary
- **Total tests written**: 16 (con parametrización)
- **Total tests passing**: 16
- **Layers used**: Unit (4), Integration (12), E2E (0)
- **Approval tests** (refactoring): None — no refactoring tasks
- **Pure functions created**: 1 (`agrupar_ventas`) en Backend; `toChartRows` y `getYearOptions` en Frontend

### Work Unit Evidence

| Evidence | Result |
|---|---|
| Focused test command | `cd Backend && venv/bin/python -m pytest tests/reportes -q` → 16 passed |
| Runtime harness | `TestClient` sobre `GET /reportes/ventas/cantidad` (tests de integración) |
| Frontend | `npx tsc -b`: 7 errores preexistentes, ninguno en `features/reports`. `npx eslint src/features/reports`: limpio |

## Deviations from Design

None — implementation matches design.

## Issues Found

- El fixture compartido `crear_comanda_facturable` usa `mozo_id=1, mesa_id=1` fijos y falla la clave foránea. Esto produce los 72 fallos y 10 errores preexistentes de la suite. El helper de este cambio crea su propio Sector, Mesa, Mozo y MedioPago.
- `tsc` y `npm run build` fallan por 7 errores preexistentes en `menu-view`, `products` y `orders`.

## Remaining Tasks

- [ ] 2.8 Verificación manual en el navegador: año por defecto, cambio de año, estado de error, otro slug sin selector.
