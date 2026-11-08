"""Rutas HTTP de menús del día."""
from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.productos import services
from src.productos.menus_del_dia import services as servicios_menus_del_dia
from src.productos.menus_del_dia.constants import PREFIJO
from src.productos.menus_del_dia.models import MenuDelDia
from src.productos.menus_del_dia.schemas import (
    MenuDelDiaActualizar,
    MenuDelDiaCrear,
    MenuDelDiaListado,
    MenuDelDiaRespuesta,
)

router = APIRouter(prefix=PREFIJO)


@router.post("", response_model=MenuDelDiaRespuesta, status_code=201)
def crear_menu_del_dia(datos: MenuDelDiaCrear, sesion: Session = Depends(get_db)):
    return servicios_menus_del_dia.crear_menu_del_dia(sesion, datos)


@router.get("", response_model=list[MenuDelDiaListado])
def listar_menus_del_dia(
    sesion: Session = Depends(get_db), hoy: date = Depends(services.obtener_hoy)
):
    return servicios_menus_del_dia.listar_menus_del_dia_con_proxima_fecha(sesion, hoy)


@router.get("/{producto_id:int}", response_model=MenuDelDiaRespuesta)
def obtener_menu_del_dia(producto_id: int, sesion: Session = Depends(get_db)):
    return services.obtener(sesion, MenuDelDia, producto_id)


@router.put("/{producto_id:int}", response_model=MenuDelDiaRespuesta)
def actualizar_menu_del_dia(
    producto_id: int,
    datos: MenuDelDiaActualizar,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    return servicios_menus_del_dia.actualizar_menu_del_dia(sesion, producto_id, datos, hoy)


@router.delete("/{producto_id:int}", status_code=204)
def dar_de_baja_menu_del_dia(
    producto_id: int,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(services.obtener_hoy),
):
    services.dar_de_baja(sesion, MenuDelDia, producto_id, hoy)
    return Response(status_code=204)
