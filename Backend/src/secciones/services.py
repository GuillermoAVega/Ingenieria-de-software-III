# Lógica de negocio de secciones. No importa FastAPI ni productos.
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.secciones.exceptions import NombreSeccionDuplicado, SeccionNoEncontrada
from src.secciones.models import Seccion
from src.secciones.schemas import SeccionActualizar, SeccionCrear
from src.texto import normalizar_nombre


def obtener_seccion(sesion: Session, seccion_id: int) -> Seccion:
    """Devuelve la sección o lanza `SeccionNoEncontrada` (404), sin dejar la transacción abierta."""
    seccion = sesion.get(Seccion, seccion_id)
    if seccion is None:
        sesion.rollback()
        raise SeccionNoEncontrada()
    return seccion


def _confirmar(sesion: Session) -> None:
    """Confirma la transacción; el índice único de nombre se traduce a 409.

    Cualquier error revierte la transacción; los ajenos al nombre se propagan.
    """
    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        if "nombre_normalizado" in str(error.orig):
            raise NombreSeccionDuplicado() from error
        raise
    except Exception:
        sesion.rollback()
        raise


def crear_seccion(sesion: Session, datos: SeccionCrear) -> Seccion:
    """Alta de una sección; el nombre duplicado lanza `NombreSeccionDuplicado`."""
    seccion = Seccion(
        nombre=datos.nombre,
        nombre_normalizado=normalizar_nombre(datos.nombre),
        subtitulo=datos.subtitulo,
        posicion=datos.posicion,
    )
    sesion.add(seccion)
    _confirmar(sesion)
    return seccion


def actualizar_seccion(
    sesion: Session, seccion_id: int, datos: SeccionActualizar
) -> Seccion:
    """Reemplazo completo de la sección: 404 si no existe y 409 si el nombre se repite."""
    seccion = obtener_seccion(sesion, seccion_id)
    seccion.nombre = datos.nombre
    seccion.nombre_normalizado = normalizar_nombre(datos.nombre)
    seccion.subtitulo = datos.subtitulo
    seccion.posicion = datos.posicion
    _confirmar(sesion)
    return seccion


def eliminar_seccion(sesion: Session, seccion_id: int) -> None:
    """Borrado físico; la BD desvincula los productos con ON DELETE SET NULL."""
    seccion = obtener_seccion(sesion, seccion_id)
    sesion.delete(seccion)
    _confirmar(sesion)
