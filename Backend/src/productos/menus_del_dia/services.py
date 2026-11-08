from datetime import date

from sqlalchemy.orm import Session

from src.productos import services
from src.productos.menus_del_dia.models import MenuDelDia
from src.productos.menus_del_dia.schemas import (
    MenuDelDiaActualizar,
    MenuDelDiaCrear,
    MenuDelDiaListado,
)


def listar_menus_del_dia(sesion: Session) -> list[MenuDelDia]:
    return services.listar(sesion, MenuDelDia)


def proxima_fecha(menu: MenuDelDia, hoy: date) -> date | None:
    return min((asignacion.fecha for asignacion in menu.fechas if asignacion.fecha >= hoy), default=None)


def listar_menus_del_dia_con_proxima_fecha(sesion: Session, hoy: date) -> list[MenuDelDiaListado]:
    return [
        MenuDelDiaListado.model_validate(menu).model_copy(
            update={"proxima_fecha": proxima_fecha(menu, hoy)}
        )
        for menu in listar_menus_del_dia(sesion)
    ]


def crear_menu_del_dia(sesion: Session, datos: MenuDelDiaCrear) -> MenuDelDia:
    return services.crear_producto(sesion, MenuDelDia, datos)


def actualizar_menu_del_dia(
    sesion: Session, menu_del_dia_id: int, datos: MenuDelDiaActualizar, hoy: date
) -> MenuDelDia:
    return services.actualizar_producto(sesion, MenuDelDia, menu_del_dia_id, datos, hoy)
