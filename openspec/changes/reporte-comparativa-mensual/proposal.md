# Propuesta: Reporte comparativo de ventas mensuales

## Intención

Los administradores necesitan comparar la evolución diaria de las ventas de un mes contra el mes anterior. Hoy el índice de reportes es una maqueta y no existe un endpoint que agregue facturación por día.

## Alcance

### Incluido

- Backend: módulo `Backend/src/reportes/` con `GET /reportes/ventas-comparativa`.
- Agregación de `Factura.importe_total` por día para facturas activas.
- Comparación contra el mes anterior con cálculo automático y cambio de año.
- Frontend: reporte `comparativa-mensual` con selector de mes/año y gráfico de dos líneas.
- Dependencia `recharts` y skill `graficos-recharts` para una estética común de gráficos.
- Script `Backend/scripts/poblar_comparativa.py` que genera ventas de octubre y noviembre del año actual hasta la fecha de ejecución.
- Pruebas de agregación, rangos, valores inactivos y validaciones.

### Excluido

- Exportación del reporte.
- Permisos por rol.
- Otros reportes del índice, que siguen en estado de demostración.

## Capacidades

### Nuevas

- `sales-comparison-report`: endpoint y visualización de ventas por día del mes seleccionado contra el mes anterior.

## Enfoque

- Una factura activa cuenta como venta por su `fecha_hora_emision` y `importe_total`.
- La respuesta devuelve dos series completas: una por cada mes, con los días sin ventas en `0`.
- El frontend alinea ambas series por número de día; la línea de un mes más corto termina en su último día real.
- El gráfico usa Recharts con las variables de color y tipografía de `ui.css`.
- Sin parámetros, el backend usa el mes actual mediante la dependencia `obtener_hoy` ya utilizada por las pruebas.

## Áreas afectadas

| Área | Impacto |
|------|---------|
| `Backend/src/reportes/` | Nuevo |
| `Backend/src/main.py` | Registro del router |
| `Backend/tests/reportes/` | Nuevo |
| `Frontend/src/features/reports/` | Reporte real, hook, API y componentes |
| `Frontend/package.json`, `package-lock.json` | Dependencia `recharts` |
| `Frontend/src/ui/ui.css` | Contenedor genérico de gráficos |
| `Backend/scripts/poblar_comparativa.py` | Datos de ejemplo de octubre y noviembre |
| `.opencode/skills/graficos-recharts/` | Skill de estética de gráficos |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Meses con distinta cantidad de días | Media | Series por día real; la gráfica alinea por número de día |
| Datos en cero confundidos con error | Baja | Mostrar la serie completa y la leyenda con nombres legibles |
| Recharts aumenta el bundle | Media | Componente encapsulado; sin otras dependencias nuevas |
