# Propuesta: Reporte de cantidad de ventas

## Intención

La pantalla `/reportes/ventas` muestra hoy datos de demostración. Se necesita un reporte real de la cantidad de ventas por mes y por día de la semana para un año, calculado por el backend a partir de facturas cobradas.

## Alcance

### Incluido
- Módulo `Backend/src/reportes/` (`constants.py`, `schemas.py`, `services.py`, `router.py`; sin modelos propios, solo consulta `Factura` y `ComprobantePago`), registrado en `main.py`.
- `GET /reportes/ventas/cantidad?anio=YYYY`: `anio` obligatorio, 422 si es inválido.
- Respuesta con 12 meses (enero a diciembre) y 7 días (lunes a domingo), completados con cero.
- Tests en `Backend/tests/reportes/`.
- Frontend `features/reports`, slug `ventas`: selector de año (por defecto el actual, reemplaza Desde/Hasta solo en este slug), dos gráficos con `BarRow`, `api.ts`, hook y componentes presentacionales; título y descripción de `ventas` actualizados.

### Excluido
- Exportación, otros reportes (otros slugs sin cambios), importes o montos, nuevas dependencias.

## Capacidades

### Nuevas
- `sales-reports`: cantidad de ventas por mes y por día de la semana filtrada por año (contrato del endpoint, definición de venta, agrupación, completado con cero) y su visualización en `/reportes/ventas`.

### Modificadas
- Ninguna.

## Enfoque

- Venta = `Factura` con `activo = true` y al menos un `ComprobantePago` con `activo = true`; se cuenta cada factura una sola vez mediante `EXISTS`.
- Filtro por rango `[1/1/anio, 1/1/anio+1)` sobre `fecha_hora_emision` (hora local sin zona); se obtienen solo las fechas y se agrupa en Python (`month`, `weekday()` con lunes = 0), portable y testeable.
- Router delgado; la regla de negocio vive en `services.py`.
- Frontend: página coordina, hook con estado único y bandera de cancelación, llamadas vía `apiFetch`, un componente por archivo, textos en español.

## Áreas afectadas

| Área | Impacto |
|------|---------|
| `Backend/src/reportes/` | Nuevo |
| `Backend/src/main.py` | Registro del router |
| `Backend/tests/reportes/` | Nuevo |
| `Frontend/src/features/reports/` | Modificado (`ReportDetailPage.tsx`, `demo.ts`, `types.ts`) y nuevos `api.ts`, hook, `components/` |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Doble conteo por varios comprobantes | Media | `EXISTS` y test con dos comprobantes |
| Facturas cerca de medianoche asignadas a otro día | Baja | Se usa la hora local almacenada sin conversión |
| Volumen alto al agrupar en Python | Baja | Solo se consulta la columna de fecha del año filtrado |
| Superar 400 líneas | Media | PRs encadenados: backend; frontend |

## Plan de reversión

Revertir los commits del cambio; se elimina `Backend/src/reportes/`, su registro en `main.py` y el slug `ventas` vuelve a la demostración. No hay cambios de esquema.

## Dependencias

- Ninguna externa.

## Criterios de éxito

- [ ] `cd Backend && python -m pytest` pasa con los tests de `reportes`.
- [ ] El endpoint devuelve 12 meses y 7 días con ceros y excluye facturas anuladas o sin comprobante activo.
- [ ] `/reportes/ventas` muestra ambos gráficos para el año elegido.
- [ ] `npm run build` y `npx eslint src/features/reports` pasan en Frontend.
