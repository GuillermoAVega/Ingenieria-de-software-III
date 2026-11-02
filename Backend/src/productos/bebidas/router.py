"""Rutas HTTP de bebidas."""
from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.productos import services
from src.productos.bebidas import services as servicios_bebidas
from src.productos.bebidas.constants import PREFIJO
from src.productos.bebidas.models import Bebida
from src.productos.bebidas.schemas import BebidaActualizar, BebidaCrear, BebidaRespuesta

router = APIRouter(prefix=PREFIJO)


@router.post("", response_model=BebidaRespuesta, status_code=201)
def crear_bebida(datos: BebidaCrear, sesion: Session = Depends(get_db)):
    return servicios_bebidas.crear_bebida(sesion, datos)


@router.get("", response_model=list[BebidaRespuesta])
def listar_bebidas(sesion: Session = Depends(get_db)):
    return servicios_bebidas.listar_bebidas(sesion)


@router.get("/{producto_id:int}", response_model=BebidaRespuesta)
def obtener_bebida(producto_id: int, sesion: Session = Depends(get_db)):
    return services.obtener(sesion, Bebida, producto_id)


@router.put("/{producto_id:int}", response_model=BebidaRespuesta)
def actualizar_bebida(
    producto_id: int,
    datos: BebidaActualizar,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    return servicios_bebidas.actualizar_bebida(sesion, producto_id, datos, hoy)


@router.delete("/{producto_id:int}", status_code=204)
def dar_de_baja_bebida(
    producto_id: int,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    services.dar_de_baja(sesion, Bebida, producto_id, hoy)
    return Response(status_code=204)
