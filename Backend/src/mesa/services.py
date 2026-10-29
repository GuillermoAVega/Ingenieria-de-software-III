from sqlalchemy import select
from sqlalchemy.orm import Session

from src.mesa import models, schemas
from src.mesa.exceptions import SectorMesaInactivo, SectorMesaNoEncontrado
from src.sector.models import Sector


def _validar_sector_activo(db: Session, sector_id: int) -> None:
    sector = db.scalar(select(Sector).where(Sector.id == sector_id))
    if sector is None:
        raise SectorMesaNoEncontrado()
    if not sector.estado:
        raise SectorMesaInactivo()


def crear_mesa(db: Session, mesa: schemas.MesaCreate) -> models.Mesa:
    _validar_sector_activo(db, mesa.sector_id)
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

    _validar_sector_activo(db, nuevos_datos.sector_id)
    mesa_db.capacidad = nuevos_datos.capacidad
    mesa_db.disponible = nuevos_datos.disponible
    mesa_db.sector_id = nuevos_datos.sector_id

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


def listar_mesas(db: Session, incluir_inactivas: bool = False):
    query = db.query(models.Mesa)
    if not incluir_inactivas:
        query = query.filter(models.Mesa.estado.is_(True))
    return query