from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.exceptions import BadRequest
from src.models import DetalleComanda, DetalleFactura, Factura
from src.productos.services import obtener_hoy
from src.promociones.services import dar_de_baja_vencidas, recalcular_producto
from src.schemas.detalle_factura import (
    DetalleFacturaCreate,
    DetalleFacturaOut,
    DetalleFacturaUpdate,
)
from src.utils import obtener_activo_o_404

router = APIRouter(prefix="/detalles-factura", tags=["Detalles de factura"])

CENTAVOS = Decimal("0.01")


def _recalcular_total(factura: Factura) -> None:
    """importe_total = suma de precio_final de los detalles activos, a 2 decimales."""
    total = sum((Decimal(str(d.precio_final)) for d in factura.detalles if d.activo), Decimal(0))
    factura.importe_total = float(total.quantize(CENTAVOS, rounding=ROUND_HALF_UP))


def _validar_detalle_comanda(db: Session, factura: Factura, detalle_comanda_id: int) -> DetalleComanda:
    """El detalle de comanda debe estar activo y pertenecer a la comanda de la factura."""
    dc = obtener_activo_o_404(db, DetalleComanda, detalle_comanda_id)
    if dc.comanda_id != factura.comanda_id:
        raise BadRequest()
    return dc


def _tomar_snapshot(detalle: DetalleFactura, dc: DetalleComanda) -> None:
    """Fija el precio unitario desde el producto; la promoción la decide el motor del grupo."""
    detalle.detalle_comanda_id = dc.id
    detalle.precio_unitario = float(dc.producto.precio)
    detalle.precio_final = float(Decimal(str(detalle.precio_unitario)) * detalle.cantidad)


def _recalcular_grupos(db: Session, factura: Factura, productos_ids: set[int]) -> None:
    """Recalcula cada grupo afectado (en orden estable) y luego el importe_total."""
    for producto_id in sorted(productos_ids):
        recalcular_producto(db, factura, producto_id)
    db.flush()
    db.refresh(factura)
    _recalcular_total(factura)


@router.post("", response_model=DetalleFacturaOut, status_code=201)
def crear_detalle_factura(
    datos: DetalleFacturaCreate,
    db: Session = Depends(get_db),
    hoy: date = Depends(obtener_hoy),
):
    dar_de_baja_vencidas(db, hoy)
    factura = obtener_activo_o_404(db, Factura, datos.factura_id)
    dc = _validar_detalle_comanda(db, factura, datos.detalle_comanda_id)
    detalle = DetalleFactura(factura_id=factura.id, cantidad=datos.cantidad)
    _tomar_snapshot(detalle, dc)
    db.add(detalle)
    db.flush()
    _recalcular_grupos(db, factura, {dc.producto_id})
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
def modificar_detalle_factura(
    id: int,
    datos: DetalleFacturaUpdate,
    db: Session = Depends(get_db),
    hoy: date = Depends(obtener_hoy),
):
    dar_de_baja_vencidas(db, hoy)
    detalle = obtener_activo_o_404(db, DetalleFactura, id)
    factura = detalle.factura
    afectados = {detalle.detalle_comanda.producto_id}
    cambios = datos.model_dump(exclude_unset=True)
    nuevo_dc = cambios.get("detalle_comanda_id")
    dc = None
    if nuevo_dc is not None and nuevo_dc != detalle.detalle_comanda_id:
        dc = _validar_detalle_comanda(db, factura, nuevo_dc)
        afectados.add(dc.producto_id)
    if "cantidad" in cambios:
        detalle.cantidad = cambios["cantidad"]
    if dc is not None:
        _tomar_snapshot(detalle, dc)
    db.flush()
    _recalcular_grupos(db, factura, afectados)
    db.commit()
    db.refresh(detalle)
    return detalle


@router.delete("/{id}", status_code=204)
def eliminar_detalle_factura(
    id: int,
    db: Session = Depends(get_db),
    hoy: date = Depends(obtener_hoy),
):
    dar_de_baja_vencidas(db, hoy)
    detalle = obtener_activo_o_404(db, DetalleFactura, id)
    producto_id = detalle.detalle_comanda.producto_id
    detalle.activo = False
    db.flush()
    _recalcular_grupos(db, detalle.factura, {producto_id})
    db.commit()
