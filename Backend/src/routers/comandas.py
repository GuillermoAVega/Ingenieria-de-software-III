from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.database import get_db
from src.comanda.services import (
    crear_comanda as servicio_crear_comanda,
    eliminar_comanda as servicio_eliminar_comanda,
    modificar_comanda as servicio_modificar_comanda,
)
from src.models import Comanda
from src.schemas.comanda import ComandaCreate, ComandaOut, ComandaUpdate
from src.schemas.detalle_comanda import DetalleComandaOut
from src.utils import obtener_activo_o_404

router = APIRouter(prefix="/comandas", tags=["Comandas"])


@router.post("", response_model=ComandaOut, status_code=201)
def crear_comanda(datos: ComandaCreate, db: Session = Depends(get_db)):
    return servicio_crear_comanda(db, datos)


@router.get("", response_model=list[ComandaOut])
def listar_comandas(
    activo: bool | None = True, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    q = (
        select(Comanda)
        .order_by(desc(Comanda.fecha), desc(Comanda.hora), desc(Comanda.id))
        .offset(skip)
        .limit(limit)
    )
    if activo is not None:
        q = q.where(Comanda.activo == activo)
    return db.scalars(q).all()


@router.get("/{id}", response_model=ComandaOut)
def obtener_comanda(id: int, db: Session = Depends(get_db)):
    return obtener_activo_o_404(db, Comanda, id)


@router.get("/{id}/detalles", response_model=list[DetalleComandaOut])
def listar_detalles_de_comanda(id: int, db: Session = Depends(get_db)):
    comanda = obtener_activo_o_404(db, Comanda, id)
    return [d for d in comanda.detalles if d.activo]


@router.put("/{id}", response_model=ComandaOut)
def modificar_comanda(id: int, datos: ComandaUpdate, db: Session = Depends(get_db)):
    comanda = obtener_activo_o_404(db, Comanda, id)
    return servicio_modificar_comanda(db, comanda, datos.model_dump(exclude_unset=True))


@router.delete("/{id}", status_code=204)
def eliminar_comanda(id: int, db: Session = Depends(get_db)):
    comanda = obtener_activo_o_404(db, Comanda, id)
    servicio_eliminar_comanda(db, comanda)
