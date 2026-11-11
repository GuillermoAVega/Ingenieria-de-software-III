# Propuesta: Reporte de medios de pago

## Intención

Completar `/reportes/medios-pago` con un reporte real que muestre, para un período,
cuántos comprobantes de pago se emitieron, su importe total y promedio, y cómo se
distribuyen por medio de pago. El administrador debe poder identificar tanto los
medios más usados como los que más importe cobraron.

## Alcance

### Incluido

- `GET /reportes/medios-pago?desde=YYYY-MM-DD&hasta=YYYY-MM-DD`.
- Resumen del período: total de comprobantes, importe total e importe promedio.
- Listado de todos los medios con uso, ordenado por cantidad de comprobantes, con
  porcentaje de uso.
- Listado de todos los medios con uso, ordenado por importe cobrado, con porcentaje
  del importe.
- Listado de todos los medios con uso, ordenado por promedio cobrado por comprobante,
  con cantidad de comprobantes, importe total y promedio.
- Visualización en `/reportes/medios-pago` con filtros Desde/Hasta, estados de carga,
  error y período vacío, e impresión del reporte.
- Tests de backend para agregación, totales, porcentajes, exclusiones, bordes y
  validaciones.
- Script de demo `scripts/poblar_comparativa_atenciones_comprobantes.py`, basado en
  `scripts/poblar_comparativa_atenciones.py`, que agrega comprobantes de pago.

### Excluido

- Modelos, tablas o migraciones nuevas.
- Dependencias nuevas.
- Límite Top N: se muestran todos los medios con uso en el período.
- Medios sin comprobantes en el período.
- Refactors opcionales de validación de período y helpers de fechas del frontend.

## Definición

- **Uso:** cada `ComprobantePago` activo cuenta como un uso. Un pago dividido entre
  dos medios suma un uso a cada uno.
- **Período:** inclusivo, filtrado por `ComprobantePago.fecha_hora_emision`.
- **Universo:** comprobantes activos cuya `Factura` también esté activa.
- **Porcentaje de uso:** `cantidad_comprobantes / total_comprobantes * 100`.
- **Porcentaje del importe:** `importe / total_importe * 100`.
- **Importe promedio:** `total_importe / total_comprobantes`, o `0.0` sin pagos.
- Los importes y porcentajes se redondean a dos decimales.
- Se incluyen medios dados de baja que tengan comprobantes activos históricos.
- No se cuentan clientes únicos: el pago no guarda el cliente.

## Capacidades

### Nuevas

- `payment-method-report`: contrato del endpoint, definición de uso, totales,
  porcentajes, orden y visualización del reporte de medios de pago.

### Modificadas

- `/reportes/medios-pago`: se reemplaza el estado de preparación por datos reales.

## Enfoque

- Router delgado: valida `desde`/`hasta` y delega en `services.py`.
- Servicio: una consulta agrupada por `MedioPago` con `join` a `Factura`, filtros de
  actividad y rango semiabierto `[desde 00:00, hasta+1 00:00)`.
- Los totales y porcentajes se calculan en el servicio para que el contrato sea
  explícito y testeable.
- Frontend: hook con estado único, llamadas por `apiFetch`, un componente por archivo,
  textos en español y `BarRow` para visualizar porcentajes.
- El segundo listado se ordena en el frontend con una función pura sobre la misma
  respuesta, sin duplicar datos en la API.

## Áreas afectadas

| Área | Impacto |
|------|---------|
| `Backend/src/reportes/{schemas,services,router}.py` | Modificado |
| `Backend/tests/reportes/test_medios_pago.py` | Nuevo |
| `Backend/scripts/poblar_comparativa_atenciones_comprobantes.py` | Nuevo |
| `Backend/tests/test_poblar_comparativa_atenciones_comprobantes.py` | Nuevo |
| `Frontend/src/features/reports/` | Modificado y nuevos hook/componente/helper |
| `openspec/changes/reporte-medios-pago/` | Nuevo |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Doble conteo por pagos divididos | Media | Cada comprobante cuenta como un uso; se documenta y se prueba |
| Diferencias por redondeo de porcentajes | Baja | Redondeo a dos decimales y tests con valores exactos |
| Período vacío o importes en cero | Baja | Totales y promedio en cero, listados vacíos |
| Reporte sin datos en la demo | Media | Script específico que agrega comprobantes a la comparativa |

## Plan de reversión

Revertir los commits del cambio. No hay cambios de esquema ni migraciones.

## Criterios de éxito

- [x] `cd Backend && venv/bin/python -m pytest tests/reportes tests/test_poblar_comparativa_atenciones_comprobantes.py` pasa.
- [x] El endpoint devuelve totales, promedio, ambos porcentajes y todos los medios con uso.
- [x] `/reportes/medios-pago` muestra período, resumen y los dos listados.
- [x] `cd Frontend && npm run build && npx eslint src/features/reports` pasa.
- [x] El script de demo permite ver el reporte con datos de octubre/noviembre.
