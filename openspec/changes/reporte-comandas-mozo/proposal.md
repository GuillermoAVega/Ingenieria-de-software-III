# Propuesta: Reporte de comandas por mozo

## Intención

Completar `/reportes/comandas-mozo` con un reporte real de cantidad de comandas y ventas facturadas por mozo, filtrable por período.

## Alcance

- Agregar `GET /reportes/comandas-por-mozo?desde=YYYY-MM-DD&hasta=YYYY-MM-DD`.
- Agrupar comandas activas por mozo y fecha; sumar facturas activas asociadas.
- Mostrar el resumen y el detalle en el frontend, con filtros, estados de carga/error y exportación para imprimir.
- Probar agregación, límites de fecha y validación del período.

## Definición

- Se incluyen comandas activas con mozo asignado cuya fecha esté dentro del rango inclusivo.
- Cada comanda cuenta aunque no tenga factura activa; en ese caso no aporta importe de ventas.
- Se suman los importes de facturas activas asociadas a las comandas incluidas.
- Se incluyen en la respuesta solo mozos con al menos una comanda en el período.

## Capacidades

### Nuevas

- `waiter-order-report`: consulta y visualización del reporte de comandas y ventas por mozo.

### Modificadas

- `/reportes/comandas-mozo`: se reemplaza el estado de preparación por datos del backend.
