# Especificación de Reportes de Ventas

Especificación nueva para el cambio `reporte-cantidad-ventas`. El módulo vive en `Backend/src/reportes/` (sin modelos propios; consulta `Factura` y `ComprobantePago`) y se expone bajo `/reportes`. La pantalla `/reportes/ventas` de `Frontend/src/features/reports` consume el endpoint. Los textos visibles están en español.

## ADDED Requirements

### Requirement: RCV-01 Endpoint de cantidad de ventas
`GET /reportes/ventas/cantidad?anio=YYYY` DEBE devolver 200 con la cantidad de ventas del año indicado agrupada por mes y por día de la semana. El router DEBE limitarse a validar el parámetro y delegar el cálculo en un servicio.

#### Scenario: RCV-01-S1 Consulta válida
- DADO un año con ventas registradas
- CUANDO un cliente consulta `GET /reportes/ventas/cantidad?anio=2025`
- ENTONCES 200 y el cuerpo contiene las cantidades por mes y por día de la semana de 2025

### Requirement: RCV-02 Validación del parámetro anio
`anio` es obligatorio y DEBE ser un entero de cuatro dígitos (1000 a 9999). Si falta, no es entero o está fuera de rango, DEBE responder 422 y no consultar datos.

#### Scenario: RCV-02-S1 Año faltante
- CUANDO un cliente consulta sin `anio`
- ENTONCES 422

#### Scenario: RCV-02-S2 Año no numérico
- CUANDO un cliente consulta con `anio=abc`
- ENTONCES 422

#### Scenario: RCV-02-S3 Año fuera de rango
- CUANDO un cliente consulta con `anio=999` o `anio=10000`
- ENTONCES 422 en cada caso

### Requirement: RCV-03 Definición de venta
Una venta es una `Factura` con `activo = true` que tiene al menos un `ComprobantePago` con `activo = true`. Cada factura DEBE contarse una sola vez, aun cuando tenga varios comprobantes activos (verificación de existencia, no unión que multiplique filas). No se consideran importes ni montos.

#### Scenario: RCV-03-S1 Factura con un comprobante activo
- DADO una factura activa con un comprobante activo emitida en el año consultado
- CUANDO se consulta el reporte
- ENTONCES se cuenta como una venta

#### Scenario: RCV-03-S2 Sin doble conteo
- DADO una factura activa con dos comprobantes activos
- CUANDO se consulta el reporte
- ENTONCES se cuenta exactamente una venta

### Requirement: RCV-04 Exclusiones
DEBEN excluirse del conteo las facturas con `activo = false` y las facturas sin ningún comprobante activo (sin comprobantes, o con todos inactivos).

#### Scenario: RCV-04-S1 Factura anulada
- DADO una factura con `activo = false` que tiene un comprobante activo
- CUANDO se consulta el reporte
- ENTONCES no se cuenta

#### Scenario: RCV-04-S2 Sin comprobante
- DADO una factura activa sin comprobantes
- CUANDO se consulta el reporte
- ENTONCES no se cuenta

#### Scenario: RCV-04-S3 Comprobantes inactivos
- DADO una factura activa cuyos comprobantes tienen todos `activo = false`
- CUANDO se consulta el reporte
- ENTONCES no se cuenta

### Requirement: RCV-05 Rango del año y fecha de referencia
Se DEBEN contar las facturas cuyo `fecha_hora_emision` esté en el intervalo semiabierto `[1/1/anio 00:00, 1/1/anio+1 00:00)`, usando la hora local almacenada sin conversión de zona horaria. El mes y el día de la semana se obtienen de esa misma fecha.

#### Scenario: RCV-05-S1 Primer instante del año
- DADO una venta emitida el 1/1/2025 a las 00:00:00
- CUANDO se consulta `anio=2025`
- ENTONCES se cuenta en enero

#### Scenario: RCV-05-S2 Último instante del año
- DADO una venta emitida el 31/12/2025 a las 23:59:59
- CUANDO se consulta `anio=2025`
- ENTONCES se cuenta en diciembre

#### Scenario: RCV-05-S3 Instante del año siguiente
- DADO una venta emitida el 1/1/2026 a las 00:00:00
- CUANDO se consulta `anio=2025`
- ENTONCES no se cuenta

#### Scenario: RCV-05-S4 Instante del año anterior
- DADO una venta emitida el 31/12/2024 a las 23:59:59
- CUANDO se consulta `anio=2025`
- ENTONCES no se cuenta

### Requirement: RCV-06 Agrupación y completado con cero
La respuesta DEBE incluir siempre 12 meses (enero a diciembre, en ese orden) y 7 días de la semana (lunes a domingo, en ese orden), con cantidad `0` para los períodos sin ventas. Con un año sin ventas, las 12 y 7 entradas siguen presentes con cantidad `0`. El lunes es el primer día de la semana.

#### Scenario: RCV-06-S1 Año sin ventas
- DADO un año sin ventas
- CUANDO se consulta el reporte
- ENTONCES hay 12 meses y 7 días, todos con cantidad `0`

#### Scenario: RCV-06-S2 Meses con huecos
- DADO ventas solo en marzo y en agosto
- CUANDO se consulta el reporte
- ENTONCES los demás meses figuran con `0` y el orden es enero a diciembre

#### Scenario: RCV-06-S3 Día de la semana
- DADO una venta emitida un domingo y otra un lunes
- CUANDO se consulta el reporte
- ENTONCES el lunes es la primera entrada con 1, el domingo la séptima con 1 y el resto `0`

#### Scenario: RCV-06-S4 Consistencia de totales
- DADO cualquier conjunto de ventas del año
- CUANDO se consulta el reporte
- ENTONCES la suma por mes es igual a la suma por día de la semana

### Requirement: RCV-07 Forma de la respuesta
El cuerpo DEBE tener la forma `{ "anio": int, "por_mes": [{ "mes": 1..12, "cantidad": int }], "por_dia_semana": [{ "dia": 0..6, "cantidad": int }] }`, donde `dia = 0` es lunes y `dia = 6` es domingo. `por_mes` tiene exactamente 12 elementos y `por_dia_semana` exactamente 7, ordenados de forma ascendente por `mes` y `dia`. Las etiquetas en español se resuelven en el frontend.

#### Scenario: RCV-07-S1 Estructura
- CUANDO se consulta un año válido
- ENTONCES `anio` coincide con el consultado, `por_mes` tiene 12 elementos con `mes` 1 a 12 y `por_dia_semana` tiene 7 con `dia` 0 a 6

### Requirement: RCV-08 Selector de año en el frontend
En `/reportes/ventas` la pantalla DEBE mostrar un selector de año cuyo valor inicial es el año actual y que reemplaza los filtros Desde/Hasta solo para este slug. Al cambiar el año DEBE consultarse de nuevo el endpoint con el año elegido.

#### Scenario: RCV-08-S1 Año por defecto
- CUANDO el usuario abre `/reportes/ventas`
- ENTONCES el selector muestra el año actual y se consulta con ese año

#### Scenario: RCV-08-S2 Cambio de año
- CUANDO el usuario elige otro año
- ENTONCES se consulta el endpoint con el nuevo `anio` y los gráficos se actualizan

### Requirement: RCV-09 Gráficos
La pantalla DEBE mostrar dos gráficos con `BarRow`: cantidad de ventas por mes (12 filas, enero a diciembre) y por día de la semana (7 filas, lunes a domingo), con etiquetas en español. El título y la descripción del slug `ventas` DEBEN reflejar el reporte de cantidad de ventas. NO DEBE haber datos de demostración para este slug.

#### Scenario: RCV-09-S1 Gráficos con datos
- DADO una respuesta exitosa
- CUANDO se renderiza la pantalla
- ENTONCES se ven 12 filas de meses con nombres en español y 7 filas de días de lunes a domingo, cada una con su cantidad

### Requirement: RCV-10 Estados de carga y error
Mientras la consulta esté en curso la pantalla DEBE mostrar un estado de carga en español. Si la consulta falla, DEBE mostrar un mensaje de error en español y no mostrar gráficos obsoletos. Una respuesta de una consulta anterior (cambio de año o desmontaje) NO DEBE sobrescribir el estado vigente.

#### Scenario: RCV-10-S1 Cargando
- CUANDO la consulta está pendiente
- ENTONCES se muestra el indicador de carga

#### Scenario: RCV-10-S2 Error
- CUANDO el backend responde con error o la red falla
- ENTONCES se muestra el mensaje de error y no los gráficos

#### Scenario: RCV-10-S3 Respuesta tardía descartada
- DADO una consulta cancelada por un cambio de año
- CUANDO llega su respuesta tardía
- ENTONCES se ignora

### Requirement: RCV-11 Otros reportes sin cambios
Los demás slugs de reportes DEBEN conservar su comportamiento actual, incluidos los filtros Desde/Hasta y sus datos.

#### Scenario: RCV-11-S1 Otro slug
- CUANDO el usuario abre un slug distinto de `ventas`
- ENTONCES ve los filtros Desde/Hasta y el contenido existente, sin selector de año

### Requirement: RCV-12 Total anual y porcentajes
La pantalla DEBE mostrar la cantidad total de ventas del año seleccionado (suma de los 12 meses). Cada fila de ambos gráficos DEBE mostrar su cantidad seguida, entre paréntesis, del porcentaje que representa sobre ese total, con hasta un decimal en formato `es-AR`. Si el total es 0, el porcentaje DEBE mostrarse como 0 %.

#### Scenario: RCV-12-S1 Total y porcentajes con ventas
- DADO un año con 200 ventas, 50 de ellas en julio
- CUANDO se renderiza la pantalla
- ENTONCES se ve "Total de ventas en <año>" con el valor 200 y la fila de julio muestra "50 (25 %)"

#### Scenario: RCV-12-S2 Año sin ventas
- DADO un año sin ventas
- CUANDO se renderiza la pantalla
- ENTONCES el total es 0 y cada fila muestra "0 (0 %)"

### Requirement: RCV-13 Exportar a PDF
El botón "Exportar PDF" DEBE abrir el diálogo de impresión del navegador (`window.print()`), desde el que se guarda el PDF. La impresión DEBE ocultar la navegación, el botón y el selector de año. DEBE mostrar un resumen del año que solo aparece al imprimir, con la fecha de emisión y cuatro indicadores: total de ventas, promedio mensual, mes con más ventas y día con más ventas (cantidad y porcentaje; ante empate, el primero; "—" si no hay ventas). Debajo de los indicadores DEBE explicar qué se cuenta como venta. Las barras DEBEN imprimirse con color y el título del documento DEBE ser "Cantidad de ventas <año>".

#### Scenario: RCV-13-S1 Exportar un año con ventas
- DADO el reporte de 2025 cargado
- CUANDO el usuario presiona "Exportar PDF"
- ENTONCES se abre el diálogo de impresión con el título "Cantidad de ventas 2025", el resumen con los cuatro indicadores y los dos gráficos, sin la navegación ni el selector de año

#### Scenario: RCV-13-S2 Resumen de un año sin ventas
- DADO un año sin ventas
- CUANDO se imprime el reporte
- ENTONCES el total es 0 y el mes y el día con más ventas muestran "—" con la leyenda "Sin ventas"
