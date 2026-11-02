"""Rutas HTTP de platos."""
from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.productos import services
from src.productos.platos import services as servicios_platos
from src.productos.platos.constants import PREFIJO
from src.productos.platos.models import Plato
from src.productos.platos.schemas import PlatoActualizar, PlatoCrear, PlatoRespuesta

router = APIRouter(prefix=PREFIJO)


@router.post("", response_model=PlatoRespuesta, status_code=201)
def crear_plato(datos: PlatoCrear, sesion: Session = Depends(get_db)):
    return servicios_platos.crear_plato(sesion, datos)


@router.get("", response_model=list[PlatoRespuesta])
def listar_platos(sesion: Session = Depends(get_db)):
    return servicios_platos.listar_platos(sesion)


@router.get("/{producto_id:int}", response_model=PlatoRespuesta)
def obtener_plato(producto_id: int, sesion: Session = Depends(get_db)):
    return services.obtener(sesion, Plato, producto_id)


@router.put("/{producto_id:int}", response_model=PlatoRespuesta)
def actualizar_plato(
    producto_id: int,
    datos: PlatoActualizar,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    return servicios_platos.actualizar_plato(sesion, producto_id, datos, hoy)


@router.delete("/{producto_id:int}", status_code=204)
def dar_de_baja_plato(
    producto_id: int,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    services.dar_de_baja(sesion, Plato, producto_id, hoy)
    return Response(status_code=204)
