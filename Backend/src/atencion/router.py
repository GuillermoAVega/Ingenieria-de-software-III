from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.atencion import schema, services

router = APIRouter(prefix="/atenciones", tags=["atenciones"])


@router.post("/", response_model=schema.Atencion)
def create_atencion(atencion: schema.AtencionCreate, db: Session = Depends(get_db)):
    return services.crear_atencion(db, atencion)


@router.get("/", response_model=list[schema.Atencion])
def read_atenciones(
    mozo_id: int | None = Query(None, description="Filtrar por mozo"),
    sector_id: int | None = Query(None, description="Filtrar por sector"),
    db: Session = Depends(get_db),
):
    return services.listar_atenciones(db, mozo_id=mozo_id, sector_id=sector_id)


@router.get("/{atencion_id}", response_model=schema.Atencion)
def read_atencion(atencion_id: int, db: Session = Depends(get_db)):
    return services.leer_atencion(db, atencion_id)


@router.put("/{atencion_id}", response_model=schema.Atencion)
def update_atencion(
    atencion_id: int, atencion: schema.AtencionUpdate, db: Session = Depends(get_db)
):
    return services.modificar_atencion(db, atencion_id, atencion)


@router.delete("/{atencion_id}", response_model=schema.Atencion)
def delete_atencion(atencion_id: int, db: Session = Depends(get_db)):
    return services.eliminar_atencion(db, atencion_id)
