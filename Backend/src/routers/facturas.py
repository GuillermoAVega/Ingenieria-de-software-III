from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.comanda.services import liberar_mesas
from src.exceptions import BadRequest
from src.mesa.models import Mesa
from src.models import Comanda, Factura
from src.schemas.comprobante_pago import ComprobantePagoOut
from src.schemas.detalle_factura import DetalleFacturaOut
from src.schemas.factura import FacturaCreate, FacturaOut, FacturaUpdate
from src.utils import obtener_activo_o_404

router = APIRouter(prefix="/facturas", tags=["Facturas"])


@router.post("", response_model=FacturaOut, status_code=201)
def crear_factura(datos: FacturaCreate, db: Session = Depends(get_db)):
    comanda = obtener_activo_o_404(db, Comanda, datos.comanda_id)
    if comanda.estado != "cerrada":
        raise BadRequest()  # la factura se genera una vez cerrada la comanda
    existente = db.scalars(
        select(Factura).where(Factura.comanda_id == datos.comanda_id, Factura.activo)
    ).first()
    if existente:
        raise BadRequest()
    factura = Factura(
        comanda_id=datos.comanda_id,
        fecha_hora_emision=datos.fecha_hora_emision or datetime.now(),
        importe_total=0,
    )
    db.add(factura)
    mesas = list(comanda.mesas_asociadas)
    if not mesas and comanda.mesa_id is not None:
        mesa = db.get(Mesa, comanda.mesa_id)
        if mesa is not None:
            mesas = [mesa]
    liberar_mesas(mesas)
    db.commit()
    db.refresh(factura)
    return factura


@router.get("", response_model=list[FacturaOut])
def listar_facturas(
    activo: bool | None = True,
    comanda_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = select(Factura).offset(skip).limit(limit)
    if activo is not None:
        q = q.where(Factura.activo == activo)
    if comanda_id is not None:
        q = q.where(Factura.comanda_id == comanda_id)
    return db.scalars(q).all()


@router.get("/{id}", response_model=FacturaOut)
def obtener_factura(id: int, db: Session = Depends(get_db)):
    return obtener_activo_o_404(db, Factura, id)


@router.get("/{id}/detalles", response_model=list[DetalleFacturaOut])
def listar_detalles_de_factura(id: int, db: Session = Depends(get_db)):
    factura = obtener_activo_o_404(db, Factura, id)
    return [d for d in factura.detalles if d.activo]


@router.get("/{id}/comprobantes", response_model=list[ComprobantePagoOut])
def listar_comprobantes_de_factura(id: int, db: Session = Depends(get_db)):
    factura = obtener_activo_o_404(db, Factura, id)
    return [c for c in factura.comprobantes if c.activo]


@router.put("/{id}", response_model=FacturaOut)
def modificar_factura(id: int, datos: FacturaUpdate, db: Session = Depends(get_db)):
    factura = obtener_activo_o_404(db, Factura, id)
    for campo, valor in datos.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(factura, campo, valor)
    db.commit()
    db.refresh(factura)
    return factura


@router.delete("/{id}", status_code=204)
def eliminar_factura(id: int, db: Session = Depends(get_db)):
    factura = obtener_activo_o_404(db, Factura, id)
    if any(c.activo for c in factura.comprobantes):
        raise BadRequest()
    factura.activo = False
    for detalle in factura.detalles:
        detalle.activo = False
    db.commit()
