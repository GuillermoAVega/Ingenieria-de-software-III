from sqlalchemy import select
from sqlalchemy.orm import Session

from src.exceptions import BadRequest, NotFound
from src.mesa.models import Mesa
from src.models import Comanda, DetalleComanda
from src.reserva.estados import EstadoReserva
from src.reserva.models import Reserva


def obtener_mesas_disponibles(
    db: Session,
    mesa_ids: list[int],
) -> list[Mesa]:
    mesas = db.scalars(
        select(Mesa).where(
            Mesa.id.in_(mesa_ids),
            Mesa.estado.is_(True),
            Mesa.disponible.is_(True),
        )
    ).all()
    if len(mesas) != len(set(mesa_ids)):
        raise BadRequest(detail="Una o más mesas no están disponibles")
    return mesas


def crear_comanda_desde_reserva(
    db: Session,
    reserva_id: int,
) -> Comanda:
    reserva = db.scalar(select(Reserva).where(Reserva.id == reserva_id))
    if reserva is None:
        raise NotFound(detail="La reserva no existe")
    if reserva.estado != EstadoReserva.PENDIENTE:
        raise BadRequest(detail="La reserva no está pendiente")

    existente = db.scalar(
        select(Comanda).where(
            Comanda.reserva_id == reserva_id,
            Comanda.activo.is_(True),
        )
    )
    if existente is not None:
        raise BadRequest(detail="La reserva ya tiene una comanda")
    if not reserva.mesa_ids:
        raise BadRequest(detail="La reserva no tiene mesas asignadas")
    mesas = db.scalars(
        select(Mesa).where(Mesa.id.in_(reserva.mesa_ids))
    ).all()

    comanda = Comanda(
        fecha=reserva.fecha,
        hora=reserva.hora,
        mozo_id=None,
        mesa_id=reserva.mesa_ids[0],
        cliente_id=reserva.cliente_id,
        reserva_id=reserva.id,
        mesas_asociadas=mesas,
        detalles=[
            DetalleComanda(
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad_producto,
            )
            for detalle in reserva.detalles
        ],
    )
    db.add(comanda)
    reserva.estado = EstadoReserva.CON_COMANDA
    db.commit()
    db.refresh(comanda)
    return comanda
