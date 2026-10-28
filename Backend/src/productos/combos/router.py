"""Rutas HTTP de combos de promoción."""
from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.productos import services
from src.productos.combos import services as servicios_combos
from src.productos.combos.constants import PREFIJO
from src.productos.combos.models import ComboPromocion
from src.productos.combos.schemas import ComboActualizar, ComboCrear, ComboRespuesta

router = APIRouter(prefix=PREFIJO)


@router.post("", response_model=ComboRespuesta, status_code=201)
def crear_combo(
    datos: ComboCrear,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    return servicios_combos.crear_combo(sesion, datos, hoy)


@router.get("/{producto_id:int}", response_model=ComboRespuesta)
def obtener_combo(producto_id: int, sesion: Session = Depends(get_db)):
    return services.obtener(sesion, ComboPromocion, producto_id)


@router.put("/{producto_id:int}", response_model=ComboRespuesta)
def actualizar_combo(
    producto_id: int,
    datos: ComboActualizar,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    return servicios_combos.actualizar_combo(sesion, producto_id, datos, hoy)


@router.delete("/{producto_id:int}", status_code=204)
def dar_de_baja_combo(
    producto_id: int,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    services.dar_de_baja(sesion, ComboPromocion, producto_id, hoy)
    return Response(status_code=204)
