"""Rutas HTTP de menús ejecutivos."""
from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.productos import services
from src.productos.menus_ejecutivos import services as servicios_menus
from src.productos.menus_ejecutivos.constants import PREFIJO
from src.productos.menus_ejecutivos.models import MenuEjecutivo
from src.productos.menus_ejecutivos.schemas import MenuActualizar, MenuCrear, MenuRespuesta

router = APIRouter(prefix=PREFIJO)


@router.post("", response_model=MenuRespuesta, status_code=201)
def crear_menu(datos: MenuCrear, sesion: Session = Depends(get_db)):
    return servicios_menus.crear_menu(sesion, datos)


@router.get("/{producto_id:int}", response_model=MenuRespuesta)
def obtener_menu(producto_id: int, sesion: Session = Depends(get_db)):
    return services.obtener(sesion, MenuEjecutivo, producto_id)


@router.put("/{producto_id:int}", response_model=MenuRespuesta)
def actualizar_menu(
    producto_id: int,
    datos: MenuActualizar,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    return servicios_menus.actualizar_menu(sesion, producto_id, datos, hoy)


@router.delete("/{producto_id:int}", status_code=204)
def dar_de_baja_menu(
    producto_id: int,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    services.dar_de_baja(sesion, MenuEjecutivo, producto_id, hoy)
    return Response(status_code=204)
