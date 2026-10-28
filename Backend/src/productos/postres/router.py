"""Rutas HTTP de postres."""
from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.productos import services
from src.productos.postres import services as servicios_postres
from src.productos.postres.constants import PREFIJO
from src.productos.postres.models import Postre
from src.productos.postres.schemas import PostreActualizar, PostreCrear, PostreRespuesta

router = APIRouter(prefix=PREFIJO)


@router.post("", response_model=PostreRespuesta, status_code=201)
def crear_postre(datos: PostreCrear, sesion: Session = Depends(get_db)):
    return servicios_postres.crear_postre(sesion, datos)


@router.get("/{producto_id:int}", response_model=PostreRespuesta)
def obtener_postre(producto_id: int, sesion: Session = Depends(get_db)):
    return services.obtener(sesion, Postre, producto_id)


@router.put("/{producto_id:int}", response_model=PostreRespuesta)
def actualizar_postre(
    producto_id: int,
    datos: PostreActualizar,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    return servicios_postres.actualizar_postre(sesion, producto_id, datos, hoy)


@router.delete("/{producto_id:int}", status_code=204)
def dar_de_baja_postre(
    producto_id: int,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    services.dar_de_baja(sesion, Postre, producto_id, hoy)
    return Response(status_code=204)
