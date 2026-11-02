from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.exceptions import BadRequest
from src.models import ComprobantePago, Factura, MedioPago
from src.schemas.comprobante_pago import (
    ComprobantePagoCreate,
    ComprobantePagoOut,
    ComprobantePagoUpdate,
)
from src.utils import obtener_activo_o_404

router = APIRouter(prefix="/comprobantes-pago", tags=["Comprobantes de pago"])


def _validar_importe(factura: Factura, importe: float, excluir_id: int | None = None):
    """La suma de comprobantes activos no puede superar el total de la factura."""
    pagado = sum(c.importe for c in factura.comprobantes if c.activo and c.id != excluir_id)
    if pagado + importe > factura.importe_total + 1e-9:
        raise BadRequest()


@router.post("", response_model=ComprobantePagoOut, status_code=201)
def crear_comprobante_pago(datos: ComprobantePagoCreate, db: Session = Depends(get_db)):
    factura = obtener_activo_o_404(db, Factura, datos.factura_id)
    obtener_activo_o_404(db, MedioPago, datos.medio_pago_id)
    _validar_importe(factura, datos.importe)
    comprobante = ComprobantePago(
        factura_id=datos.factura_id,
        medio_pago_id=datos.medio_pago_id,
        importe=datos.importe,
        fecha_hora_emision=datos.fecha_hora_emision or datetime.now(),
    )
    db.add(comprobante)
    db.commit()
    db.refresh(comprobante)
    return comprobante


@router.get("", response_model=list[ComprobantePagoOut])
def listar_comprobantes_pago(
    activo: bool | None = True,
    factura_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = select(ComprobantePago).offset(skip).limit(limit)
    if activo is not None:
        q = q.where(ComprobantePago.activo == activo)
    if factura_id is not None:
        q = q.where(ComprobantePago.factura_id == factura_id)
    return db.scalars(q).all()


@router.get("/{id}", response_model=ComprobantePagoOut)
def obtener_comprobante_pago(id: int, db: Session = Depends(get_db)):
    return obtener_activo_o_404(db, ComprobantePago, id)


@router.put("/{id}", response_model=ComprobantePagoOut)
def modificar_comprobante_pago(id: int, datos: ComprobantePagoUpdate, db: Session = Depends(get_db)):
    comprobante = obtener_activo_o_404(db, ComprobantePago, id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "medio_pago_id" in cambios:
        obtener_activo_o_404(db, MedioPago, cambios["medio_pago_id"])
    if "importe" in cambios:
        _validar_importe(comprobante.factura, cambios["importe"], excluir_id=id)
    for campo, valor in cambios.items():
        setattr(comprobante, campo, valor)
    db.commit()
    db.refresh(comprobante)
    return comprobante


@router.delete("/{id}", status_code=204)
def eliminar_comprobante_pago(id: int, db: Session = Depends(get_db)):
    comprobante = obtener_activo_o_404(db, ComprobantePago, id)
    comprobante.activo = False
    db.commit()
