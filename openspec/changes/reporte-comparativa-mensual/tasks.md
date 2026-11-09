# Tareas: Reporte comparativo de ventas mensuales

## Fase 1: Estética de gráficos

- [x] 1.1 Crear `.opencode/skills/graficos-recharts/SKILL.md` con la paleta, tipografía, ejes, tooltip, leyenda y accesibilidad.
- [x] 1.2 Dejar la skill en formato Agent Skills estándar, sin dependencias de OpenCode, y referenciarla desde `AGENTS.md`.
- [x] 1.3 Agregar `recharts` a `Frontend/package.json` y al lockfile.
- [x] 1.4 Agregar el contenedor `.chart-wrap` a `Frontend/src/ui/ui.css`.

## Fase 2: Backend

- [x] 2.1 Crear `Backend/src/reportes/` con `constants`, `schemas`, `services` y `router`.
- [x] 2.2 Agregar `GET /reportes/ventas-comparativa` con parámetros opcionales y validación.
- [x] 2.3 Agregar el router en `Backend/src/main.py`.
- [x] 2.4 Crear `Backend/tests/reportes/test_ventas_comparativa.py`.
- [x] 2.5 Verificar con `python -m pytest tests/reportes -q`.

## Fase 3: Frontend

- [x] 3.1 Agregar el slug y los tipos de la comparativa en `features/reports/types.ts`.
- [x] 3.2 Crear `features/reports/api.ts` y `useSalesComparison.ts`.
- [x] 3.3 Crear `MonthYearFilter`, `SalesComparisonChart`, `SalesComparisonTotals` y `SalesComparisonReport`.
- [x] 3.4 Integrar el reporte en `ReportDetailPage` y agregar la tarjeta en `demo.ts`.
- [x] 3.5 Marcar la línea del mes anterior como discontinua, cortar solo la serie del mes actual en la fecha actual y mostrar los totales acumulados al mismo día de corte, con el total completo del mes anterior como dato secundario.
- [x] 3.6 Verificar tipos de la feature y ejecutar `npx eslint src/features/reports`.

## Fase 4: Datos de ejemplo

- [x] 4.1 Crear `Backend/scripts/poblar_comparativa.py` con ventas para cada día de octubre y noviembre del año actual, solo hasta la fecha de ejecución.
- [x] 4.2 Reutilizar `poblar_base` y el motor real de facturación para que las facturas sean coherentes.
- [x] 4.3 Documentar el uso y la advertencia de recreación de la base.

## Fase 5: Verificación

- [x] 5.1 `npx vite build` sin errores de empaquetado.
- [ ] 5.2 `npm run build` completo: bloqueado por errores de tipado preexistentes en `menu-view`, `orders` y `products`.
- [ ] 5.3 `pytest` completo: los tests del reporte pasan; la suite mantiene fallos preexistentes en promociones y facturación.
