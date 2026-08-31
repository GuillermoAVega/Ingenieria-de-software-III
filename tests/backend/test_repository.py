import pytest

from app.backend import repository
from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import ClientStatus, Customer


@pytest.fixture
def session():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)
    db = factory()
    try:
        yield db
    finally:
        db.close()


def test_insertar_cliente_persiste_con_estado_activo(session):
    customer = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    assert customer.status == ClientStatus.ACTIVE
    stored = session.query(Customer).filter_by(dni=30111222).one()
    assert stored.status == ClientStatus.ACTIVE


def test_duplicado_dni_exacto(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    assert repository.dni_exists(session, "30111222") is True


def test_duplicado_dni_normalizado_por_ceros_a_la_izquierda(session):
    repository.create_customer(
        session,
        dni="123456",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )

    assert repository.dni_exists(session, "0123456") is True


def test_duplicado_dni_con_cliente_existente_inactivo(session):
    customer = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    customer.status = ClientStatus.INACTIVE
    session.commit()

    assert repository.dni_exists(session, "30111222") is True


def test_dni_no_registrado_no_es_duplicado(session):
    assert repository.dni_exists(session, "30111222") is False
