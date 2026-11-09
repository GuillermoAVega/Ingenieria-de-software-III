# Especificación del Reporte Comparativo de Ventas

Especificación nueva para el cambio `reporte-comparativa-mensual`. El backend expone `GET /reportes/ventas-comparativa` y el frontend muestra el reporte bajo el slug `comparativa-mensual`.

## ADDED Requirements

### Requirement: Ventas por día de un mes
El sistema DEBE devolver las ventas diarias de un mes agrupadas por la fecha de emisión de las facturas. Una venta DEBE contarse cuando la factura está activa y su `fecha_hora_emision` cae dentro del mes consultado. El importe del día DEBE ser la suma de `importe_total` de esas facturas, redondeada a dos decimales. Los días sin ventas DEBEN devolverse con importe `0`.

#### Scenario: SCR-01 Suma de facturas del mismo día
- DADO dos facturas activas emitidas el 2 de junio por $100 y $75,50
- CUANDO se consulta junio de 2026
- ENTONCES el día 2 devuelve $175,50

#### Scenario: SCR-02 Facturas inactivas excluidas
- DADO una factura inactiva emitida el 2 de junio por $999
- CUANDO se consulta junio de 2026
- ENTONCES el día 2 no incluye ese importe

#### Scenario: SCR-03 Día sin ventas
- DADO un mes sin facturas emitidas el día 3
- CUANDO se consulta ese mes
- ENTONCES el día 3 devuelve importe `0`

### Requirement: Comparación con el mes anterior
La respuesta DEBE incluir una segunda serie con las ventas del mes inmediatamente anterior. Si el mes consultado es enero, el mes anterior DEBE ser diciembre del año anterior. Cada serie DEBE contener solo los días reales de su mes.

#### Scenario: SCR-04 Comparación normal
- CUANDO se consulta octubre de 2026
- ENTONCES `anio_anterior = 2026`, `mes_anterior = 9` y se devuelven las ventas diarias de septiembre

#### Scenario: SCR-05 Cambio de año
- CUANDO se consulta enero de 2026
- ENTONCES `anio_anterior = 2025`, `mes_anterior = 12` y se devuelven las ventas diarias de diciembre de 2025

### Requirement: Período por defecto y validación
Sin parámetros `anio` ni `mes`, el endpoint DEBE usar el mes actual. El parámetro `mes` DEBE estar entre 1 y 12 y `anio` dentro del rango permitido. Valores fuera de rango DEBEN devolver `422`.

#### Scenario: SCR-06 Mes actual por defecto
- DADO que la fecha actual es junio de 2026
- CUANDO se consulta el endpoint sin parámetros
- ENTONCES devuelve `anio = 2026` y `mes = 6`

#### Scenario: SCR-07 Mes inválido
- CUANDO se consulta con `mes = 13`
- ENTONCES devuelve `422`

### Requirement: Visualización comparativa
El reporte `comparativa-mensual` DEBE permitir elegir mes y año. DEBE mostrar un gráfico de dos líneas con las ventas por día en pesos, una para el mes seleccionado y otra para el mes anterior. La línea del mes anterior DEBE ser discontinua. El eje X DEBE cubrir todos los días de los meses comparados. La serie del mes seleccionado DEBE cortarse en la fecha actual, mientras que la del mes anterior DEBE continuar hasta el último día de su mes cuando ese mes ya transcurrió. Por encima del gráfico DEBEN mostrarse los totales acumulados de ambos meses hasta el mismo día de corte. La interfaz DEBE mostrar estados de carga y error en español.

#### Scenario: SCR-08 Gráfico con el mes seleccionado
- DADO el reporte abierto en el mes de junio de 2026
- CUANDO el administrador cambia a mayo de 2026
- ENTONCES solicita la comparativa de mayo de 2026 contra abril de 2026 y actualiza el gráfico

#### Scenario: SCR-09 Error de carga
- DADO que la API de reportes no responde
- CUANDO se abre el reporte
- ENTONCES se muestra un mensaje de error en español y no un gráfico vacío

#### Scenario: SCR-10 Totales con el mismo día de corte
- DADO que hoy es 9 de noviembre de 2026 y se muestra la comparativa de noviembre contra octubre
- CUANDO se calculan los totales
- ENTONCES el total de noviembre suma del 1 al 9 de noviembre
- Y el total de octubre suma del 1 al 9 de octubre
- Y el gráfico muestra la línea de octubre como discontinua

#### Scenario: SCR-11 Corte solo en la serie del mes actual
- DADO que hoy es 9 de noviembre de 2026 y se muestra la comparativa de noviembre contra octubre
- CUANDO se renderiza el gráfico
- ENTONCES el eje X llega hasta el día 31
- Y la línea de noviembre termina en el día 9
- Y la línea de octubre continúa hasta el día 31
