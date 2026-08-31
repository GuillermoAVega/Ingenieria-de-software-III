from sqlalchemy.orm import Session

from app.backend import core
from app.backend.models import Customer


def dni_exists(session: Session, dni: str) -> bool:
    normalized_dni = core.normalize_dni(dni)
    return (
        session.query(Customer).filter(Customer.dni == normalized_dni).first()
        is not None
    )


def create_customer(
    session: Session,
    dni: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
) -> Customer:
    customer = Customer(
        dni=core.normalize_dni(dni),
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        status=core.initial_status(),
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer
