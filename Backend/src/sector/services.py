import unicodedata
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.sector.models import Sector
from src.atencion.models import Atencion  # noqa: F401 — registra Atencion para Sector.atenciones
from src.sector import schema, exceptions


def _normalizar(texto: str) -> str:
    minusculas = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in minusculas if unicodedata.category(c) != "Mn")


def _nombre_en_uso(db: Session, nombre: str, exclude_id: Optional[int] = None) -> bool:
    query = select(Sector.id, Sector.nombre)
    if exclude_id is not None:
        query = query.where(Sector.id != exclude_id)
    objetivo = _normalizar(nombre)
    return any(_normalizar(n) == objetivo for _, n in db.execute(query))


def crear_sector(db: Session, sector: schema.SectorCreate) -> schema.Sector:
    if _nombre_en_uso(db, sector.nombre):
        raise exceptions.SectorNombreDuplicado()

    _sector = Sector(**sector.model_dump())
    db.add(_sector)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        if "nombre" in error_msg or "sectores.nombre" in error_msg:
            raise exceptions.SectorNombreDuplicado()
        raise
    db.refresh(_sector)
    return _sector


def listar_sectores(db: Session, nombre: Optional[str] = None) -> List[schema.Sector]:
    query = select(Sector)
    if nombre:
        query = query.where(Sector.nombre.ilike(f"%{nombre}%"))
    return db.scalars(query).all()


def leer_sector(db: Session, sector_id: int) -> schema.Sector:
    db_sector = db.scalar(select(Sector).where(Sector.id == sector_id))
    if db_sector is None:
        raise exceptions.SectorNoEncontrado()
    return db_sector


def _sector_activo_por_id(db: Session, sector_id: int) -> schema.Sector:
    db_sector = leer_sector(db, sector_id)
    if not db_sector.estado:
        raise exceptions.SectorYaInactivo()
    return db_sector


def modificar_sector(db: Session, sector_id: int, sector: schema.SectorUpdate) -> schema.Sector:
    db_sector = _sector_activo_por_id(db, sector_id)
    update_data = sector.model_dump(exclude_unset=True)

    if "nombre" in update_data and _nombre_en_uso(
        db, update_data["nombre"], exclude_id=sector_id
    ):
        raise exceptions.SectorNombreDuplicado()

    for key, value in update_data.items():
        setattr(db_sector, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise exceptions.SectorNombreDuplicado()
    db.refresh(db_sector)
    return db_sector


def eliminar_sector(db: Session, sector_id: int) -> schema.Sector:
    db_sector = db.scalar(select(Sector).where(Sector.id == sector_id))
    if db_sector is None:
        raise exceptions.SectorNoEncontrado()
    if not db_sector.estado:
        raise exceptions.SectorYaInactivo()
    if any(a.estado and a.fecha_hasta is None for a in db_sector.atenciones):
        raise exceptions.SectorConAtencionesAbiertas()
    db_sector.estado = False
    db.commit()
    db.refresh(db_sector)
    return db_sector


def reactivar_sector(db: Session, sector_id: int) -> schema.Sector:
    db_sector = db.scalar(select(Sector).where(Sector.id == sector_id))
    if db_sector is None:
        raise exceptions.SectorNoEncontrado()
    if db_sector.estado:
        raise exceptions.SectorYaActivo()
    db_sector.estado = True
    db.commit()
    db.refresh(db_sector)
    return db_sector
