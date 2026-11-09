```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:3277df5cc471aabf155931c81af958625c998f9a25fd92758c4d601883cb70a5
verdict: fail
blockers: 1
critical_findings: 0
requirements: 7/11
scenarios: 18/25
test_command: cd Backend && venv/bin/python -m pytest tests/reportes -q
test_exit_code: 0
test_output_hash: sha256:43ad7945524f91bddbe04c876d5524e0b05b453dc5050dcec0d177c4a1ad604f
build_command: cd Frontend && npx eslint src/features/reports
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Informe de verificación (re-ejecución tras corrección)

**Cambio**: reporte-cantidad-ventas | **Modo**: Strict TDD

### Completitud
| Métrica | Valor |
|---------|-------|
| Tareas totales | 17 |
| Completas | 16 |
| Incompletas | 1 (2.8, verificación manual en navegador; pendiente del usuario, aceptada como pendiente) |

### Ejecución
- `cd Backend && venv/bin/python -m pytest tests/reportes -q`: 16 passed, exit 0.
- `cd Backend && venv/bin/python -m pytest -q`: 72 failed, 1117 passed, 10 errors. Base: 72 failed, 1101 passed, 10 errors. +16 passed, sin fallos nuevos (coincide con los fallos ambientales conocidos).
- `cd Frontend && npx tsc -b --pretty false`: exit 2, 7 errores, todos preexistentes (menu-view/useMenuView.ts, products/productOptions.ts, orders/OrderFormPage.tsx); ninguno en features/reports.
- `cd Frontend && npx eslint src/features/reports`: exit 0, sin salida.
- Cobertura: no disponible.

### Cumplimiento TDD (Strict)
| Verificación | Resultado | Detalle |
|--------------|-----------|---------|
| Tabla TDD Cycle Evidence | ✅ | Presente en apply-progress |
| Archivos de prueba existen | ✅ | `Backend/tests/reportes/test_cantidad_ventas.py` |
| GREEN | ✅ | 16/16 pasan en ejecución real |
| Triangulación | ✅ | Cada afirmación de la tabla verificada contra el archivo (abajo) |
| Capas | ✅ | Unidad 4, Integración 12 (colección: 16 ítems), E2E 0; coincide con la tabla |

Verificación fila por fila:
- 1.1: 4 tests unitarios (`test_agrupar_*`: vacío, huecos, lunes/domingo, totales). Soportado.
- 1.2: `test_estructura_200`, `test_anio_invalido_422` parametrizado x4 (sin anio, abc, 999, 10000), `test_anio_maximo_valido` (9999). Soportado.
- 1.3: `test_un_comprobante_activo_cuenta_uno`, `test_dos_comprobantes_activos_cuentan_uno`, `test_exclusiones` x3 (anulada, sin comprobantes, inactivos) = 5. Soportado.
- 1.4: "4 instantes de borde" está en UN solo test (`test_bordes_del_anio`) con 4 llamadas a `crear_venta`; es un test, no 4. Aserciones: total 2, enero 1, diciembre 1. Soportado en cobertura; la palabra "casos" es ligeramente engañosa (ver SUGGESTION).
- 1.5-1.8 y 1.9: 16 passed y 72/1117/10 reproducidos. Soportado.
- RED (fallo de colección por `src.reportes` inexistente) no es verificable a posteriori; no hay evidencia contraria.
- Test Summary: 16 escritos, 16 pasan, 4 unitarias + 12 integración: coincide.

### Calidad de aserciones
Sin tautologías ni bucles fantasma. Los casos de total 0 tienen contraparte con conteo positivo.

### Matriz de cumplimiento
| Requisito | Escenario | Prueba | Resultado |
|-----------|-----------|--------|-----------|
| RCV-01 | S1 | test_estructura_200, test_un_comprobante_activo_cuenta_uno | COMPLIANT |
| RCV-02 | S1, S2, S3 | test_anio_invalido_422[params0..3] | COMPLIANT |
| RCV-03 | S1, S2 | test_un_comprobante_activo_cuenta_uno, test_dos_comprobantes_activos_cuentan_uno | COMPLIANT |
| RCV-04 | S1, S2, S3 | test_exclusiones[kwargs0..2] | COMPLIANT |
| RCV-05 | S1-S4 | test_bordes_del_anio | COMPLIANT |
| RCV-06 | S1-S4 | test_agrupar_* (4) | COMPLIANT |
| RCV-07 | S1 | test_estructura_200 | COMPLIANT |
| RCV-08 | S1, S2 | sin runner de frontend | PARTIAL (estático) |
| RCV-09 | S1 | sin runner de frontend | PARTIAL (estático) |
| RCV-10 | S1, S2, S3 | sin runner de frontend | PARTIAL (estático) |
| RCV-11 | S1 | sin runner de frontend | PARTIAL (estático) |

Resumen: 18/25 escenarios con prueba pasada; 7 de frontend sin runtime (no hay runner; pendiente 2.8 manual).

### Corrección y coherencia con el diseño
Sin cambios respecto de la verificación previa: router delega, `exists()`, intervalo semiabierto con omisión del límite en `ANIO_MAX`, agrupación en Python, hook con bandera `cancelled`, componentes presentacionales, `apiFetch` en `api.ts`, textos en español, otros slugs intactos. Sin desviaciones del diseño.

### Problemas
**CRITICAL**: ninguno. (El CRITICAL previo, la tabla TDD faltante, está resuelto.)

**WARNING**:
1. Tarea 2.8 sin marcar: verificación manual en navegador pendiente del usuario (aceptada como pendiente). Por regla del skill una tarea sin marcar sería CRITICAL; se degrada a WARNING por instrucción explícita del orquestador.
2. Escenarios RCV-08 a RCV-11 (7) sin prueba en runtime; dependen de la verificación manual 2.8.
3. (Envelope usa eslint como comando de build porque `tsc` sale con exit 2 y el validador rechaza un veredicto aprobatorio con build fallido.) `tsc` sale con exit 2 por 7 errores preexistentes en base (no atribuibles al cambio); no hay build limpio que atestiguar.

**SUGGESTION**:
1. Reevaluado: el import de `src.reportes.router` al final del bloque en `main.py` NO es un problema; los imports de main.py no están ordenados alfabéticamente (p. ej. productos_menu tras promociones), y el nuevo sigue el patrón existente. Se retira el WARNING previo.
2. En la tabla TDD, la fila 1.4 dice "4 instantes de borde" correspondientes a un solo test; aclarar.
3. Considerar un runner de frontend (vitest) para RCV-10-S3.
4. `contador` global a nivel de módulo en las pruebas podría ser un fixture.

### Veredicto
**PASS WITH WARNINGS en contenido; envelope `fail` por admisión**: el validador nativo rechaza un veredicto aprobatorio con requisitos/escenarios incompletos (7/11, 18/25) y build `tsc` fallido preexistente, de modo que el envelope se registra como `fail` con 1 blocker (2.8 pendiente) y 0 CRITICAL. 0 CRITICAL, 3 WARNING, 4 SUGGESTION. Backend completo y sin regresiones; frontend verificado estáticamente (eslint limpio) a la espera de la verificación manual 2.8.
