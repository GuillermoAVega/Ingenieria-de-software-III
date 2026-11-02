from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.exceptions import BadRequest
from src.models import DetalleComanda, DetalleFactura, Factura
from src.schemas.detalle_factura import (
    DetalleFacturaCreate,
    DetalleFacturaOut,
    DetalleFacturaUpdate,
)
from src.utils import obtener_activo_o_404

router = APIRouter(prefix="/detalles-factura", tags=["Detalles de factura"])


def _recalcular_total(factura: Factura) -> None:
    """importe_total = suma de precio_final de los detalles activos."""
    factura.importe_total = sum(d.precio_final for d in factura.detalles if d.activo)


def _validar_detalle_comanda(db: Session, factura: Factura, detalle_comanda_id: int | None):
    """El detalle de comanda debe estar activo y pertenecer a la comanda de la factura."""
    if detalle_comanda_id is None:
        return
    dc = obtener_activo_o_404(db, DetalleComanda, detalle_comanda_id)
    if dc.comanda_id != factura.comanda_id:
        raise BadRequest()


@router.post("", response_model=DetalleFacturaOut, status_code=201)
def crear_detalle_factura(datos: DetalleFacturaCreate, db: Session = Depends(get_db)):
    factura = obtener_activo_o_404(db, Factura, datos.factura_id)
    _validar_detalle_comanda(db, factura, datos.detalle_comanda_id)
    campos = datos.model_dump()
    if campos["precio_final"] is None:
        campos["precio_final"] = datos.precio_unitario * datos.cantidad
    detalle = DetalleFactura(**campos)
    db.add(detalle)
    db.flush()
    db.refresh(factura)
    _recalcular_total(factura)
    db.commit()
    db.refresh(detalle)
    return detalle


@router.get("", response_model=list[DetalleFacturaOut])
def listar_detalles_factura(
    activo: bool | None = True,
    factura_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = select(DetalleFactura).offset(skip).limit(limit)
    if activo is not None:
        q = q.where(DetalleFactura.activo == activo)
    if factura_id is not None:
        q = q.where(DetalleFactura.factura_id == factura_id)
    return db.scalars(q).all()


@router.get("/{id}", response_model=DetalleFacturaOut)
def obtener_detalle_factura(id: int, db: Session = Depends(get_db)):
    return obtener_activo_o_404(db, DetalleFactura, id)


@router.put("/{id}", response_model=DetalleFacturaOut)
def modificar_detalle_factura(id: int, datos: DetalleFacturaUpdate, db: Session = Depends(get_db)):
    detalle = obtener_activo_o_404(db, DetalleFactura, id)
    cambios = datos.model_dump(exclude_unset=True)
    if "detalle_comanda_id" in cambios:
        _validar_detalle_comanda(db, detalle.factura, cambios["detalle_comanda_id"])
    for campo, valor in cambios.items():
        setattr(detalle, campo, valor)
    # si cambió precio o cantidad y no se envió precio_final, se recalcula
    if ("precio_unitario" in cambios or "cantidad" in cambios) and "precio_final" not in cambios:
        detalle.precio_final = detalle.precio_unitario * detalle.cantidad
    _recalcular_total(detalle.factura)
    db.commit()
    db.refresh(detalle)
    return detalle


@router.delete("/{id}", status_code=204)
def eliminar_detalle_factura(id: int, db: Session = Depends(get_db)):
    detalle = obtener_activo_o_404(db, DetalleFactura, id)
    detalle.activo = False
    _recalcular_total(detalle.factura)
    db.commit()
