from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.mozo.models import Mozo
from src.atencion.models import Atencion  # noqa: F401 — registra Atencion para Mozo.atenciones
from src.mozo import schema, exceptions


def crear_mozo(db: Session, mozo: schema.MozoCreate) -> schema.Mozo:
    _mozo = Mozo(**mozo.model_dump())
    db.add(_mozo)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        if "nro_legajo" in error_msg or "mozos.nro_legajo" in error_msg:
            raise exceptions.LegajoDuplicado()
        raise
    db.refresh(_mozo)
    return _mozo


def listar_mozos(
    db: Session,
    nombre: Optional[str] = None,
    nro_legajo: Optional[int] = None,
) -> List[schema.Mozo]:
    query = select(Mozo)
    if nombre:
        query = query.where(Mozo.nombre.ilike(f"%{nombre}%"))
    if nro_legajo is not None:
        query = query.where(Mozo.nro_legajo == nro_legajo)
    return db.scalars(query).all()


def leer_mozo(db: Session, nro_legajo: int) -> schema.Mozo:
    db_mozo = db.scalar(select(Mozo).where(Mozo.nro_legajo == nro_legajo))
    if db_mozo is None:
        raise exceptions.MozoNoEncontrado()
    return db_mozo


def _mozo_activo_por_id(db: Session, mozo_id: int) -> schema.Mozo:
    db_mozo = db.scalar(select(Mozo).where(Mozo.id == mozo_id))
    if db_mozo is None:
        raise exceptions.MozoNoEncontrado()
    if not db_mozo.estado:
        raise exceptions.MozoYaInactivo()
    return db_mozo


def modificar_mozo(db: Session, mozo_id: int, mozo: schema.MozoUpdate) -> schema.Mozo:
    db_mozo = _mozo_activo_por_id(db, mozo_id)
    update_data = mozo.model_dump(exclude_unset=True)

    if "nro_legajo" in update_data:
        existing = db.scalar(
            select(Mozo).where(Mozo.nro_legajo == update_data["nro_legajo"], Mozo.id != mozo_id)
        )
        if existing:
            raise exceptions.LegajoDuplicado()

    for key, value in update_data.items():
        setattr(db_mozo, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise exceptions.LegajoDuplicado()
    db.refresh(db_mozo)
    return db_mozo


def eliminar_mozo(db: Session, mozo_id: int) -> schema.Mozo:
    db_mozo = db.scalar(select(Mozo).where(Mozo.id == mozo_id))
    if db_mozo is None:
        raise exceptions.MozoNoEncontrado()
    if not db_mozo.estado:
        raise exceptions.MozoYaInactivo()
    if any(a.estado and a.fecha_hasta is None for a in db_mozo.atenciones):
        raise exceptions.MozoConAtencionesAbiertas()
    db_mozo.estado = False
    db.commit()
    db.refresh(db_mozo)
    return db_mozo


def reactivar_mozo(db: Session, mozo_id: int) -> schema.Mozo:
    db_mozo = db.scalar(select(Mozo).where(Mozo.id == mozo_id))
    if db_mozo is None:
        raise exceptions.MozoNoEncontrado()
    if db_mozo.estado:
        raise exceptions.MozoYaActivo()
    db_mozo.estado = True
    db.commit()
    db.refresh(db_mozo)
    return db_mozo
