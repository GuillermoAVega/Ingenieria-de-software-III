from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.comanda.services import (
    asignar_mozo_para_mesas,
    crear_comanda_desde_reserva,
    obtener_mesas_disponibles,
)
from src.exceptions import BadRequest
from src.models import Comanda, DetalleComanda, Factura
from src.mesa.models import Mesa
from src.schemas.comanda import ComandaCreate, ComandaOut, ComandaUpdate
from src.schemas.detalle_comanda import DetalleComandaOut
from src.utils import exigir_producto_activo, obtener_activo_o_404

router = APIRouter(prefix="/comandas", tags=["Comandas"])


@router.post("", response_model=ComandaOut, status_code=201)
def crear_comanda(datos: ComandaCreate, db: Session = Depends(get_db)):
    if datos.reserva_id is not None:
        return crear_comanda_desde_reserva(db, datos.reserva_id)
    valores = datos.model_dump(exclude={"detalles", "mesa_ids", "comensales"})
    if datos.reserva_id is None:
        ahora = datetime.now()
        valores["fecha"] = datos.fecha or ahora.date()
        valores["hora"] = datos.hora or ahora.time().replace(microsecond=0)
    mesa_ids = datos.mesa_ids or ([datos.mesa_id] if datos.mesa_id is not None else [])
    mesa_ids = list(dict.fromkeys(mesa_ids))
    mesas = obtener_mesas_disponibles(db, mesa_ids)
    if datos.comensales is not None and sum(mesa.capacidad for mesa in mesas) < datos.comensales:
        raise BadRequest(detail="La capacidad de las mesas seleccionadas no alcanza para todos los comensales")
    valores["mozo_id"] = asignar_mozo_para_mesas(db, mesas)
    for mesa in mesas:
        mesa.disponible = False
    valores["mesa_id"] = mesa_ids[0]
    comanda = Comanda(**valores, mesas_asociadas=mesas)
    for detalle in datos.detalles:
        exigir_producto_activo(db, detalle.producto_id)
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
    if nuevo_estado == "cerrada":
        detalles_activos = [detalle for detalle in comanda.detalles if detalle.activo]
        if not detalles_activos:
            raise BadRequest(detail="No se puede cerrar una comanda sin productos")
        if any(not detalle.entregado for detalle in detalles_activos):
            raise BadRequest(detail="No se puede cerrar la comanda: hay productos pendientes de entrega")
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
