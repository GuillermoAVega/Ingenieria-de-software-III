from calendar import monthrange
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import Factura
from src.reportes.schemas import PuntoVentaDia, VentasComparativaRespuesta
from collections import Counter
from collections.abc import Iterable
from datetime import datetime

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from src.models import ComprobantePago, Factura
from src.reportes.constants import ANIO_MAX, DIAS_SEMANA, MESES
from src.reportes.schemas import (
    CantidadPorDiaSemana,
    CantidadPorMes,
    CantidadVentasRespuesta,
)



def _mes_anterior(anio: int, mes: int) -> tuple[int, int]:
    return (anio - 1, 12) if mes == 1 else (anio, mes - 1)


def _siguiente_mes(anio: int, mes: int) -> tuple[int, int]:
    return (anio + 1, 1) if mes == 12 else (anio, mes + 1)


def _ventas_por_dia(sesion: Session, anio: int, mes: int) -> list[PuntoVentaDia]:
    """Ventas de facturas activas por día, con los días sin ventas en cero."""
    _, cantidad_dias = monthrange(anio, mes)
    inicio = datetime(anio, mes, 1)
    anio_siguiente, mes_siguiente = _siguiente_mes(anio, mes)
    fin = datetime(anio_siguiente, mes_siguiente, 1)

    fecha = func.date(Factura.fecha_hora_emision)
    filas = sesion.execute(
        select(fecha, func.sum(Factura.importe_total))
        .where(
            Factura.activo.is_(True),
            Factura.fecha_hora_emision >= inicio,
            Factura.fecha_hora_emision < fin,
        )
        .group_by(fecha)
    ).all()

    importes = {
        int(str(fecha_fila)[-2:]): round(float(importe or 0), 2)
        for fecha_fila, importe in filas
    }
    return [
        PuntoVentaDia(dia=dia, importe=importes.get(dia, 0.0))
        for dia in range(1, cantidad_dias + 1)
    ]


def ventas_comparativa(
    sesion: Session, anio: int, mes: int
) -> VentasComparativaRespuesta:
    anio_anterior, mes_anterior = _mes_anterior(anio, mes)
    return VentasComparativaRespuesta(
        anio=anio,
        mes=mes,
        anio_anterior=anio_anterior,
        mes_anterior=mes_anterior,
        actual=_ventas_por_dia(sesion, anio, mes),
        anterior=_ventas_por_dia(sesion, anio_anterior, mes_anterior),
    )


"""Consultas de reportes de ventas."""


def agrupar_ventas(anio: int, fechas: Iterable[datetime]) -> CantidadVentasRespuesta:
    """Cuenta las fechas por mes y por día de la semana (lunes = 0), completando con ceros."""
    fechas = list(fechas)
    por_mes = Counter(fecha.month for fecha in fechas)
    por_dia = Counter(fecha.weekday() for fecha in fechas)
    return CantidadVentasRespuesta(
        anio=anio,
        por_mes=[CantidadPorMes(mes=m, cantidad=por_mes[m]) for m in range(1, MESES + 1)],
        por_dia_semana=[
            CantidadPorDiaSemana(dia=d, cantidad=por_dia[d]) for d in range(DIAS_SEMANA)
        ],
    )


def cantidad_ventas(sesion: Session, anio: int) -> CantidadVentasRespuesta:
    """Ventas del año: facturas activas con al menos un comprobante activo."""
    consulta = select(Factura.fecha_hora_emision).where(
        Factura.activo.is_(True),
        Factura.fecha_hora_emision >= datetime(anio, 1, 1),
        exists().where(
            ComprobantePago.factura_id == Factura.id,
            ComprobantePago.activo.is_(True),
        ),
    )
    if anio < ANIO_MAX:  # datetime(10000, 1, 1) no existe
        consulta = consulta.where(Factura.fecha_hora_emision < datetime(anio + 1, 1, 1))
    return agrupar_ventas(anio, sesion.scalars(consulta).all())
