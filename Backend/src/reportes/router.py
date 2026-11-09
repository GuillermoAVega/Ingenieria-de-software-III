"""Rutas HTTP de reportes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.reportes import services
from src.reportes.constants import ANIO_MAX, ANIO_MIN, PREFIJO
from src.reportes.schemas import CantidadVentasRespuesta

router = APIRouter(prefix=PREFIJO)


@router.get("/ventas/cantidad", response_model=CantidadVentasRespuesta)
def cantidad_ventas(
    anio: int = Query(ge=ANIO_MIN, le=ANIO_MAX), sesion: Session = Depends(get_db)
):
    return services.cantidad_ventas(sesion, anio)
