"""Rutas HTTP del menú del día y traducción de sus errores de dominio a HTTP."""
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.productos_menu import services
from src.productos_menu.constants import PREFIJO
from src.productos_menu.exceptions import (
    FechaMenuOcupada,
    ProductoDadoDeBaja,
    ProductoInexistente,
    ProductoMenuNoEncontrado,
)
from src.productos_menu.schemas import (
    ProductoMenuActualizar,
    ProductoMenuCrear,
    ProductoMenuRespuesta,
)

router = APIRouter(prefix=PREFIJO)


@router.post("", response_model=ProductoMenuRespuesta, status_code=201)
def crear_producto_menu(datos: ProductoMenuCrear, sesion: Session = Depends(get_db)):
    return services.crear_producto_menu(sesion, datos)


@router.put("/{producto_menu_id:int}", response_model=ProductoMenuRespuesta)
def actualizar_producto_menu(
    producto_menu_id: int,
    datos: ProductoMenuActualizar,
    sesion: Session = Depends(get_db),
):
    return services.actualizar_fecha_producto_menu(sesion, producto_menu_id, datos)


@router.delete("/{producto_menu_id:int}", status_code=204)
def eliminar_producto_menu(producto_menu_id: int, sesion: Session = Depends(get_db)):
    services.eliminar_producto_menu(sesion, producto_menu_id)
    return Response(status_code=204)


def _error_de_campo(campo: str, mensaje: str, tipo: str, **extra) -> dict:
    """Entrada de error con la misma forma que las del 422 de Pydantic."""
    return {"loc": ["body", campo], "msg": mensaje, "type": tipo, **extra}


def manejar_producto_inexistente(
    _peticion: Request, error: ProductoInexistente
) -> JSONResponse:
    detalle = _error_de_campo(
        "producto_id", error.mensaje, "producto_inexistente", ids=[error.producto_id]
    )
    return JSONResponse(status_code=422, content={"detail": [detalle]})


def manejar_producto_dado_de_baja(
    _peticion: Request, error: ProductoDadoDeBaja
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": error.mensaje})


def manejar_fecha_ocupada(_peticion: Request, error: FechaMenuOcupada) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": error.mensaje})


def manejar_no_encontrado(
    _peticion: Request, error: ProductoMenuNoEncontrado
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": error.mensaje})


MANEJADORES_EXCEPCIONES = {
    ProductoInexistente: manejar_producto_inexistente,
    ProductoDadoDeBaja: manejar_producto_dado_de_baja,
    FechaMenuOcupada: manejar_fecha_ocupada,
    ProductoMenuNoEncontrado: manejar_no_encontrado,
}
