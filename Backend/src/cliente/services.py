from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.cliente import models, schemas

def crear_cliente(db: Session, cliente: schemas.ClienteCreate) -> schemas.Cliente:
    cliente_db = models.Cliente(**cliente.model_dump())
    db.add(cliente_db)
    try:
        db.commit()
        db.refresh(cliente_db)
        return cliente_db
    except IntegrityError:
        db.rollback()
        raise ValueError("El cliente ya se encuentra registrado")

def eliminar_cliente(db: Session, cliente_dni: str) -> str:
    cliente_db = db.query(models.Cliente).filter(
        models.Cliente.dni == cliente_dni
    ).first()

    if not cliente_db:
        raise ValueError("El cliente no existe")
    
    if not cliente_db.estado:
        raise ValueError("El cliente ya está dado de baja")
    
    cliente_db.estado = False
    db.commit()

    return "Cliente dado de baja correctamente"

def restaurar_cliente(db: Session, cliente_dni: str) -> str:
    cliente_db = db.query(models.Cliente).filter(
        models.Cliente.dni == cliente_dni
    ).first()

    if not cliente_db:
        raise ValueError("El cliente no existe")

    if cliente_db.estado:
        raise ValueError("El cliente ya está activo")

    cliente_db.estado = True
    db.commit()

    return "Cliente restaurado correctamente"

def modificar_cliente(
    db: Session,
    cliente_dni: str,
    nuevos_datos: schemas.ClienteUpdate
) -> str:

    cliente_db = db.query(models.Cliente).filter(
        models.Cliente.dni == cliente_dni,
        models.Cliente.estado.is_(True),
    ).first()

    if not cliente_db:
        raise ValueError("El cliente no existe")

    if nuevos_datos.dni != cliente_db.dni:

        dni_en_uso = db.query(models.Cliente).filter(
            models.Cliente.dni == nuevos_datos.dni,
            models.Cliente.id != cliente_db.id
        ).first()

        if dni_en_uso:
            raise ValueError("El DNI ya está en uso")

    cliente_db.dni = nuevos_datos.dni
    cliente_db.nombre = nuevos_datos.nombre
    cliente_db.apellido = nuevos_datos.apellido
    cliente_db.telefono = nuevos_datos.telefono

    db.commit()
    db.refresh(cliente_db)

    return "Cliente modificado correctamente"

def obtener_cliente(db: Session, cliente_dni: str):

    cliente_db = db.query(models.Cliente).filter(
        models.Cliente.dni == cliente_dni,
        models.Cliente.estado.is_(True),
    ).first()

    if not cliente_db:
        raise ValueError("El cliente no existe")

    return cliente_db

def listar_clientes(
    db: Session
):
    return db.query(models.Cliente).filter(models.Cliente.estado.is_(True))