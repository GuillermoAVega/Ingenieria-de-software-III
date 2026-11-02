"""Router de /productos: compone los subrouters y traduce los errores de dominio a HTTP."""
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.productos.bebidas.router import router as router_bebidas
from src.productos.combos.exceptions import FechaHastaVencida
from src.productos.combos.router import router as router_combos
from src.productos.exceptions import (
    BajaRestringida,
    ComponenteInactivo,
    ComponenteInvalido,
    ErrorConflicto,
    ProductoNoEncontrado,
    SeccionInexistente,
)
from src.productos.menus_ejecutivos.router import router as router_menus
from src.productos.platos.router import router as router_platos
from src.productos.postres.router import router as router_postres

router = APIRouter(prefix="/productos")


# `Producto` es abstracto: no hay GET en /productos, así que sin esta ruta
# explícita un POST devolvería 404 en lugar de 405
@router.post("", include_in_schema=False)
def rechazar_creacion_generica():
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


router.include_router(router_platos)
router.include_router(router_bebidas)
router.include_router(router_postres)
router.include_router(router_menus)
router.include_router(router_combos)


def _error_de_campo(campo: str, mensaje: str, tipo: str, **extra) -> dict:
    """Entrada de error con la misma forma que las del 422 de Pydantic."""
    return {"loc": ["body", campo], "msg": mensaje, "type": tipo, **extra}


def manejar_no_encontrado(_peticion: Request, error: ProductoNoEncontrado) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": error.mensaje})


def manejar_componente_invalido(_peticion: Request, error: ComponenteInvalido) -> JSONResponse:
    detalle = _error_de_campo(
        error.campo, error.mensaje, "componente_invalido", ids=error.ids
    )
    return JSONResponse(status_code=422, content={"detail": [detalle]})


def manejar_seccion_inexistente(_peticion: Request, error: SeccionInexistente) -> JSONResponse:
    detalle = _error_de_campo(
        "seccion_id", error.mensaje, "seccion_inexistente", ids=[error.seccion_id]
    )
    return JSONResponse(status_code=422, content={"detail": [detalle]})


def manejar_fecha_hasta_vencida(_peticion: Request, error: FechaHastaVencida) -> JSONResponse:
    detalle = _error_de_campo("fecha_hasta", error.mensaje, "fecha_hasta_vencida")
    return JSONResponse(status_code=422, content={"detail": [detalle]})


def manejar_conflicto(_peticion: Request, error: ErrorConflicto) -> JSONResponse:
    cuerpo = {"detail": error.mensaje}
    if isinstance(error, ComponenteInactivo):
        cuerpo["ids"] = error.ids
    elif isinstance(error, BajaRestringida):
        cuerpo["bloqueantes"] = error.bloqueantes
    return JSONResponse(status_code=409, content=cuerpo)


# Starlette resuelve por MRO: `ErrorConflicto` cubre también sus subclases
MANEJADORES_EXCEPCIONES = {
    ProductoNoEncontrado: manejar_no_encontrado,
    ComponenteInvalido: manejar_componente_invalido,
    SeccionInexistente: manejar_seccion_inexistente,
    FechaHastaVencida: manejar_fecha_hasta_vencida,
    ErrorConflicto: manejar_conflicto,
}
