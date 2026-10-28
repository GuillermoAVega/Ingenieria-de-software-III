from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.mozo import schema, services

router = APIRouter(prefix="/mozos", tags=["mozos"])


@router.post("/", response_model=schema.Mozo)
def create_mozo(mozo: schema.MozoCreate, db: Session = Depends(get_db)):
    return services.crear_mozo(db, mozo)


@router.get("/", response_model=list[schema.Mozo])
def read_mozos(
    nombre: str | None = Query(None, description="Filtrar por nombre (coincidencia parcial)"),
    nro_legajo: int | None = Query(None, gt=0, description="Filtrar por nro_legajo"),
    db: Session = Depends(get_db),
):
    return services.listar_mozos(db, nombre=nombre, nro_legajo=nro_legajo)


@router.get("/{nro_legajo}", response_model=schema.Mozo)
def read_mozo(nro_legajo: int, db: Session = Depends(get_db)):
    return services.leer_mozo(db, nro_legajo)


@router.put("/{mozo_id}", response_model=schema.Mozo)
def update_mozo(mozo_id: int, mozo: schema.MozoUpdate, db: Session = Depends(get_db)):
    return services.modificar_mozo(db, mozo_id, mozo)


@router.delete("/{mozo_id}", response_model=schema.Mozo)
def delete_mozo(mozo_id: int, db: Session = Depends(get_db)):
    return services.eliminar_mozo(db, mozo_id)


@router.patch("/{mozo_id}/reactivar", response_model=schema.Mozo)
def reactivate_mozo(mozo_id: int, db: Session = Depends(get_db)):
    return services.reactivar_mozo(db, mozo_id)
