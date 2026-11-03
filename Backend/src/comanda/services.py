from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.exceptions import BadRequest, NotFound
from src.mesa.models import Mesa
from src.atencion.models import Atencion
from src.models import Comanda, DetalleComanda
from src.reserva.estados import EstadoReserva
from src.reserva.models import Reserva

MINUTOS_ANTES_COMANDA_RESERVA = 15
MINUTOS_DESPUES_COMANDA_RESERVA = 30


def ocupar_mesas(mesas: list[Mesa]) -> None:
    for mesa in mesas:
        mesa.disponible = False


def liberar_mesas(mesas: list[Mesa]) -> None:
    for mesa in mesas:
        mesa.disponible = True


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


def asignar_mozo_para_mesas(db: Session, mesas: list[Mesa]) -> int:
    sector_ids = {mesa.sector_id for mesa in mesas}
    if len(sector_ids) != 1:
        raise BadRequest(
            detail="Las mesas de una comanda deben pertenecer al mismo sector"
        )

    hoy = date.today()
    atenciones = db.scalars(
        select(Atencion)
        .where(
            Atencion.sector_id == next(iter(sector_ids)),
            Atencion.estado.is_(True),
            Atencion.fecha_desde <= hoy,
            (Atencion.fecha_hasta.is_(None) | (Atencion.fecha_hasta >= hoy)),
        )
        .order_by(Atencion.id)
    ).all()
    if not atenciones:
        raise BadRequest(detail="No hay un mozo asignado al sector de la mesa")

    mozo_ids = [atencion.mozo_id for atencion in atenciones]
    comandas_abiertas = db.scalars(
        select(Comanda).where(
            Comanda.mozo_id.in_(mozo_ids),
            Comanda.activo.is_(True),
            Comanda.estado == "abierta",
        )
    ).all()
    tareas_por_mozo = {mozo_id: 0 for mozo_id in mozo_ids}
    for comanda in comandas_abiertas:
        tareas_por_mozo[comanda.mozo_id] += 1

    return min(mozo_ids, key=lambda mozo_id: (tareas_por_mozo[mozo_id], mozo_id))


def crear_comanda_desde_reserva(
    db: Session,
    reserva_id: int,
) -> Comanda:
    reserva = db.scalar(select(Reserva).where(Reserva.id == reserva_id))
    if reserva is None:
        raise NotFound(detail="La reserva no existe")
    if reserva.estado != EstadoReserva.PENDIENTE:
        raise BadRequest(detail="La reserva no está pendiente")

    ahora = datetime.now()
    fecha_hora_reserva = datetime.combine(reserva.fecha, reserva.hora)
    desde = fecha_hora_reserva - timedelta(minutes=MINUTOS_ANTES_COMANDA_RESERVA)
    hasta = fecha_hora_reserva + timedelta(minutes=MINUTOS_DESPUES_COMANDA_RESERVA)
    if ahora < desde or ahora > hasta:
        raise BadRequest(
            detail="La comanda solo puede crearse desde 15 minutos antes hasta 30 minutos despues de la reserva"
        )

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
    ocupar_mesas(mesas)
    db.add(comanda)
    reserva.estado = EstadoReserva.CON_COMANDA
    db.commit()
    db.refresh(comanda)
    return comanda
