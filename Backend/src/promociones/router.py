"""Rutas HTTP de promociones y traducción de sus errores de dominio a HTTP."""
from datetime import date

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.productos.services import obtener_hoy
from src.promociones import services
from src.promociones.constants import PREFIJO
from src.promociones.exceptions import (
    FechaHastaVencida,
    ProductosDadosDeBaja,
    ProductosInexistentes,
    PromocionEnUso,
    PromocionNoEncontrada,
)
from src.promociones.schemas import (
    PromocionActualizar,
    PromocionCrear,
    PromocionRespuesta,
)

router = APIRouter(prefix=PREFIJO)


@router.post("", response_model=PromocionRespuesta, status_code=201)
def crear_promocion(
    datos: PromocionCrear,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(obtener_hoy),
):
    return services.crear_promocion(sesion, datos, hoy)


@router.get("", response_model=list[PromocionRespuesta])
def listar_promociones(
    incluir_bajas: bool = False,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(obtener_hoy),
):
    return services.listar_promociones(sesion, hoy, incluir_bajas)


@router.get("/{promocion_id:int}", response_model=PromocionRespuesta)
def obtener_promocion(
    promocion_id: int,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(obtener_hoy),
):
    services.dar_de_baja_vencidas(sesion, hoy)
    promocion = services.obtener_promocion(sesion, promocion_id)
    services.marcar_en_uso(sesion, [promocion])
    return promocion


@router.put("/{promocion_id:int}", response_model=PromocionRespuesta)
def actualizar_promocion(
    promocion_id: int,
    datos: PromocionActualizar,
    sesion: Session = Depends(get_db),
    hoy: date = Depends(obtener_hoy),
):
    return services.actualizar_promocion(sesion, promocion_id, datos, hoy)


@router.delete("/{promocion_id:int}", status_code=204)
def dar_de_baja_promocion(promocion_id: int, sesion: Session = Depends(get_db)):
    services.dar_de_baja_promocion(sesion, promocion_id)
    return Response(status_code=204)


def _error_de_campo(campo: str, mensaje: str, tipo: str, **extra) -> dict:
    """Entrada de error con la misma forma que las del 422 de Pydantic."""
    return {"loc": ["body", campo], "msg": mensaje, "type": tipo, **extra}


def manejar_no_encontrada(_peticion: Request, error: PromocionNoEncontrada) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": error.mensaje})


def manejar_en_uso(_peticion: Request, error: PromocionEnUso) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": error.mensaje})


def manejar_productos_dados_de_baja(
    _peticion: Request, error: ProductosDadosDeBaja
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": error.mensaje})


def manejar_productos_inexistentes(
    _peticion: Request, error: ProductosInexistentes
) -> JSONResponse:
    detalle = _error_de_campo(
        "productos_ids", error.mensaje, "producto_inexistente", ids=error.ids
    )
    return JSONResponse(status_code=422, content={"detail": [detalle]})


def manejar_fecha_hasta_vencida(
    _peticion: Request, error: FechaHastaVencida
) -> JSONResponse:
    detalle = _error_de_campo("fecha_hasta", error.mensaje, "fecha_hasta_vencida")
    return JSONResponse(status_code=422, content={"detail": [detalle]})


MANEJADORES_EXCEPCIONES = {
    PromocionNoEncontrada: manejar_no_encontrada,
    PromocionEnUso: manejar_en_uso,
    ProductosDadosDeBaja: manejar_productos_dados_de_baja,
    ProductosInexistentes: manejar_productos_inexistentes,
    FechaHastaVencida: manejar_fecha_hasta_vencida,
}
