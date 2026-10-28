from sqlalchemy.orm import Session

from src.mesa import models, schemas


def crear_mesa(db: Session, mesa: schemas.MesaCreate) -> models.Mesa:
    mesa_db = models.Mesa(**mesa.model_dump())
    db.add(mesa_db)
    db.commit()
    db.refresh(mesa_db)
    return mesa_db


def eliminar_mesa(db: Session, mesa_id: int) -> str:
    mesa_db = db.query(models.Mesa).filter(
        models.Mesa.id == mesa_id
    ).first()

    if not mesa_db:
        raise ValueError("La mesa no existe")

    if not mesa_db.estado:
        raise ValueError("La mesa ya está dada de baja")

    mesa_db.estado = False
    db.commit()

    return "Mesa dada de baja correctamente"


def restaurar_mesa(db: Session, mesa_id: int) -> str:
    mesa_db = db.query(models.Mesa).filter(
        models.Mesa.id == mesa_id
    ).first()

    if not mesa_db:
        raise ValueError("La mesa no existe")

    if mesa_db.estado:
        raise ValueError("La mesa ya está activa")

    mesa_db.estado = True
    db.commit()

    return "Mesa restaurada correctamente"


def modificar_mesa(
    db: Session,
    mesa_id: int,
    nuevos_datos: schemas.MesaUpdate,
) -> models.Mesa:
    mesa_db = db.query(models.Mesa).filter(
        models.Mesa.id == mesa_id,
        models.Mesa.estado.is_(True),
    ).first()

    if not mesa_db:
        raise ValueError("La mesa no existe")

    mesa_db.capacidad = nuevos_datos.capacidad
    mesa_db.disponible = nuevos_datos.disponible

    db.commit()
    db.refresh(mesa_db)

    return mesa_db


def obtener_mesa(db: Session, mesa_id: int) -> models.Mesa:
    mesa_db = db.query(models.Mesa).filter(
        models.Mesa.id == mesa_id,
        models.Mesa.estado.is_(True),
    ).first()

    if not mesa_db:
        raise ValueError("La mesa no existe")

    return mesa_db


def listar_mesas(db: Session):
    return db.query(models.Mesa).filter(models.Mesa.estado.is_(True))