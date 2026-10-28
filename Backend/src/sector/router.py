from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.sector import schema, services

router = APIRouter(prefix="/sectores", tags=["sectores"])


@router.post("/", response_model=schema.Sector)
def create_sector(sector: schema.SectorCreate, db: Session = Depends(get_db)):
    return services.crear_sector(db, sector)


@router.get("/", response_model=list[schema.Sector])
def read_sectores(
    nombre: str | None = Query(None, description="Filtrar por nombre (coincidencia parcial)"),
    db: Session = Depends(get_db),
):
    return services.listar_sectores(db, nombre=nombre)


@router.get("/{sector_id}", response_model=schema.Sector)
def read_sector(sector_id: int, db: Session = Depends(get_db)):
    return services.leer_sector(db, sector_id)


@router.put("/{sector_id}", response_model=schema.Sector)
def update_sector(sector_id: int, sector: schema.SectorUpdate, db: Session = Depends(get_db)):
    return services.modificar_sector(db, sector_id, sector)


@router.delete("/{sector_id}", response_model=schema.Sector)
def delete_sector(sector_id: int, db: Session = Depends(get_db)):
    return services.eliminar_sector(db, sector_id)


@router.patch("/{sector_id}/reactivar", response_model=schema.Sector)
def reactivate_sector(sector_id: int, db: Session = Depends(get_db)):
    return services.reactivar_sector(db, sector_id)
