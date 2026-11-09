"""Consultas de reportes de ventas."""
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
