from datetime import datetime

from sqlalchemy.orm import Session

from src.cliente.models import Cliente
from src.detalleReserva.schemas import DetalleReservaCreate
from src.mesa.models import Mesa
from src.reserva import exceptions, models, schemas
from src.reserva.estados import EstadoReserva


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
    from src.detalleReserva import services as detalle_reserva_services

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

    if reserva_db.estado == EstadoReserva.CANCELADA:
        raise exceptions.EstadoReservaInvalido(
            "La reserva ya está cancelada"
        )

    validar_fecha_hora_modificable(reserva_db)
    reserva_db.estado = EstadoReserva.CANCELADA
    db.commit()


def modificar_reserva(
    db: Session,
    reserva_id: int,
    nuevos_datos: schemas.ReservaUpdate,
) -> models.Reserva:
    reserva_db = obtener_reserva_modificable(db, reserva_id)
    datos = nuevos_datos.model_dump()
    _validar_relaciones(db, datos["cliente_id"], [])

    for atributo, valor in datos.items():
        setattr(reserva_db, atributo, valor)

    db.commit()
    db.refresh(reserva_db)
    return reserva_db


def obtener_reserva(db: Session, reserva_id: int) -> models.Reserva:
    reserva_db = db.query(models.Reserva).filter(
        models.Reserva.id == reserva_id,
    ).first()

    if reserva_db is None:
        raise exceptions.RecursoNoEncontrado("La reserva no existe")

    return reserva_db


def obtener_reserva_modificable(
    db: Session,
    reserva_id: int,
) -> models.Reserva:
    reserva_db = obtener_reserva(db, reserva_id)
    if reserva_db.estado == EstadoReserva.CANCELADA:
        raise exceptions.EstadoReservaInvalido(
            "No se puede modificar una reserva cancelada"
        )

    validar_fecha_hora_modificable(reserva_db)
    return reserva_db


def validar_fecha_hora_modificable(reserva: models.Reserva) -> None:
    fecha_hora_reserva = datetime.combine(reserva.fecha, reserva.hora)
    if fecha_hora_reserva <= datetime.now():
        raise exceptions.EstadoReservaInvalido(
            "No se puede modificar una reserva después de su fecha y hora"
        )


def listar_reservas(db: Session):
    return db.query(models.Reserva)


def listar_mesas_reserva(db: Session, reserva_id: int) -> list[Mesa]:
    obtener_reserva(db, reserva_id)
    return (
        db.query(Mesa)
        .join(models.ReservaMesa, models.ReservaMesa.mesa_id == Mesa.id)
        .filter(models.ReservaMesa.reserva_id == reserva_id)
        .all()
    )


def agregar_mesa_reserva(
    db: Session,
    reserva_id: int,
    mesa_id: int,
) -> Mesa:
    obtener_reserva_modificable(db, reserva_id)
    mesa_db = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if mesa_db is None:
        raise exceptions.RecursoNoEncontrado("La mesa no existe")

    asociacion = db.query(models.ReservaMesa).filter(
        models.ReservaMesa.reserva_id == reserva_id,
        models.ReservaMesa.mesa_id == mesa_id,
    ).first()
    if asociacion is not None:
        raise exceptions.RecursoYaExiste(
            "La mesa ya está asociada a la reserva"
        )

    db.add(models.ReservaMesa(reserva_id=reserva_id, mesa_id=mesa_id))
    db.commit()
    return mesa_db


def quitar_mesa_reserva(db: Session, reserva_id: int, mesa_id: int) -> None:
    obtener_reserva_modificable(db, reserva_id)
    asociacion = db.query(models.ReservaMesa).filter(
        models.ReservaMesa.reserva_id == reserva_id,
        models.ReservaMesa.mesa_id == mesa_id,
    ).first()
    if asociacion is None:
        raise exceptions.RecursoNoEncontrado(
            "La mesa no está asociada a la reserva"
        )

    db.delete(asociacion)
    db.commit()