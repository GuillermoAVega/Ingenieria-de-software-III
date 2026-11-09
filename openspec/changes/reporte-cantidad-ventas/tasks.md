# Tareas: Reporte de cantidad de ventas

## Review Workload Forecast

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | ~420 (PR1 backend 200, PR2 frontend 220) |
| Riesgo de presupuesto de 400 líneas | High (total); cada PR individual Low |
| PRs encadenados recomendados | Sí |
| División sugerida | PR 1 → PR 2 |
| Estrategia de entrega | auto-chain |
| Estrategia de cadena | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Unidades de trabajo sugeridas

| Unidad | Objetivo | PR | Comando de prueba | Harness de ejecución | Límite de rollback |
|--------|----------|----|-------------------|----------------------|--------------------|
| 1 | Endpoint `GET /reportes/ventas/cantidad` | PR 1 | `cd Backend && venv/bin/python -m pytest tests/reportes` | `uvicorn` + `GET /reportes/ventas/cantidad?anio=2025` | `src/reportes/`, `tests/reportes/`, `main.py` |
| 2 | Pantalla `/reportes/ventas` | PR 2 | `cd Frontend && npm run build && npx eslint src/features/reports` | Abrir `/reportes/ventas` en navegador y cambiar el año | `features/reports/` |

## Fase 1: Backend del reporte (PR 1)

Sin migración ni reset de base de datos (no hay modelos nuevos). Helper local de pruebas: crea `Comanda` (como `crear_comanda_facturable([])`), `MedioPago`, `Factura` y `ComprobantePago` con `fecha_hora_emision` explícita.

- [x] 1.1 RED: `Backend/tests/reportes/__init__.py` y `test_cantidad_ventas.py` (unidad): `agrupar_ventas` con lista vacía (12 + 7 ceros), huecos marzo/agosto, lunes y domingo, suma por mes igual a suma por día (RCV-06, RCV-07 parte estructura).
- [x] 1.2 RED: mismo archivo (integración): 200 y estructura; 422 sin `anio`, `abc`, `999` y `10000` (RCV-01, RCV-02, RCV-07).
- [x] 1.3 RED: mismo archivo (integración): un comprobante activo cuenta 1; dos comprobantes activos cuentan 1; factura anulada, sin comprobantes y con comprobantes inactivos no cuentan (RCV-03, RCV-04).
- [x] 1.4 RED: mismo archivo (integración): bordes 1/1 00:00 y 31/12 23:59:59 cuentan; 1/1 del año siguiente y 31/12 del anterior no (RCV-05).
- [x] 1.5 GREEN: crear `Backend/src/reportes/{__init__,constants,schemas}.py` con `PREFIJO`, `ANIO_MIN`, `ANIO_MAX`, `MESES`, `DIAS_SEMANA` y los esquemas `CantidadPorMes`, `CantidadPorDiaSemana`, `CantidadVentasRespuesta` (RCV-07).
- [x] 1.6 GREEN: `Backend/src/reportes/services.py`: `agrupar_ventas` (función pura, completado con ceros, lunes = 0) (RCV-06).
- [x] 1.7 GREEN: mismo archivo: `cantidad_ventas` con `exists()` sobre `ComprobantePago` activo, rango semiabierto `[inicio, fin)` y omisión del límite superior cuando `anio == ANIO_MAX` (RCV-03, RCV-04, RCV-05).
- [x] 1.8 GREEN: `Backend/src/reportes/router.py` con `GET /ventas/cantidad` y `anio: int = Query(ge=ANIO_MIN, le=ANIO_MAX)`; registrar `app.include_router(router_reportes)` en `Backend/src/main.py` (RCV-01, RCV-02).
- [x] 1.9 Ejecutar `cd Backend && venv/bin/python -m pytest` (suite completa).

## Fase 2: Frontend del reporte (PR 2)

Sin runner de pruebas: la verificación es `npm run build` y `npx eslint src/features/reports` desde `Frontend/`, más la verificación manual de la tarea 2.8. Textos visibles en español.

- [x] 2.1 `Frontend/src/features/reports/types.ts`: agregar `SalesCountResponse`. Crear `api.ts` con `getSalesCount(year)` usando `apiFetch('/reportes/ventas/cantidad?anio=YYYY')` (RCV-01, RCV-08).
- [x] 2.2 `Frontend/src/features/reports/salesLabels.ts`: `MONTH_LABELS`, `WEEKDAY_LABELS`, `getYearOptions(currentYear)` (10 años desde el actual hacia atrás) y `toChartRows(items, labels)` (RCV-08, RCV-09).
- [x] 2.3 `Frontend/src/features/reports/useSalesCountReport.ts`: estado único `{ year, data, loading, error }`, `updateYear` y `useEffect([year])` con bandera `cancelled` para descartar respuestas tardías (RCV-08, RCV-10).
- [x] 2.4 `Frontend/src/features/reports/components/YearSelector.tsx` (`Field` "Año" + `Select`) y `components/SalesCountChart.tsx` (`Card` + `BarRow`, `max` = máximo de filas), solo presentacionales (RCV-08, RCV-09).
- [x] 2.5 `Frontend/src/features/reports/SalesCountReport.tsx`: contenedor con selector, "Cargando reporte…" (`EmptyState`), error con `Alert tone="danger"` y `getErrorMessage`, y dos gráficos (meses y días); sin gráficos durante carga o error (RCV-09, RCV-10).
- [x] 2.6 `Frontend/src/features/reports/ReportDetailPage.tsx`: renderizar `<SalesCountReport />` si `report.slug === 'ventas'`; los demás slugs conservan filtros Desde/Hasta y contenido (RCV-11).
- [x] 2.7 `Frontend/src/features/reports/demo.ts`: título "Cantidad de ventas", descripción "Ventas cobradas por mes y por día de la semana en un año."; sin datos de demostración para `ventas` (RCV-09).
- [x] 2.9 Total anual (`Stat` en la tarjeta Período) y porcentaje por fila: `countTotal`, `toChartRows` con `share` y `formatCountWithShare` en `salesLabels.ts`; `BarRow` acepta `display` opcional (RCV-12).
- [ ] 2.8 Verificar `cd Frontend && npm run build && npx eslint src/features/reports`; verificación manual en navegador (año por defecto, cambio de año, error, otro slug sin selector).

## Anexo: cobertura RCV → tarea

| RCV | Tarea | RCV | Tarea |
|-----|-------|-----|-------|
| 01 | 1.2, 1.8 | 07 | 1.1, 1.2, 1.5 |
| 02 | 1.2, 1.8 | 08 | 2.1 a 2.4 |
| 03 | 1.3, 1.7 | 09 | 2.2, 2.4, 2.5, 2.7 |
| 04 | 1.3, 1.7 | 10 | 2.3, 2.5 |
| 05 | 1.4, 1.7 | 11 | 2.6 |
| 06 | 1.1, 1.6 | 12 | 2.9 |
