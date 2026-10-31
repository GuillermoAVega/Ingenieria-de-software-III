"""Rutas HTTP de secciones y traducción de sus errores de dominio a HTTP."""
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.secciones import services
from src.secciones.constants import PREFIJO
from src.secciones.exceptions import (
    NombreSeccionDuplicado,
    PosicionSeccionDuplicada,
    SeccionNoEncontrada,
)
from src.secciones.schemas import SeccionActualizar, SeccionCrear, SeccionRespuesta

router = APIRouter(prefix=PREFIJO)


@router.post("", response_model=SeccionRespuesta, status_code=201)
def crear_seccion(datos: SeccionCrear, sesion: Session = Depends(get_db)):
    return services.crear_seccion(sesion, datos)


@router.get("/{seccion_id:int}", response_model=SeccionRespuesta)
def obtener_seccion(seccion_id: int, sesion: Session = Depends(get_db)):
    return services.obtener_seccion(sesion, seccion_id)


@router.put("/{seccion_id:int}", response_model=SeccionRespuesta)
def actualizar_seccion(
    seccion_id: int, datos: SeccionActualizar, sesion: Session = Depends(get_db)
):
    return services.actualizar_seccion(sesion, seccion_id, datos)


@router.delete("/{seccion_id:int}", status_code=204)
def eliminar_seccion(seccion_id: int, sesion: Session = Depends(get_db)):
    services.eliminar_seccion(sesion, seccion_id)
    return Response(status_code=204)


def manejar_no_encontrada(_peticion: Request, error: SeccionNoEncontrada) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": error.mensaje})


def manejar_nombre_duplicado(
    _peticion: Request, error: NombreSeccionDuplicado
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": error.mensaje})


def manejar_posicion_duplicada(
    _peticion: Request, error: PosicionSeccionDuplicada
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": error.mensaje})


MANEJADORES_EXCEPCIONES = {
    SeccionNoEncontrada: manejar_no_encontrada,
    NombreSeccionDuplicado: manejar_nombre_duplicado,
    PosicionSeccionDuplicada: manejar_posicion_duplicada,
}
