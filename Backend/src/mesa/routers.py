from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.mesa import schemas, services


router = APIRouter(prefix="/mesas", tags=["MESAS"])


@router.get("", response_model=list[schemas.Mesa])
def listar_mesas(
    incluir_inactivas: bool = Query(False),
    db: Session = Depends(get_db),
):
    return services.listar_mesas(db, incluir_inactivas=incluir_inactivas).all()


@router.get("/{mesa_id}", response_model=schemas.Mesa)
def obtener_mesa(mesa_id: int, db: Session = Depends(get_db)):
    try:
        return services.obtener_mesa(db, mesa_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post("", response_model=schemas.Mesa, status_code=status.HTTP_201_CREATED)
def crear_mesa(mesa: schemas.MesaCreate, db: Session = Depends(get_db)):
    return services.crear_mesa(db, mesa)


@router.put("/{mesa_id}", response_model=schemas.Mesa)
def modificar_mesa(
    mesa_id: int,
    nuevos_datos: schemas.MesaUpdate,
    db: Session = Depends(get_db),
):
    try:
        return services.modificar_mesa(db, mesa_id, nuevos_datos)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete("/{mesa_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mesa(mesa_id: int, db: Session = Depends(get_db)):
    try:
        services.eliminar_mesa(db, mesa_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{mesa_id}/reactivar", response_model=schemas.Mesa)
def reactivar_mesa(mesa_id: int, db: Session = Depends(get_db)):
    try:
        services.restaurar_mesa(db, mesa_id)
        return services.obtener_mesa(db, mesa_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error