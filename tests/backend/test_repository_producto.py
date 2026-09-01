import pytest

from app.backend import repository_producto
from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import Product


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


def _create_product(session, **overrides):
    defaults = {
        "sku": "ABC123",
        "name": "Coca-Cola 500ml",
        "brand": "Coca-Cola",
        "description": "Botella descartable",
        "unit_price": 350.5,
        "stock": 100,
    }
    defaults.update(overrides)
    product = Product(**defaults)
    session.add(product)
    session.commit()
    return product


def test_sku_exists_detecta_duplicado_exacto(session):
    _create_product(session, sku="ABC123")

    assert repository_producto.sku_exists(session, "ABC123") is True


def test_sku_exists_detecta_duplicado_insensible_a_mayusculas(session):
    _create_product(session, sku="ABC123")

    assert repository_producto.sku_exists(session, "abc123") is True


def test_sku_exists_false_si_no_esta_registrado(session):
    assert repository_producto.sku_exists(session, "XYZ999") is False


def test_create_product_persiste_con_los_valores_ingresados(session):
    product = repository_producto.create_product(
        session,
        sku="ABC123",
        name="Coca-Cola 500ml",
        brand="Coca-Cola",
        description="Botella descartable",
        unit_price="350.50",
        stock="100",
    )

    assert product.sku == "ABC123"
    assert product.unit_price == 350.5
    assert product.stock == 100
    stored = session.query(Product).filter_by(sku="ABC123").one()
    assert stored.description == "Botella descartable"


def test_create_product_permite_descripcion_vacia(session):
    product = repository_producto.create_product(
        session,
        sku="XYZ999",
        name="Producto sin descripción",
        brand="Marca",
        description="",
        unit_price="10",
        stock="5",
    )

    assert product.description == ""
