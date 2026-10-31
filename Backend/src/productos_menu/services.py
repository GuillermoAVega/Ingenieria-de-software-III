# Lógica de negocio del menú del día. No importa FastAPI.
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.productos import registro  # noqa: F401  (carga los mappers de todos los subtipos)
from src.productos.models import Producto
from src.productos_menu.exceptions import (
    FechaMenuOcupada,
    ProductoDadoDeBaja,
    ProductoInexistente,
    ProductoMenuNoEncontrado,
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


def _verificar_producto_activo(sesion: Session, producto: Producto) -> None:
    """Revierte y lanza `ProductoDadoDeBaja` (409) si el producto está dado de baja."""
    if producto.dado_de_baja:
        sesion.rollback()
        raise ProductoDadoDeBaja()


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


def crear_producto_menu(sesion: Session, datos: ProductoMenuCrear) -> ProductoMenu:
    """Alta de un menú del día. Prioridad: producto inexistente, dado de baja, fecha ocupada."""
    producto = sesion.get(Producto, datos.producto_id)
    if producto is None:
        sesion.rollback()
        raise ProductoInexistente(datos.producto_id)
    _verificar_producto_activo(sesion, producto)
    _verificar_fecha_libre(sesion, datos.fecha)
    registro_menu = ProductoMenu(producto_id=producto.id, fecha=datos.fecha)
    sesion.add(registro_menu)
    _confirmar(sesion)
    return registro_menu


def actualizar_fecha_producto_menu(
    sesion: Session, producto_menu_id: int, datos: ProductoMenuActualizar
) -> ProductoMenu:
    """Cambia solo la fecha. Prioridad: 404, producto dado de baja, fecha ocupada por otro."""
    registro_menu = obtener_producto_menu(sesion, producto_menu_id)
    _verificar_producto_activo(sesion, registro_menu.producto)
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
