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
    {
        "dni": "32112233",
        "first_name": "Diego",
        "last_name": "Rodríguez",
        "email": "diego.rodriguez@mail.com",
        "phone": "11-2233-4455",
    },
    {
        "dni": "33223344",
        "first_name": "Sofía",
        "last_name": "González",
        "email": "sofia.gonzalez@mail.com",
        "phone": "351-333-4455",
    },
    {
        "dni": "34334455",
        "first_name": "Nicolás",
        "last_name": "Pérez",
        "email": "nicolas.perez@mail.com",
        "phone": "261-444-5566",
    },
    {
        "dni": "35445566",
        "first_name": "Valentina",
        "last_name": "Díaz",
        "email": "valentina.diaz@mail.com",
        "phone": "379-555-6677",
    },
    {
        "dni": "36556677",
        "first_name": "Agustín",
        "last_name": "Martínez",
        "email": "agustin.martinez@mail.com",
        "phone": "342-666-7788",
    },
    {
        "dni": "37667788",
        "first_name": "Camila",
        "last_name": "Romero",
        "email": "camila.romero@mail.com",
        "phone": "223-777-8899",
    },
    {
        "dni": "38778899",
        "first_name": "Facundo",
        "last_name": "Suárez",
        "email": "facundo.suarez@mail.com",
        "phone": "11-8899-0011",
    },
    {
        "dni": "40889900",
        "first_name": "Julieta",
        "last_name": "Torres",
        "email": "julieta.torres@mail.com",
        "phone": "351-990-0112",
    },
    {
        "dni": "42990011",
        "first_name": "Ezequiel",
        "last_name": "Flores",
        "email": "ezequiel.flores@mail.com",
        "phone": "261-101-1223",
    },
    {
        "dni": "43101122",
        "first_name": "Rocío",
        "last_name": "Acosta",
        "email": "rocio.acosta@mail.com",
        "phone": "379-212-2334",
    },
    {
        "dni": "44212233",
        "first_name": "Franco",
        "last_name": "Benítez",
        "email": "franco.benitez@mail.com",
        "phone": "342-323-3445",
    },
    {
        "dni": "45323344",
        "first_name": "Milagros",
        "last_name": "Molina",
        "email": "milagros.molina@mail.com",
        "phone": "223-434-4556",
    },
    {
        "dni": "46434455",
        "first_name": "Bruno",
        "last_name": "Herrera",
        "email": "bruno.herrera@mail.com",
        "phone": "11-545-5667",
    },
    {
        "dni": "47545566",
        "first_name": "Antonella",
        "last_name": "Aguirre",
        "email": "antonella.aguirre@mail.com",
        "phone": "351-656-6778",
    },
    {
        "dni": "48656677",
        "first_name": "Tomás",
        "last_name": "Ibáñez",
        "email": "tomas.ibanez@mail.com",
        "phone": "261-767-7889",
    },
    {
        "dni": "49767788",
        "first_name": "Florencia",
        "last_name": "Cabrera",
        "email": "florencia.cabrera@mail.com",
        "phone": "379-878-8990",
    },
    {
        "dni": "50878899",
        "first_name": "Ignacio",
        "last_name": "Núñez",
        "email": "ignacio.nunez@mail.com",
        "phone": "342-989-9001",
    },
    {
        "dni": "51989900",
        "first_name": "Ariana",
        "last_name": "Ríos",
        "email": "ariana.rios@mail.com",
        "phone": "223-090-0112",
    },
    {
        "dni": "27090011",
        "first_name": "María Belén",
        "last_name": "Vega",
        "email": "mariabelen.vega@mail.com",
        "phone": "11-101-2233",
    },
    {
        "dni": "29101122",
        "first_name": "Federico",
        "last_name": "Silva",
        "email": "federico.silva@mail.com",
        "phone": "351-212-3345",
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
