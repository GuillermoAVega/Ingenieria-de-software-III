```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:e21908ea9fd9cb93d6a6fa37f007045b503b5b8cc48c805be5a5e3d67fde8807
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 21/21
scenarios: 62/62
test_command: cd Backend && venv/bin/python -m pytest -q --ignore=tests/test_flujo_facturacion.py
test_exit_code: 0
test_output_hash: sha256:9a63a61262ccf65ff294e9dc1b7c50193d13d5c985a22a3d1ee1872373ed4c79
build_command: cd Backend && ENV=test venv/bin/python -c "import src.main"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Informe de verificación

**Cambio**: menu-del-dia-producto
**Modo**: TDD estricto (`strict_tdd: true`)

Conteo real de la especificación: 21 `### Requirement` (daily-menu-management 14, product-catalog 4, product-logical-delete 3) y 62 `#### Scenario` (29 + 19 + 14). Se usan los conteos reales (21/62), no 15.

### Completitud
Todas las tareas (1.1 a 5.1) figuran `[x]`. Las 7 casillas manuales de la tarea 4.6 siguen sin marcar ("pendiente de ejecutar en navegador"); la tarea 5.1 es documental.

### Ejecución
| Comando | Resultado |
|---|---|
| `cd Backend && venv/bin/python -m pytest -q --ignore=tests/test_flujo_facturacion.py` | 926 passed, 3 warnings, exit 0 |
| Suite completa sin `--ignore` | 926 passed, 5 errors |
| `cd Backend && ENV=test venv/bin/python -c "import src.main"` | OK (exit 0, salida vacía) |
| `cd Frontend && npx tsc -b` | Cero errores en `src/features`; solo TS2307 `react-router-dom` en `src/pages/*` |
| `cd Frontend && npx eslint src/features` | Sin salida, exit 0 |
| `cd Frontend && npm run build` | Falla solo por TS2307 `react-router-dom` (no instalado) en `src/pages`, preexistente |

**Fallo ambiental conocido (exclusión explícita)**: `Backend/tests/test_flujo_facturacion.py` tiene 5 errores preexistentes (`fixture 'client' not found`), ajenos a este cambio. Por eso el `test_command` lo excluye con `--ignore`.

### Matriz de escenarios
- Backend (52): MDD-01..24, 30..43, 49..62 tienen al menos una prueba que pasó (`Backend/tests/productos/menus_del_dia/` y las suites de `productos_menu`).
- Frontend (10, sin herramientas de prueba en el proyecto): MDD-25..29 y 44..48 verificados por lectura de código.
  - MDD-25/26: `useDailyMenuForm` carga `getMenusDelDia()` (solo activos) y envía `menu_del_dia_id` y `fecha`.
  - MDD-27: el `catch` asigna solo `error`/`fieldErrors`; conserva valores.
  - MDD-28: edición con `Input` deshabilitado con `menu_del_dia_nombre`; PUT con `{ fecha }`.
  - MDD-29: `DailyMenusTab` muestra nombre y `Badge` "Dado de baja".
  - MDD-44..46: tipo `menus-del-dia` en `products/api.ts`, hooks y páginas.
  - MDD-47: `products/errors.ts` `getDeleteErrorMessage` lee `fechas` del 409; `actionError` en el listado.
  - MDD-48: `format.ts` `menu_del_dia: 'Menú del día'`.

### Adherencia al diseño
Las decisiones 1 a 14 se reflejan en el código. Sin desviaciones detectadas.

### AGENTS.md (frontend)
Un solo `useState` con objeto tipado por hook; lógica en hooks; sin `fetch` directo; mensajes en español. Conforme.

### Hallazgos
**CRITICAL**: ninguno.

**WARNING**
1. Verificación manual del frontend (tarea 4.6) no ejecutada: MDD-25..29 y 44..48 carecen de comprobación en navegador y de pruebas automáticas.
2. En la pestaña "Menús del día" de `ProductsListPage.tsx` coexisten dos botones con el mismo texto "Nuevo menú del día": el fijo (asigna fecha a un menú existente; preexistente en HEAD) y el de la pestaña (crea el producto). No contradice la especificación pero es ambiguo.
3. `npm run build` y `npm run lint` globales fallan por causas preexistentes ajenas (`react-router-dom` faltante, `src/ui.tsx`).

**SUGGESTION**
1. Renombrar el botón fijo a "Asignar fecha a menú del día" o ocultarlo en la pestaña `menus-del-dia`.
2. Reiniciar la base SQLite local (tarea 5.1) antes de probar manualmente: `producto_menu` cambió de columna.

### Veredicto
PASS WITH WARNINGS. CRITICAL 0, WARNING 3, SUGGESTION 2. Listo para `sdd-archive`, idealmente tras la lista manual 4.6.
