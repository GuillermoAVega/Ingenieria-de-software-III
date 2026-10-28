from sqlalchemy.orm import Session

from src.detalleReserva import models, schemas


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