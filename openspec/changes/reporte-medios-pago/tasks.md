# Tareas: Reporte de medios de pago

## Fase 1: Backend

Sin migración ni reset de base de datos. Los tests usan el motor SQLite en memoria y
crean Sector, Mesa, Mozo, Comanda, Factura, MedioPago y ComprobantePago.

- [x] 1.1 RED: crear `Backend/tests/reportes/test_medios_pago.py` con el fixture de pagos y los casos de estructura, totales, promedio, porcentajes, orden, exclusiones, bordes y validaciones (PMR-01 a PMR-06).
- [x] 1.2 RED: agregar casos de pago dividido, medio inactivo con uso histórico y fecha de pago distinta de la fecha de factura.
- [x] 1.3 GREEN: agregar `MedioPagoUsoItem` y `MediosPagoRespuesta` en `Backend/src/reportes/schemas.py`.
- [x] 1.4 GREEN: implementar `medios_pago()` en `Backend/src/reportes/services.py` con la consulta agrupada, totales, promedio y porcentajes.
- [x] 1.5 GREEN: agregar `GET /reportes/medios-pago` en `Backend/src/reportes/router.py` con validación de período.
- [x] 1.6 Ejecutar `cd Backend && venv/bin/python -m pytest tests/reportes/test_medios_pago.py`.

## Fase 2: Frontend

Sin runner de pruebas: la verificación es `npm run build` y `npx eslint src/features/reports`.

- [x] 2.1 `Frontend/src/features/reports/types.ts`: agregar `PaymentMethodUsageRow` y `PaymentMethodReport`.
- [x] 2.2 `Frontend/src/features/reports/api.ts`: agregar `getPaymentMethodReport(desde, hasta)`.
- [x] 2.3 `Frontend/src/features/reports/format.ts`: agregar `formatPercentage`.
- [x] 2.4 `Frontend/src/features/reports/paymentMethodRanking.ts`: agregar `sortByImporte` con desempate por cantidad y descripción.
- [x] 2.5 `Frontend/src/features/reports/usePaymentMethodReport.ts`: estado único, período inicial, validación, carga con bandera de cancelación y listados derivados.
- [x] 2.6 `Frontend/src/features/reports/PaymentMethodReport.tsx`: período, resumen de tres totales, listado por cantidad, listado por importe, carga, error y vacío.
- [x] 2.7 `Frontend/src/features/reports/ReportDetailPage.tsx`: renderizar `PaymentMethodReport` para `medios-pago` y habilitar la exportación.
- [x] 2.8 `Frontend/src/features/reports/demo.ts`: actualizar título y descripción del slug `medios-pago`.
- [x] 2.9 Verificar `cd Frontend && npm run build && npx eslint src/features/reports`.
- [x] 2.10 Agregar `importe_promedio` por medio en el backend y el listado “Top por promedio por comprobante” con cantidad, importe total y promedio.

## Fase 3: Script de demo

- [x] 3.1 RED: crear `Backend/tests/test_poblar_comparativa_atenciones_comprobantes.py` y verificar que las facturas activas quedan con comprobantes y que el reporte devuelve datos.
- [x] 3.2 GREEN: crear `Backend/scripts/poblar_comparativa_atenciones_comprobantes.py` reutilizando `poblar_comparativa_atenciones` y `_cobrar`.
- [x] 3.3 Ejecutar el test del script y una prueba manual con una base descartable.

## Anexo: cobertura PMR → tarea

| PMR | Tareas |
|-----|--------|
| 01 | 1.1, 1.5 |
| 02 | 1.1, 1.2, 1.4 |
| 03 | 1.1, 1.4 |
| 04 | 1.1, 1.2, 1.4 |
| 05 | 1.1, 1.2, 1.4 |
| 06 | 1.1, 1.3, 1.4 |
| 07 | 2.1 a 2.8, 2.10 |
| 08 | 3.1, 3.2 |
| 09 | 1.4, 2.10 |
