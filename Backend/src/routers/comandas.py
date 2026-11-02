from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.exceptions import BadRequest
from src.models import Comanda, DetalleComanda, Factura
from src.schemas.comanda import ComandaCreate, ComandaOut, ComandaUpdate
from src.schemas.detalle_comanda import DetalleComandaOut
from src.utils import obtener_activo_o_404

router = APIRouter(prefix="/comandas", tags=["Comandas"])


@router.post("", response_model=ComandaOut, status_code=201)
def crear_comanda(datos: ComandaCreate, db: Session = Depends(get_db)):
    comanda = Comanda(**datos.model_dump(exclude={"detalles"}))
    comanda.detalles = [DetalleComanda(**d.model_dump()) for d in datos.detalles]
    db.add(comanda)
    db.commit()
    db.refresh(comanda)
    return comanda


@router.get("", response_model=list[ComandaOut])
def listar_comandas(
    activo: bool | None = True, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    q = select(Comanda).offset(skip).limit(limit)
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
    cambios = datos.model_dump(exclude_unset=True)
    if cambios.get("estado", "") is None:
        del cambios["estado"]
    nuevo_estado = cambios.get("estado")
    if comanda.estado == "cerrada" and set(cambios) - {"estado"}:
        raise BadRequest()  # reabrila antes de modificarla
    if nuevo_estado == "cerrada" and not any(d.activo for d in comanda.detalles):
        raise BadRequest()  # no se cierra una comanda sin productos
    if nuevo_estado == "abierta" and comanda.factura and comanda.factura.activo:
        raise BadRequest()  # ya fue facturada
    for campo, valor in cambios.items():
        setattr(comanda, campo, valor)
    db.commit()
    db.refresh(comanda)
    return comanda


@router.delete("/{id}", status_code=204)
def eliminar_comanda(id: int, db: Session = Depends(get_db)):
    comanda = obtener_activo_o_404(db, Comanda, id)
    factura = db.scalars(select(Factura).where(Factura.comanda_id == id, Factura.activo)).first()
    if factura:
        raise BadRequest()
    comanda.activo = False
    for detalle in comanda.detalles:
        detalle.activo = False
    db.commit()
