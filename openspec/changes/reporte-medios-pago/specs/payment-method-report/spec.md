# Especificación del Reporte de Medios de Pago

Especificación nueva para el cambio `reporte-medios-pago`. El backend expone
`GET /reportes/medios-pago` y el frontend muestra el reporte bajo el slug
`medios-pago`.

## ADDED Requirements

### Requirement: PMR-01 Endpoint y período

El sistema DEBE exponer `GET /reportes/medios-pago` con `desde` y `hasta`
obligatorios en formato `YYYY-MM-DD`. El período DEBE ser inclusivo y filtrarse por
`ComprobantePago.fecha_hora_emision`. Fechas faltantes, inválidas o invertidas DEBEN
producir HTTP 422.

#### Scenario: PMR-01-S1 Consulta válida

- DADO un período válido
- CUANDO se consulta el reporte
- ENTONCES responde 200 con los datos del período

#### Scenario: PMR-01-S2 Fechas faltantes o inválidas

- CUANDO se consulta sin `desde`, sin `hasta` o con una fecha inválida
- ENTONCES responde 422

#### Scenario: PMR-01-S3 Rango invertido

- CUANDO se consulta con `desde` posterior a `hasta`
- ENTONCES responde 422

### Requirement: PMR-02 Universo y exclusiones

Se DEBEN contar los `ComprobantePago` activos cuya `Factura` esté activa y cuya
`fecha_hora_emision` caiga dentro del período. NO se cuentan comprobantes inactivos,
comprobantes de facturas inactivas ni pagos fuera del período.

#### Scenario: PMR-02-S1 Comprobante inactivo

- DADO un comprobante con `activo = false`
- CUANDO se consulta el reporte
- ENTONCES no se cuenta

#### Scenario: PMR-02-S2 Factura inactiva

- DADO un comprobante activo de una factura con `activo = false`
- CUANDO se consulta el reporte
- ENTONCES no se cuenta

#### Scenario: PMR-02-S3 Bordes inclusivos

- DADO un pago a las 00:00 del `desde` y otro a las 23:59:59 del `hasta`
- CUANDO se consulta el reporte
- ENTONCES ambos se cuentan

#### Scenario: PMR-02-S4 Fecha del pago

- DADO una factura emitida fuera del período pero pagada dentro
- CUANDO se consulta el reporte
- ENTONCES el pago se cuenta
- Y un pago fuera del período no se cuenta aunque su factura se haya emitido dentro

### Requirement: PMR-03 Totales y promedio

La respuesta DEBE incluir `total_comprobantes`, `total_importe` e
`importe_promedio`. El importe promedio DEBE ser `total_importe / total_comprobantes`
redondeado a dos decimales, o `0.0` cuando no hay comprobantes.

#### Scenario: PMR-03-S1 Totales del período

- DADO tres comprobantes que suman $180
- CUANDO se consulta el reporte
- ENTONCES `total_comprobantes = 3`, `total_importe = 180.0` e `importe_promedio = 60.0`

#### Scenario: PMR-03-S2 Período vacío

- DADO un período sin comprobantes
- CUANDO se consulta el reporte
- ENTONCES los tres totales son cero y `medios` es una lista vacía

### Requirement: PMR-04 Porcentajes por medio

Cada medio DEBE informar `porcentaje_uso` y `porcentaje_importe`.
`porcentaje_uso` DEBE ser la cantidad de comprobantes del medio sobre el total de
comprobantes del período. `porcentaje_importe` DEBE ser el importe del medio sobre
el total cobrado en el período. Ambos se redondean a dos decimales.

#### Scenario: PMR-04-S1 Distribución por cantidad

- DADO dos pagos en efectivo y uno con tarjeta de débito
- CUANDO se consulta el reporte
- ENTONCES efectivo tiene 66,67 % de uso y débito 33,33 %

#### Scenario: PMR-04-S2 Distribución por importe

- DADO $150 cobrados en efectivo y $30 con tarjeta de débito
- CUANDO se consulta el reporte
- ENTONCES efectivo tiene 83,33 % del importe y débito 16,67 %

#### Scenario: PMR-04-S3 Pago dividido

- DADO una factura pagada 50 % en efectivo y 50 % con tarjeta
- CUANDO se consulta el reporte
- ENTONCES cada medio suma un uso y su importe corresponde a la mitad

### Requirement: PMR-05 Orden y alcance del listado

`medios` DEBE incluir todos los medios con al menos un comprobante en el período, sin
límite Top N. DEBE ordenarse por cantidad de comprobantes descendente, luego por
importe descendente y luego por descripción ascendente. Un medio dado de baja que
tenga comprobantes activos históricos DEBE incluirse.

#### Scenario: PMR-05-S1 Orden por cantidad

- DADO medios con 2 y 1 comprobantes
- CUANDO se consulta el reporte
- ENTONCES el de 2 comprobantes aparece primero

#### Scenario: PMR-05-S2 Desempate

- DADO dos medios con la misma cantidad de comprobantes
- CUANDO se consulta el reporte
- ENTONCES aparece primero el de mayor importe y, si empatan, el de descripción alfabéticamente menor

#### Scenario: PMR-05-S3 Medio inactivo con uso histórico

- DADO un medio con `activo = false` que tiene un comprobante activo en el período
- CUANDO se consulta el reporte
- ENTONCES el medio aparece en el listado

### Requirement: PMR-06 Forma de la respuesta

El cuerpo DEBE tener la forma:

```json
{
  "desde": "YYYY-MM-DD",
  "hasta": "YYYY-MM-DD",
  "total_comprobantes": 0,
  "total_importe": 0.0,
  "importe_promedio": 0.0,
  "medios": [
    {
      "medio_pago_id": 1,
      "descripcion": "Efectivo",
      "cantidad_comprobantes": 0,
      "importe": 0.0,
      "importe_promedio": 0.0,
      "porcentaje_uso": 0.0,
      "porcentaje_importe": 0.0
    }
  ]
}
```

#### Scenario: PMR-06-S1 Estructura

- CUANDO se consulta un período válido
- ENTONCES el cuerpo contiene todas las claves indicadas con los tipos correctos

### Requirement: PMR-07 Visualización del reporte

La pantalla `/reportes/medios-pago` DEBE mostrar, en este orden:

1. Encabezado “Período” con filtros Desde/Hasta.
2. Resumen con comprobantes de pago, importe total e importe promedio.
3. Listado “Top por cantidad de comprobantes” con cantidad y porcentaje de uso.
4. Listado “Top por importe cobrado” con importe y porcentaje del importe.
5. Listado “Top por promedio por comprobante” con cantidad, importe total y promedio
   de cada medio.

El segundo listado DEBE ordenarse por importe descendente, luego por cantidad
descendente y luego por descripción. El tercer listado DEBE ordenarse por promedio
descendente, luego por importe descendente y luego por descripción. La pantalla DEBE
mostrar estados de carga, error y período vacío, y DEBE permitir imprimir el reporte.
El resumen DEBE incluir el rango de fechas para que se vea en la impresión.

#### Scenario: PMR-07-S1 Orden de la pantalla

- CUANDO el administrador abre el reporte
- ENTONCES ve primero el período, luego el resumen y luego los tres listados

#### Scenario: PMR-07-S2 Período vacío

- DADO un período sin comprobantes
- CUANDO termina la consulta
- ENTONCES se muestra un único mensaje de “Sin comprobantes de pago en este período”

#### Scenario: PMR-07-S3 Error de carga

- DADO que la API no responde
- CUANDO se abre el reporte
- ENTONCES se muestra un mensaje de error en español

### Requirement: PMR-08 Script de demo

DEBE existir `scripts/poblar_comparativa_atenciones_comprobantes.py`, basado en el
script de comparativa con atenciones, que agregue comprobantes de pago a las facturas
generadas para poder visualizar el reporte con datos de octubre y noviembre.

#### Scenario: PMR-08-S1 Base poblada con comprobantes

- CUANDO se ejecuta el script para un año
- ENTONCES las facturas activas quedan con comprobantes activos y el reporte devuelve datos para ese período

### Requirement: PMR-09 Promedio por medio

Cada medio DEBE informar `importe_promedio`, calculado como
`importe / cantidad_comprobantes` y redondeado a dos decimales. El reporte DEBE
incluir un listado ordenado por `importe_promedio` descendente, con desempate por
importe descendente y luego descripción ascendente, que muestre la cantidad de
comprobantes, el importe total y el promedio de cada medio.

#### Scenario: PMR-09-S1 Promedio de cada medio

- DADO un medio con dos comprobantes que suman $150
- CUANDO se consulta el reporte
- ENTONCES su `importe_promedio` es 75.0

#### Scenario: PMR-09-S2 Orden por promedio

- DADO medios con promedios distintos
- CUANDO se consulta el reporte
- ENTONCES el listado por promedio muestra primero el de mayor promedio
