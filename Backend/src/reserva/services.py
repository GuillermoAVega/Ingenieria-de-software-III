from sqlalchemy.orm import Session

from src.cliente.models import Cliente
from src.detalleReserva import services as detalle_reserva_services
from src.detalleReserva.schemas import DetalleReservaCreate
from src.mesa.models import Mesa
from src.reserva import exceptions, models, schemas


def _validar_relaciones(
    db: Session,
    cliente_id: int,
    mesa_ids: list[int],
) -> None:
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
    ).first()
    if cliente is None:
        raise exceptions.RecursoNoEncontrado("El cliente no existe")

    ids_mesas_solicitadas = set(mesa_ids)
    if not ids_mesas_solicitadas:
        return

    mesas = db.query(Mesa).filter(
        Mesa.id.in_(ids_mesas_solicitadas),
    ).all()
    ids_mesas_existentes = {mesa.id for mesa in mesas}
    if ids_mesas_existentes != ids_mesas_solicitadas:
        raise exceptions.RecursoNoEncontrado(
            "Una o más mesas no existen"
        )


def crear_reserva(db: Session, reserva: schemas.ReservaCreate) -> models.Reserva:
    datos = reserva.model_dump()
    mesa_ids = datos.pop("mesa_ids")
    detalles = [
        DetalleReservaCreate.model_validate(detalle)
        for detalle in datos.pop("detalles")
    ]
    _validar_relaciones(db, datos["cliente_id"], mesa_ids)

    reserva_db = models.Reserva(**datos)
    reserva_db.mesas_asociadas = [
        models.ReservaMesa(mesa_id=mesa_id)
        for mesa_id in dict.fromkeys(mesa_ids)
    ]
    db.add(reserva_db)
    db.flush()
    detalle_reserva_services.crear_detalles_reserva(
        db,
        reserva_db.id,
        detalles,
    )
    db.commit()
    db.refresh(reserva_db)
    return reserva_db


def cancelar_reserva(db: Session, reserva_id: int) -> None:
    reserva_db = db.query(models.Reserva).filter(
        models.Reserva.id == reserva_id
    ).first()

    if reserva_db is None:
        raise exceptions.RecursoNoEncontrado("La reserva no existe")

    if not reserva_db.estado:
        raise exceptions.EstadoReservaInvalido(
            "La reserva ya está cancelada"
        )

    reserva_db.estado = False
    db.commit()


def modificar_reserva(
    db: Session,
    reserva_id: int,
    nuevos_datos: schemas.ReservaUpdate,
) -> models.Reserva:
    reserva_db = obtener_reserva(db, reserva_id)
    datos = nuevos_datos.model_dump()
    mesa_ids = datos.pop("mesa_ids")
    detalles = [
        DetalleReservaCreate.model_validate(detalle)
        for detalle in datos.pop("detalles")
    ]
    _validar_relaciones(db, datos["cliente_id"], mesa_ids)

    for atributo, valor in datos.items():
        setattr(reserva_db, atributo, valor)
    reserva_db.detalles = []
    db.flush()
    detalle_reserva_services.crear_detalles_reserva(
        db,
        reserva_db.id,
        detalles,
    )
    reserva_db.mesas_asociadas = [
        models.ReservaMesa(mesa_id=mesa_id)
        for mesa_id in dict.fromkeys(mesa_ids)
    ]

    db.commit()
    db.refresh(reserva_db)
    return reserva_db


def obtener_reserva(db: Session, reserva_id: int) -> models.Reserva:
    reserva_db = db.query(models.Reserva).filter(
        models.Reserva.id == reserva_id,
        models.Reserva.estado.is_(True),
    ).first()

    if reserva_db is None:
        raise exceptions.RecursoNoEncontrado("La reserva no existe")

    return reserva_db


def listar_reservas(db: Session):
    return db.query(models.Reserva).filter(models.Reserva.estado.is_(True))