import pytest
from sqlalchemy.exc import IntegrityError

from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import ClientStatus, Customer, Product


def test_crear_tablas_sin_errores():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)


def test_sku_unico_rechaza_duplicado_exacto():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()

    session.add(
        Product(
            sku="ABC123",
            name="Coca-Cola 500ml",
            brand="Coca-Cola",
            description="Botella descartable",
            unit_price=350.5,
            stock=100,
        )
    )
    session.commit()

    session.add(
        Product(
            sku="ABC123",
            name="Otro producto",
            brand="Otra marca",
            description=None,
            unit_price=10.0,
            stock=5,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


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
