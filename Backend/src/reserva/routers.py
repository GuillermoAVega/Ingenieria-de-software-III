from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.reserva import exceptions, schemas, services


router = APIRouter(prefix="/reservas", tags=["RESERVAS"])


@router.get("", response_model=list[schemas.Reserva])
def listar_reservas(db: Session = Depends(get_db)):
    return services.listar_reservas(db).all()


@router.get("/{reserva_id}", response_model=schemas.Reserva)
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    try:
        return services.obtener_reserva(db, reserva_id)
    except exceptions.RecursoNoEncontrado as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post("", response_model=schemas.Reserva, status_code=status.HTTP_201_CREATED)
def crear_reserva(
    reserva: schemas.ReservaCreate,
    db: Session = Depends(get_db),
):
    try:
        return services.crear_reserva(db, reserva)
    except exceptions.RecursoNoEncontrado as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.put("/{reserva_id}", response_model=schemas.Reserva)
def modificar_reserva(
    reserva_id: int,
    nuevos_datos: schemas.ReservaUpdate,
    db: Session = Depends(get_db),
):
    try:
        return services.modificar_reserva(db, reserva_id, nuevos_datos)
    except exceptions.RecursoNoEncontrado as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    try:
        services.cancelar_reserva(db, reserva_id)
    except exceptions.RecursoNoEncontrado as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except exceptions.EstadoReservaInvalido as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)

