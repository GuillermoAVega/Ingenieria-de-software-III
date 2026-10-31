# Lógica de negocio de secciones. No importa FastAPI ni productos.
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.secciones.exceptions import (
    NombreSeccionDuplicado,
    PosicionSeccionDuplicada,
    SeccionNoEncontrada,
)
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


def _verificar_unicidad(
    sesion: Session,
    nombre_normalizado: str,
    posicion: int,
    excluir_id: int | None = None,
) -> None:
    """Orden fijo: nombre antes que posición. Revierte y lanza el primer conflicto."""
    for columna, valor, error in (
        (Seccion.nombre_normalizado, nombre_normalizado, NombreSeccionDuplicado),
        (Seccion.posicion, posicion, PosicionSeccionDuplicada),
    ):
        consulta = select(Seccion.id).where(columna == valor)
        if excluir_id is not None:
            consulta = consulta.where(Seccion.id != excluir_id)
        if sesion.scalar(consulta) is not None:
            sesion.rollback()
            raise error()


def _confirmar(sesion: Session) -> None:
    """Confirma la transacción; los índices únicos se traducen a 409 (carrera o bug).

    Se inspecciona `nombre_normalizado` antes que `seccion.posicion`. Cualquier error
    revierte la transacción; los ajenos a ambos índices se propagan.
    """
    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        detalle = str(error.orig)
        if "nombre_normalizado" in detalle:
            raise NombreSeccionDuplicado() from error
        if "seccion.posicion" in detalle:
            raise PosicionSeccionDuplicada() from error
        raise
    except Exception:
        sesion.rollback()
        raise


def crear_seccion(sesion: Session, datos: SeccionCrear) -> Seccion:
    """Alta de una sección; el nombre o la posición duplicados lanzan su error de dominio."""
    nombre_normalizado = normalizar_nombre(datos.nombre)
    _verificar_unicidad(sesion, nombre_normalizado, datos.posicion)
    seccion = Seccion(
        nombre=datos.nombre,
        nombre_normalizado=nombre_normalizado,
        subtitulo=datos.subtitulo,
        posicion=datos.posicion,
    )
    sesion.add(seccion)
    _confirmar(sesion)
    return seccion


def actualizar_seccion(
    sesion: Session, seccion_id: int, datos: SeccionActualizar
) -> Seccion:
    """Reemplazo completo de la sección: 404 si no existe y 409 si el nombre o la posición se repiten."""
    seccion = obtener_seccion(sesion, seccion_id)
    nombre_normalizado = normalizar_nombre(datos.nombre)
    _verificar_unicidad(sesion, nombre_normalizado, datos.posicion, excluir_id=seccion_id)
    seccion.nombre = datos.nombre
    seccion.nombre_normalizado = nombre_normalizado
    seccion.subtitulo = datos.subtitulo
    seccion.posicion = datos.posicion
    _confirmar(sesion)
    return seccion


def eliminar_seccion(sesion: Session, seccion_id: int) -> None:
    """Borrado físico; la BD desvincula los productos con ON DELETE SET NULL."""
    seccion = obtener_seccion(sesion, seccion_id)
    sesion.delete(seccion)
    _confirmar(sesion)
