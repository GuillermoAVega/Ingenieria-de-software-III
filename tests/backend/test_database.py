from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import ClientStatus, Customer


def test_crear_tablas_sin_errores():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)


def test_dni_no_es_unico_a_nivel_de_base():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()

    session.add(
        Customer(
            dni=30111222,
            first_name="Juan",
            last_name="Perez",
            email="juan@dominio.com",
            phone="11-4444-5555",
            status=ClientStatus.ACTIVE,
        )
    )
    session.commit()

    session.add(
        Customer(
            dni=30111222,
            first_name="Ana",
            last_name="Lopez",
            email="ana@dominio.com",
            phone="11-2222-3333",
            status=ClientStatus.INACTIVE,
        )
    )
    session.commit()

    stored = session.query(Customer).filter_by(dni=30111222).all()
    assert len(stored) == 2
