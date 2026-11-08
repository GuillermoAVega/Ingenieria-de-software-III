# Lógica de negocio del menú del día. No importa FastAPI.
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from src.productos import registro  # noqa: F401  (carga los mappers de todos los subtipos)
from src.productos.constants import TIPO_MENU_DEL_DIA
from src.productos.models import Producto
from src.productos_menu.exceptions import (
    FechaMenuOcupada,
    FechaMenuPasada,
    MenuDelDiaDadoDeBaja,
    MenuDelDiaInexistente,
    ProductoMenuNoEncontrado,
    ProductoNoMenuDelDia,
)
from src.productos_menu.models import ProductoMenu
from src.productos_menu.schemas import ProductoMenuActualizar, ProductoMenuCrear


def obtener_producto_menu(sesion: Session, producto_menu_id: int) -> ProductoMenu:
    """Devuelve el menú del día o lanza `ProductoMenuNoEncontrado` (404), sin dejar la transacción abierta."""
    registro_menu = sesion.get(ProductoMenu, producto_menu_id)
    if registro_menu is None:
        sesion.rollback()
        raise ProductoMenuNoEncontrado()
    return registro_menu


def listar_productos_menu(sesion: Session) -> list[ProductoMenu]:
    """Lista todos los menús del día, del más reciente al más antiguo.

    Incluye los menús cuyo MenuDelDia fue dado de baja (historial). Carga el
    MenuDelDia asociado en la misma consulta para evitar N+1 al serializar.
    """
    consulta = (
        select(ProductoMenu)
        .options(selectinload(ProductoMenu.menu_del_dia))
        .order_by(ProductoMenu.fecha.desc())
    )
    return list(sesion.scalars(consulta))


def _verificar_menu_activo(sesion: Session, menu: Producto) -> None:
    """Revierte y lanza `MenuDelDiaDadoDeBaja` (409) si el menú del día está dado de baja."""
    if menu.dado_de_baja:
        sesion.rollback()
        raise MenuDelDiaDadoDeBaja()


def _verificar_fecha_no_pasada(sesion: Session, fecha: date, hoy: date) -> None:
    """Revierte y lanza `FechaMenuPasada` (422) si la fecha es anterior a hoy (hoy y futuras son válidas)."""
    if fecha < hoy:
        sesion.rollback()
        raise FechaMenuPasada()


def _verificar_fecha_libre(
    sesion: Session, fecha: date, excluir_id: int | None = None
) -> None:
    """Revierte y lanza `FechaMenuOcupada` (409) si otro registro ya usa la fecha."""
    consulta = select(ProductoMenu.id).where(ProductoMenu.fecha == fecha)
    if excluir_id is not None:
        consulta = consulta.where(ProductoMenu.id != excluir_id)
    if sesion.scalar(consulta) is not None:
        sesion.rollback()
        raise FechaMenuOcupada()


def _confirmar(sesion: Session) -> None:
    """Confirma la transacción; el índice único de la fecha se traduce a 409 (carrera o bug).

    Cualquier error revierte la transacción; los ajenos a `producto_menu.fecha` se propagan.
    """
    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        if "producto_menu.fecha" in str(error.orig):
            raise FechaMenuOcupada() from error
        raise
    except Exception:
        sesion.rollback()
        raise


def crear_producto_menu(
    sesion: Session, datos: ProductoMenuCrear, hoy: date
) -> ProductoMenu:
    """Alta de un menú del día. `hoy` es la fecha actual inyectada.

    Prioridad: producto inexistente (422), no es MenuDelDia (422), fecha pasada
    (422), dado de baja (409), fecha ocupada (409). Los errores de validación de la
    entrada (422) se evalúan antes que los conflictos de estado (409).
    """
    menu = sesion.get(Producto, datos.menu_del_dia_id)
    if menu is None:
        sesion.rollback()
        raise MenuDelDiaInexistente(datos.menu_del_dia_id)
    if menu.tipo != TIPO_MENU_DEL_DIA:
        sesion.rollback()
        raise ProductoNoMenuDelDia(datos.menu_del_dia_id)
    _verificar_fecha_no_pasada(sesion, datos.fecha, hoy)
    _verificar_menu_activo(sesion, menu)
    _verificar_fecha_libre(sesion, datos.fecha)
    registro_menu = ProductoMenu(menu_del_dia_id=menu.id, fecha=datos.fecha)
    sesion.add(registro_menu)
    _confirmar(sesion)
    return registro_menu


def actualizar_fecha_producto_menu(
    sesion: Session, producto_menu_id: int, datos: ProductoMenuActualizar, hoy: date
) -> ProductoMenu:
    """Cambia solo la fecha. `hoy` es la fecha actual inyectada.

    Prioridad: 404, fecha pasada (422), producto dado de baja (409), fecha
    ocupada por otro (409).
    """
    registro_menu = obtener_producto_menu(sesion, producto_menu_id)
    _verificar_fecha_no_pasada(sesion, datos.fecha, hoy)
    _verificar_menu_activo(sesion, registro_menu.menu_del_dia)
    _verificar_fecha_libre(sesion, datos.fecha, excluir_id=producto_menu_id)
    # Se asigna después de verificar: la sesión no autoflushea
    registro_menu.fecha = datos.fecha
    _confirmar(sesion)
    return registro_menu


def eliminar_producto_menu(sesion: Session, producto_menu_id: int) -> None:
    """Borrado físico; no consulta el estado del producto asociado."""
    registro_menu = obtener_producto_menu(sesion, producto_menu_id)
    sesion.delete(registro_menu)
    _confirmar(sesion)
