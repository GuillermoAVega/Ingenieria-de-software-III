from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.cliente import schemas, services
from src.database import get_db


router = APIRouter(prefix="/clientes", tags=["CLIENTES"])


@router.get("", response_model=list[schemas.Cliente])
def listar_clientes(db: Session = Depends(get_db)):
    return services.listar_clientes(db).all()


@router.get("/{cliente_dni}", response_model=schemas.Cliente)
def obtener_cliente(cliente_dni: str, db: Session = Depends(get_db)):
    try:
        return services.obtener_cliente(db, cliente_dni)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post("", response_model=schemas.Cliente, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    try:
        return services.crear_cliente(db, cliente)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.put("/{cliente_dni}", response_model=schemas.Cliente)
def modificar_cliente(
    cliente_dni: str,
    nuevos_datos: schemas.ClienteUpdate,
    db: Session = Depends(get_db),
):
    try:
        cliente = services.obtener_cliente(db, cliente_dni)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    try:
        services.modificar_cliente(db, cliente.dni, nuevos_datos)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_dni}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(cliente_dni: str, db: Session = Depends(get_db)):
    try:
        services.eliminar_cliente(db, cliente_dni)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)