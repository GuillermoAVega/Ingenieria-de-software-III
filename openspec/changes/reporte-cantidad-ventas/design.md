# Diseño: Reporte de cantidad de ventas

## Enfoque técnico

Nuevo paquete `Backend/src/reportes/` sin modelos propios (patrón `secciones`): el router valida `anio` con `Query` y delega en `services.py`, que obtiene solo las fechas de emisión de las ventas del año y las agrupa en Python. El frontend agrega en `features/reports` una sección contenedora para el slug `ventas` (hook + `api.ts` + componentes presentacionales) y deja intacto el resto de `ReportDetailPage`.

## Decisiones de arquitectura

| Tema | Opción elegida | Alternativa descartada | Motivo |
|------|----------------|------------------------|--------|
| Validación de `anio` | `anio: int = Query(ge=ANIO_MIN, le=ANIO_MAX)`; FastAPI responde 422 antes de llamar al servicio | Validar en el servicio con excepción de dominio | Cumple RCV-02 sin código propio ni manejadores |
| Definición de venta | `exists().where(ComprobantePago.factura_id == Factura.id, ComprobantePago.activo.is_(True))` | `JOIN` + `COUNT(DISTINCT)` | Sin multiplicación de filas (RCV-03); mismo estilo que `promociones/services.py` |
| Agrupación | Consulta `select(Factura.fecha_hora_emision)`; `fecha.month` y `fecha.weekday()` en Python | `strftime` en SQL | `%w` de SQLite usa domingo = 0; Python es portable y testeable sin base |
| Rango | `inicio = datetime(anio, 1, 1)`, `fin = datetime(anio + 1, 1, 1)`, `>= inicio AND < fin` | `extract('year')` | Semiabierto exacto (RCV-05) y apto para índices. `datetime(10000, 1, 1)` lanza `ValueError`: con `anio == ANIO_MAX` se omite el límite superior |
| Contrato del servicio | `cantidad_ventas(sesion, anio) -> CantidadVentasRespuesta` que usa la función pura `agrupar_ventas(anio, fechas)` | Devolver diccionarios | Tipado y prueba unitaria directa del completado con ceros |
| Errores | Sin `exceptions.py` ni `MANEJADORES_EXCEPCIONES` | Excepciones de dominio | No hay casos de dominio: solo lectura |
| Ramificación del frontend | `ReportDetailPage` renderiza `<SalesCountReport />` si `report.slug === 'ventas'`; si no, el filtro Desde/Hasta y el contenido actual | Hook condicional dentro de la página | Las reglas de hooks impiden llamarlo condicionalmente; aislar el contenedor mantiene RCV-11 |
| Contenedor | `SalesCountReport.tsx` en la raíz de la feature (consume el hook) | Ubicarlo en `components/` | `components/` no carga datos (Frontend/AGENTS.md) |
| Selector de año | `Select` de `ui/ui.tsx` dentro de `Field` "Año", con los 10 años desde el actual hacia atrás | `Input type="number"` | Evita años inválidos sin validación adicional |
| Gráficos | Un componente `SalesCountChart` reutilizado dos veces con filas `{label, value}` y `BarRow` (`max` = máximo de filas; `BarRow` ya maneja `max = 0`) | Dos componentes distintos | Mismo markup; menos código |

## Flujo de datos

    YearSelector --onChange--> useSalesCountReport (state.year)
         useEffect([year]) -> getSalesCount(year) -> apiFetch('/reportes/ventas/cantidad?anio=YYYY')
            -> router.cantidad_ventas(anio: Query 1000..9999)  [422 si inválido]
            -> services.cantidad_ventas(sesion, anio)
                 SELECT fecha_hora_emision FROM factura
                 WHERE activo AND fecha >= inicio AND fecha < fin AND EXISTS(comprobante activo)
            -> agrupar_ventas(anio, fechas) -> 12 meses + 7 días con ceros
         <- SalesCountResponse -> toChartRows(...) -> SalesCountChart x2

Una respuesta tardía se descarta con la bandera `cancelled` del efecto (RCV-10-S3).

## Cambios de archivos

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `Backend/src/reportes/__init__.py` | Crear | Paquete |
| `Backend/src/reportes/constants.py` | Crear | `PREFIJO = "/reportes"`, `ANIO_MIN = 1000`, `ANIO_MAX = 9999`, `MESES = 12`, `DIAS_SEMANA = 7` |
| `Backend/src/reportes/schemas.py` | Crear | Esquemas de respuesta |
| `Backend/src/reportes/services.py` | Crear | `cantidad_ventas`, `agrupar_ventas` |
| `Backend/src/reportes/router.py` | Crear | `GET /ventas/cantidad` |
| `Backend/src/main.py` | Modificar | `app.include_router(router_reportes)` |
| `Backend/tests/reportes/__init__.py`, `test_cantidad_ventas.py` | Crear | Ver estrategia |
| `Frontend/src/features/reports/types.ts` | Modificar | Tipos de respuesta |
| `Frontend/src/features/reports/api.ts` | Crear | `getSalesCount(year)` |
| `Frontend/src/features/reports/useSalesCountReport.ts` | Crear | Estado único `{ year, data, loading, error }` y `updateYear` |
| `Frontend/src/features/reports/salesLabels.ts` | Crear | `MONTH_LABELS`, `WEEKDAY_LABELS`, `getYearOptions(currentYear)`, `toChartRows(items, labels)` |
| `Frontend/src/features/reports/SalesCountReport.tsx` | Crear | Contenedor: selector, carga, error, dos gráficos |
| `Frontend/src/features/reports/components/YearSelector.tsx` | Crear | `Field` + `Select` |
| `Frontend/src/features/reports/components/SalesCountChart.tsx` | Crear | `Card` + `BarRow` |
| `Frontend/src/features/reports/ReportDetailPage.tsx` | Modificar | Rama `ventas`; resto sin cambios |
| `Frontend/src/features/reports/demo.ts` | Modificar | `ventas`: título "Cantidad de ventas", descripción "Ventas cobradas por mes y por día de la semana en un año." |

## Interfaces

```python
class CantidadPorMes(BaseModel):
    mes: int
    cantidad: int

class CantidadPorDiaSemana(BaseModel):
    dia: int  # 0 = lunes
    cantidad: int

class CantidadVentasRespuesta(BaseModel):
    anio: int
    por_mes: list[CantidadPorMes]
    por_dia_semana: list[CantidadPorDiaSemana]

def agrupar_ventas(anio: int, fechas: Iterable[datetime]) -> CantidadVentasRespuesta: ...
def cantidad_ventas(sesion: Session, anio: int) -> CantidadVentasRespuesta: ...
```

```ts
export type SalesCountResponse = {
  anio: number
  por_mes: { mes: number; cantidad: number }[]
  por_dia_semana: { dia: number; cantidad: number }[]
}
```

Estados visibles: "Cargando reporte…" (`EmptyState`), error con `Alert tone="danger"` y `getErrorMessage`; con error o carga no se renderizan gráficos.

## Estrategia de pruebas

| Capa | Qué | Cómo |
|------|-----|------|
| Unidad | `agrupar_ventas`: lista vacía (12 + 7 ceros), huecos marzo/agosto, lunes y domingo, suma por mes = suma por día | Sin base |
| Integración | 200 y estructura (RCV-07); 422 sin `anio`, `abc`, `999`, `10000`; un comprobante activo cuenta 1; dos comprobantes cuentan 1; factura anulada, sin comprobantes y con comprobantes inactivos no cuentan; bordes 1/1 00:00 y 31/12 23:59:59 cuentan, 1/1 del año siguiente y 31/12 del anterior no | `cliente` + `persistir`; helper local que crea `Comanda` (como `crear_comanda_facturable([])`), `MedioPago`, `Factura` y `ComprobantePago` con `fecha_hora_emision` explícita |
| Frontend | Tipos y lint | `npm run build`, `npx eslint src/features/reports` (sin runner) |

## Matriz de amenazas

N/A: no hay enrutamiento de shell, subprocesos, automatización de VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migración / despliegue

Sin migración ni cambios de esquema. PRs encadenados: 1) backend + tests (~200 líneas); 2) frontend (~220 líneas).

## Preguntas abiertas

Ninguna.
