from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.exceptions import BadRequest
from src.models import Comanda, DetalleComanda, DetalleFactura
from src.schemas.detalle_comanda import (
    DetalleComandaCreate,
    DetalleComandaOut,
    DetalleComandaUpdate,
)
from src.utils import exigir_producto_activo, obtener_activo_o_404

router = APIRouter(prefix="/detalles-comanda", tags=["Detalles de comanda"])


def _exigir_abierta(comanda: Comanda) -> None:
    """Una comanda cerrada ya no admite cambios en sus productos."""
    if comanda.estado != "abierta":
        raise BadRequest()


@router.post("", response_model=DetalleComandaOut, status_code=201)
def crear_detalle_comanda(datos: DetalleComandaCreate, db: Session = Depends(get_db)):
    comanda = obtener_activo_o_404(db, Comanda, datos.comanda_id)
    _exigir_abierta(comanda)
    exigir_producto_activo(db, datos.producto_id)
    detalle = DetalleComanda(**datos.model_dump())
    db.add(detalle)
    db.commit()
    db.refresh(detalle)
    return detalle


@router.get("", response_model=list[DetalleComandaOut])
def listar_detalles_comanda(
    activo: bool | None = True,
    comanda_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = select(DetalleComanda).offset(skip).limit(limit)
    if activo is not None:
        q = q.where(DetalleComanda.activo == activo)
    if comanda_id is not None:
        q = q.where(DetalleComanda.comanda_id == comanda_id)
    return db.scalars(q).all()


@router.get("/{id}", response_model=DetalleComandaOut)
def obtener_detalle_comanda(id: int, db: Session = Depends(get_db)):
    return obtener_activo_o_404(db, DetalleComanda, id)


@router.put("/{id}", response_model=DetalleComandaOut)
def modificar_detalle_comanda(id: int, datos: DetalleComandaUpdate, db: Session = Depends(get_db)):
    detalle = obtener_activo_o_404(db, DetalleComanda, id)
    cambios = datos.model_dump(exclude_unset=True)
    # marcar la entrega sigue permitido con la comanda cerrada; el resto no
    if set(cambios) - {"entregado"}:
        _exigir_abierta(detalle.comanda)
    nuevo_producto = cambios.get("producto_id")
    if nuevo_producto is not None and nuevo_producto != detalle.producto_id:
        exigir_producto_activo(db, nuevo_producto)
    for campo, valor in cambios.items():
        setattr(detalle, campo, valor)
    db.commit()
    db.refresh(detalle)
    return detalle


@router.delete("/{id}", status_code=204)
def eliminar_detalle_comanda(id: int, db: Session = Depends(get_db)):
    detalle = obtener_activo_o_404(db, DetalleComanda, id)
    _exigir_abierta(detalle.comanda)
    facturado = db.scalars(
        select(DetalleFactura).where(
            DetalleFactura.detalle_comanda_id == id, DetalleFactura.activo
        )
    ).first()
    if facturado:
        raise BadRequest()
    detalle.activo = False
    db.commit()
