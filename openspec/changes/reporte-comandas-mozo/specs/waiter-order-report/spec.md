# Reporte de comandas por mozo

## Requisitos

### Requisito: Consultar comandas por mozo

El sistema DEBE exponer `GET /reportes/comandas-por-mozo` con fechas `desde` y `hasta` obligatorias. El rango es inclusivo; fechas ausentes, inválidas o invertidas DEBEN producir HTTP 422.

#### Escenario: Agrupar actividad del período

- DADO un período válido
- CUANDO se consulta el reporte
- ENTONCES se devuelven, por cada mozo con comandas activas, la cantidad de comandas y la suma de importes de sus facturas activas
- Y las comandas sin factura activa cuentan con importe cero
- Y se excluyen comandas inactivas y fechas fuera del período

### Requisito: Visualizar el reporte

La pantalla `/reportes/comandas-mozo` DEBE permitir seleccionar Desde/Hasta, mostrar totales y el detalle por mozo, informar la carga y los errores, y permitir imprimir/exportar el reporte. El PDF DEBE mostrar el rango de fechas seleccionado.

#### Escenario: Período sin comandas

- DADO un período sin comandas activas asignadas a mozos
- CUANDO termina la consulta
- ENTONCES se informa que no hay comandas en ese período.

#### Escenario: Exportar el período seleccionado

- DADO un rango seleccionado y cargado
- CUANDO se exporta el reporte a PDF
- ENTONCES el PDF muestra las fechas Desde y Hasta del reporte.
