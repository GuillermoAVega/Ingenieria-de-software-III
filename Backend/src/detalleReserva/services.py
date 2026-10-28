from sqlalchemy.orm import Session

from src.detalleReserva import models, schemas
from src.reserva import exceptions
from src.reserva.services import (
    obtener_reserva_activa,
    obtener_reserva_modificable,
)


def crear_detalles_reserva(
    db: Session,
    reserva_id: int,
    detalles: list[schemas.DetalleReservaCreate],
) -> list[models.DetalleReserva]:
    detalles_db = [
        models.DetalleReserva(
            reserva_id=reserva_id,
            **detalle.model_dump(),
        )
        for detalle in detalles
    ]
    db.add_all(detalles_db)
    return detalles_db


def listar_detalles_reserva(
    db: Session,
    reserva_id: int,
) -> list[models.DetalleReserva]:
    obtener_reserva_activa(db, reserva_id)
    return db.query(models.DetalleReserva).filter(
        models.DetalleReserva.reserva_id == reserva_id,
    ).all()


def agregar_detalle_reserva(
    db: Session,
    reserva_id: int,
    detalle: schemas.DetalleReservaCreate,
) -> models.DetalleReserva:
    obtener_reserva_modificable(db, reserva_id)
    detalle_existente = db.query(models.DetalleReserva).filter(
        models.DetalleReserva.reserva_id == reserva_id,
        models.DetalleReserva.producto_id == detalle.producto_id,
    ).first()
    if detalle_existente is not None:
        raise exceptions.RecursoYaExiste(
            "El producto ya está asociado a la reserva"
        )

    detalle_db = models.DetalleReserva(
        reserva_id=reserva_id,
        **detalle.model_dump(),
    )
    db.add(detalle_db)
    db.commit()
    db.refresh(detalle_db)
    return detalle_db


def quitar_detalle_reserva(
    db: Session,
    reserva_id: int,
    producto_id: int,
) -> None:
    obtener_reserva_modificable(db, reserva_id)
    detalle_db = db.query(models.DetalleReserva).filter(
        models.DetalleReserva.reserva_id == reserva_id,
        models.DetalleReserva.producto_id == producto_id,
    ).first()
    if detalle_db is None:
        raise exceptions.RecursoNoEncontrado(
            "El detalle no existe en la reserva"
        )

    db.delete(detalle_db)
    db.commit()