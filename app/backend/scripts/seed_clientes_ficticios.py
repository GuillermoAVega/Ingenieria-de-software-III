from sqlalchemy.orm import Session

from app.backend import core, repository

FICTITIOUS_CUSTOMERS: list[dict[str, str]] = [
    {
        "dni": "30111222",
        "first_name": "María José",
        "last_name": "Fernández",
        "email": "mariaj@correo.com",
        "phone": "11-4444-5555",
    },
    {
        "dni": "28999888",
        "first_name": "Juan Ignacio",
        "last_name": "Gómez",
        "email": "jgomez@mail.com",
        "phone": "1145556666",
    },
    {
        "dni": "41234567",
        "first_name": "Ana",
        "last_name": "López",
        "email": "analopez@dominio.com",
        "phone": "351-222-3333",
    },
    {
        "dni": "0987654",
        "first_name": "Martín",
        "last_name": "Álvarez",
        "email": "martin@correo.com",
        "phone": "261-555-1234",
    },
    {
        "dni": "39456123",
        "first_name": "Lucía",
        "last_name": "Sánchez",
        "email": "lucia@mail.com",
        "phone": "3794441234",
    },
]


def _is_valid_customer(data: dict[str, str]) -> bool:
    return (
        core.validate_name(data["first_name"])
        and core.validate_name(data["last_name"])
        and core.validate_email(data["email"])
        and core.validate_phone(data["phone"])
        and core.validate_dni_format(data["dni"])
    )


def seed_clientes_ficticios(session: Session) -> int:
    inserted = 0
    for data in FICTITIOUS_CUSTOMERS:
        if not _is_valid_customer(data):
            continue
        if repository.dni_exists(session, data["dni"]):
            continue
        repository.create_customer(session, **data)
        inserted += 1
    return inserted


def main() -> None:
    from app.backend.database import Base, create_db_engine, create_session_factory

    engine = create_db_engine()
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()
    try:
        inserted = seed_clientes_ficticios(session)
        print(f"Clientes ficticios insertados: {inserted}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
