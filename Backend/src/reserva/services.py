from datetime import date, datetime, time

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
    cant_comensales: int,
) -> None:
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
    ).first()
    if cliente is None:
        raise exceptions.RecursoNoEncontrado("El cliente no existe")

    _validar_capacidad_mesas(db, mesa_ids, cant_comensales)


def _validar_disponibilidad_mesas(
    db: Session,
    fecha: date,
    hora: time,
    mesa_ids: list[int],
    excluir_reserva_id: int | None = None,
) -> None:
    ids_mesas_solicitadas = set(mesa_ids)
    if not ids_mesas_solicitadas:
        return

    consulta = (
        db.query(models.Reserva)
        .join(
            models.ReservaMesa,
            models.ReservaMesa.reserva_id == models.Reserva.id,
        )
        .filter(
            models.ReservaMesa.mesa_id.in_(ids_mesas_solicitadas),
            models.Reserva.fecha == fecha,
            models.Reserva.hora == hora,
            models.Reserva.estado.in_(
                (EstadoReserva.PENDIENTE, EstadoReserva.CON_COMANDA)
            ),
        )
    )
    if excluir_reserva_id is not None:
        consulta = consulta.filter(models.Reserva.id != excluir_reserva_id)

    reserva_existente = consulta.first()
    if reserva_existente is not None:
        mesa_compartida = ids_mesas_solicitadas.intersection(
            reserva_existente.mesa_ids
        )
        mesa_id = min(mesa_compartida)
        raise exceptions.RecursoYaExiste(
            f"La mesa {mesa_id} ya está reservada para esa fecha y hora"
        )


def _validar_capacidad_mesas(
    db: Session,
    mesa_ids: list[int],
    cant_comensales: int,
) -> None:
    ids_mesas_solicitadas = set(mesa_ids)
    if not ids_mesas_solicitadas:
        raise exceptions.DatosReservaInvalidos(
            "La reserva debe tener al menos una mesa asignada"
        )

    mesas = db.query(Mesa).filter(
        Mesa.id.in_(ids_mesas_solicitadas),
    ).all()
    ids_mesas_existentes = {mesa.id for mesa in mesas}
    if ids_mesas_existentes != ids_mesas_solicitadas:
        raise exceptions.RecursoNoEncontrado(
            "Una o más mesas no existen"
        )
    capacidad_total = sum(mesa.capacidad for mesa in mesas)
    if capacidad_total < cant_comensales:
        raise exceptions.DatosReservaInvalidos(
            "La capacidad total de las mesas debe cubrir la cantidad de comensales"
        )


def crear_reserva(db: Session, reserva: schemas.ReservaCreate) -> models.Reserva:
    from src.detalleReserva import services as detalle_reserva_services

    datos = reserva.model_dump()
    mesa_ids = datos.pop("mesa_ids")
    detalles = [
        DetalleReservaCreate.model_validate(detalle)
        for detalle in datos.pop("detalles")
    ]
    _validar_relaciones(
        db,
        datos["cliente_id"],
        mesa_ids,
        datos["cant_comensales"],
    )
    _validar_disponibilidad_mesas(
        db,
        datos["fecha"],
        datos["hora"],
        mesa_ids,
    )

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

    if reserva_db.estado != EstadoReserva.PENDIENTE:
        raise exceptions.EstadoReservaInvalido(
            "Solo se pueden cancelar reservas pendientes"
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
    mesa_ids = datos.pop("mesa_ids")
    _validar_relaciones(
        db,
        datos["cliente_id"],
        mesa_ids,
        datos["cant_comensales"],
    )
    _validar_disponibilidad_mesas(
        db,
        datos["fecha"],
        datos["hora"],
        mesa_ids,
        excluir_reserva_id=reserva_id,
    )

    for atributo, valor in datos.items():
        setattr(reserva_db, atributo, valor)
    mesas_actuales = {
        asociacion.mesa_id: asociacion
        for asociacion in reserva_db.mesas_asociadas
    }
    reserva_db.mesas_asociadas = [
        mesas_actuales.get(mesa_id) or models.ReservaMesa(mesa_id=mesa_id)
        for mesa_id in dict.fromkeys(mesa_ids)
    ]

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
    if reserva_db.estado != EstadoReserva.PENDIENTE:
        raise exceptions.EstadoReservaInvalido(
            "Solo se pueden modificar reservas pendientes"
        )

    return reserva_db


def validar_fecha_hora_modificable(reserva: models.Reserva) -> None:
    fecha_hora_reserva = datetime.combine(reserva.fecha, reserva.hora)
    if fecha_hora_reserva <= datetime.now():
        raise exceptions.EstadoReservaInvalido(
            "No se puede cancelar una reserva después de su fecha y hora"
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
    reserva_db = obtener_reserva_modificable(db, reserva_id)
    mesa_db = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if mesa_db is None:
        raise exceptions.RecursoNoEncontrado("La mesa no existe")

    _validar_disponibilidad_mesas(
        db,
        reserva_db.fecha,
        reserva_db.hora,
        [mesa_id],
        excluir_reserva_id=reserva_id,
    )

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
    reserva_db = obtener_reserva_modificable(db, reserva_id)
    asociacion = db.query(models.ReservaMesa).filter(
        models.ReservaMesa.reserva_id == reserva_id,
        models.ReservaMesa.mesa_id == mesa_id,
    ).first()
    if asociacion is None:
        raise exceptions.RecursoNoEncontrado(
            "La mesa no está asociada a la reserva"
        )

    mesas_restantes = [
        asociacion_mesa.mesa_id
        for asociacion_mesa in reserva_db.mesas_asociadas
        if asociacion_mesa.mesa_id != mesa_id
    ]
    _validar_capacidad_mesas(
        db,
        mesas_restantes,
        reserva_db.cant_comensales,
    )
    db.delete(asociacion)
    db.commit()