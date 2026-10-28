from typing import List, Optional
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.atencion.models import Atencion
from src.mozo.models import Mozo
from src.sector.models import Sector
from src.atencion import schema, exceptions


def _validar_mozo_sector(db: Session, mozo_id: int, sector_id: int) -> None:
    db_mozo = db.scalar(select(Mozo).where(Mozo.id == mozo_id, Mozo.estado == True))
    if db_mozo is None:
        raise exceptions.MozoInvalido()
    db_sector = db.scalar(select(Sector).where(Sector.id == sector_id, Sector.estado == True))
    if db_sector is None:
        raise exceptions.SectorInvalido()


def crear_atencion(db: Session, atencion: schema.AtencionCreate) -> schema.Atencion:
    _validar_mozo_sector(db, atencion.mozo_id, atencion.sector_id)
    _atencion = Atencion(**atencion.model_dump())
    db.add(_atencion)
    db.commit()
    db.refresh(_atencion)
    return _atencion


def listar_atenciones(
    db: Session,
    mozo_id: Optional[int] = None,
    sector_id: Optional[int] = None,
) -> List[schema.Atencion]:
    query = select(Atencion)
    if mozo_id is not None:
        query = query.where(Atencion.mozo_id == mozo_id)
    if sector_id is not None:
        query = query.where(Atencion.sector_id == sector_id)
    return db.scalars(query).all()


def leer_atencion(db: Session, atencion_id: int) -> schema.Atencion:
    db_atencion = db.scalar(
        select(Atencion).where(Atencion.id == atencion_id, Atencion.estado == True)
    )
    if db_atencion is None:
        raise exceptions.AtencionNoEncontrada()
    return db_atencion


def modificar_atencion(
    db: Session, atencion_id: int, atencion: schema.AtencionUpdate
) -> schema.Atencion:
    db_atencion = leer_atencion(db, atencion_id)
    update_data = atencion.model_dump(exclude_unset=True)

    nueva_desde = update_data.get("fecha_desde", db_atencion.fecha_desde)
    nueva_hasta = update_data.get("fecha_hasta", db_atencion.fecha_hasta)
    if nueva_hasta is not None and nueva_desde is not None and nueva_hasta < nueva_desde:
        raise exceptions.FechaInvalida()

    if "mozo_id" in update_data or "sector_id" in update_data:
        _validar_mozo_sector(
            db,
            update_data.get("mozo_id", db_atencion.mozo_id),
            update_data.get("sector_id", db_atencion.sector_id),
        )

    for key, value in update_data.items():
        setattr(db_atencion, key, value)

    db.commit()
    db.refresh(db_atencion)
    return db_atencion


def eliminar_atencion(db: Session, atencion_id: int) -> schema.Atencion:
    db_atencion = db.scalar(select(Atencion).where(Atencion.id == atencion_id))
    if db_atencion is None:
        raise exceptions.AtencionNoEncontrada()
    if not db_atencion.estado:
        raise exceptions.AtencionYaInactiva()
    db_atencion.estado = False
    db.commit()
    db.refresh(db_atencion)
    return db_atencion
