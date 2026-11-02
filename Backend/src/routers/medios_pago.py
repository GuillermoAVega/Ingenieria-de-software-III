from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.exceptions import BadRequest
from src.models import ComprobantePago, MedioPago
from src.schemas.medio_pago import MedioPagoCreate, MedioPagoOut, MedioPagoUpdate
from src.utils import obtener_activo_o_404

router = APIRouter(prefix="/medios-pago", tags=["Medios de pago"])


def _validar_descripcion_unica(db: Session, descripcion: str, excluir_id: int | None = None):
    existente = db.scalars(select(MedioPago).where(MedioPago.descripcion == descripcion)).first()
    if existente and existente.id != excluir_id:
        raise BadRequest()


@router.post("", response_model=MedioPagoOut, status_code=201)
def crear_medio_pago(datos: MedioPagoCreate, db: Session = Depends(get_db)):
    _validar_descripcion_unica(db, datos.descripcion)
    medio = MedioPago(**datos.model_dump())
    db.add(medio)
    db.commit()
    db.refresh(medio)
    return medio


@router.get("", response_model=list[MedioPagoOut])
def listar_medios_pago(
    activo: bool | None = True, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    q = select(MedioPago).offset(skip).limit(limit)
    if activo is not None:
        q = q.where(MedioPago.activo == activo)
    return db.scalars(q).all()


@router.get("/{id}", response_model=MedioPagoOut)
def obtener_medio_pago(id: int, db: Session = Depends(get_db)):
    return obtener_activo_o_404(db, MedioPago, id)


@router.put("/{id}", response_model=MedioPagoOut)
def modificar_medio_pago(id: int, datos: MedioPagoUpdate, db: Session = Depends(get_db)):
    medio = obtener_activo_o_404(db, MedioPago, id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "descripcion" in cambios:
        _validar_descripcion_unica(db, cambios["descripcion"], excluir_id=id)
    for campo, valor in cambios.items():
        setattr(medio, campo, valor)
    db.commit()
    db.refresh(medio)
    return medio


@router.delete("/{id}", status_code=204)
def eliminar_medio_pago(id: int, db: Session = Depends(get_db)):
    medio = obtener_activo_o_404(db, MedioPago, id)
    en_uso = db.scalars(
        select(ComprobantePago).where(
            ComprobantePago.medio_pago_id == id, ComprobantePago.activo
        )
    ).first()
    if en_uso:
        raise BadRequest()
    medio.activo = False
    db.commit()
