from datetime import date

"""Rutas HTTP de reportes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.productos.services import obtener_hoy
from src.reportes import services
from src.reportes.constants import PREFIJO, ANIO_MAX, ANIO_MIN, PREFIJO
from src.reportes.schemas import (
    CantidadVentasRespuesta,
    ComandasPorMozoRespuesta,
    ProductosMasVendidosRespuesta,
    VentasComparativaRespuesta,
)

router = APIRouter(prefix=PREFIJO, tags=["Reportes"])


@router.get("/comandas-por-mozo", response_model=ComandasPorMozoRespuesta)
def comandas_por_mozo(
    desde: date = Query(),
    hasta: date = Query(),
    sesion: Session = Depends(get_db),
):
    """Cantidad de comandas y ventas por mozo en un período inclusivo."""
    if desde > hasta:
        raise HTTPException(
            status_code=422,
            detail="La fecha Desde debe ser anterior o igual a la fecha Hasta.",
        )
    return services.comandas_por_mozo(sesion, desde, hasta)


@router.get("/productos-mas-vendidos", response_model=ProductosMasVendidosRespuesta)
def productos_mas_vendidos(
    desde: date = Query(),
    hasta: date = Query(),
    limite: int = Query(default=10, ge=1, le=50),
    sesion: Session = Depends(get_db),
):
    """Ranking de productos facturados por unidades en un período inclusivo."""
    if desde > hasta:
        raise HTTPException(
            status_code=422,
            detail="La fecha Desde debe ser anterior o igual a la fecha Hasta.",
        )
    return services.productos_mas_vendidos(sesion, desde, hasta, limite)


@router.get("/ventas-comparativa", response_model=VentasComparativaRespuesta)
def ventas_comparativa(
    anio: int | None = Query(default=None, ge=2000, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    sesion: Session = Depends(get_db),
    hoy: date = Depends(obtener_hoy),
):
    """Ventas por día del mes indicado contra el mes anterior."""
    return services.ventas_comparativa(
        sesion,
        anio if anio is not None else hoy.year,
        mes if mes is not None else hoy.month,
    )



@router.get("/ventas/cantidad", response_model=CantidadVentasRespuesta)
def cantidad_ventas(
    anio: int = Query(ge=ANIO_MIN, le=ANIO_MAX), sesion: Session = Depends(get_db)
):
    return services.cantidad_ventas(sesion, anio)
