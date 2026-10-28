from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.detalleReserva import services as detalle_reserva_services
from src.detalleReserva import schemas as detalle_reserva_schemas
from src.mesa import schemas as mesa_schemas
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
    except exceptions.EstadoReservaInvalido as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/{reserva_id}/mesas",
    response_model=list[mesa_schemas.Mesa],
)
def listar_mesas_reserva(reserva_id: int, db: Session = Depends(get_db)):
    try:
        return services.listar_mesas_reserva(db, reserva_id)
    except exceptions.RecursoNoEncontrado as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/{reserva_id}/mesas",
    response_model=mesa_schemas.Mesa,
    status_code=status.HTTP_201_CREATED,
)
def agregar_mesa_reserva(
    reserva_id: int,
    datos: schemas.ReservaMesaCreate,
    db: Session = Depends(get_db),
):
    try:
        return services.agregar_mesa_reserva(
            db,
            reserva_id,
            datos.mesa_id,
        )
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
    except exceptions.RecursoYaExiste as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete(
    "/{reserva_id}/mesas/{mesa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def quitar_mesa_reserva(
    reserva_id: int,
    mesa_id: int,
    db: Session = Depends(get_db),
):
    try:
        services.quitar_mesa_reserva(db, reserva_id, mesa_id)
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


@router.get(
    "/{reserva_id}/detalles",
    response_model=list[detalle_reserva_schemas.DetalleReserva],
)
def listar_detalles_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
):
    try:
        return detalle_reserva_services.listar_detalles_reserva(
            db,
            reserva_id,
        )
    except exceptions.RecursoNoEncontrado as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/{reserva_id}/detalles",
    response_model=detalle_reserva_schemas.DetalleReserva,
    status_code=status.HTTP_201_CREATED,
)
def agregar_detalle_reserva(
    reserva_id: int,
    detalle: detalle_reserva_schemas.DetalleReservaCreate,
    db: Session = Depends(get_db),
):
    try:
        return detalle_reserva_services.agregar_detalle_reserva(
            db,
            reserva_id,
            detalle,
        )
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
    except exceptions.RecursoYaExiste as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete(
    "/{reserva_id}/detalles/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def quitar_detalle_reserva(
    reserva_id: int,
    producto_id: int,
    db: Session = Depends(get_db),
):
    try:
        detalle_reserva_services.quitar_detalle_reserva(
            db,
            reserva_id,
            producto_id,
        )
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
