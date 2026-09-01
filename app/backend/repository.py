from sqlalchemy.orm import Session

from app.backend import core
from app.backend.models import ClientStatus, Customer


def dni_exists(session: Session, dni: str) -> bool:
    normalized_dni = core.normalize_dni(dni)
    return (
        session.query(Customer).filter(Customer.dni == normalized_dni).first()
        is not None
    )


def find_by_dni(session: Session, dni: str) -> Customer | None:
    normalized_dni = core.try_normalize_dni(dni)
    if normalized_dni is None:
        return None
    return (
        session.query(Customer)
        .filter(Customer.dni == normalized_dni)
        .order_by(Customer.status != ClientStatus.ACTIVE)
        .first()
    )


def dni_belongs_to_another_active_customer(
    session: Session, dni: str, exclude_id: int
) -> bool:
    normalized_dni = core.try_normalize_dni(dni)
    if normalized_dni is None:
        return False
    return (
        session.query(Customer)
        .filter(
            Customer.dni == normalized_dni,
            Customer.id != exclude_id,
            Customer.status == ClientStatus.ACTIVE,
        )
        .first()
        is not None
    )


def update_customer(
    session: Session,
    customer: Customer,
    *,
    dni: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
) -> Customer:
    customer.dni = core.normalize_dni(dni)
    customer.first_name = first_name
    customer.last_name = last_name
    customer.email = email
    customer.phone = phone
    session.commit()
    session.refresh(customer)
    return customer


def deactivate_by_dni(session: Session, dni: str) -> Customer | None:
    customer = find_by_dni(session, dni)
    if customer is None:
        return None
    customer.status = ClientStatus.INACTIVE
    session.commit()
    session.refresh(customer)
    return customer


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
