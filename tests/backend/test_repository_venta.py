import pytest

from app.backend import repository, repository_producto, repository_venta
from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import SaleItem, SaleStatus


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


def _create_customer(session, dni="30111222"):
    return repository.create_customer(
        session,
        dni=dni,
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )


def _create_product(session, sku="ABC123", stock="100", unit_price="350.50"):
    return repository_producto.create_product(
        session,
        sku=sku,
        name="Coca-Cola 500ml",
        brand="Coca-Cola",
        description="",
        unit_price=unit_price,
        stock=stock,
    )


def test_create_sale_con_un_item(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="100")

    sale = repository_venta.create_sale(
        session,
        customer,
        [(product, 2, 350.5)],
    )

    assert sale.status == SaleStatus.CONFIRMED
    assert sale.total == 701.0
    assert sale.customer_id == customer.id

    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    assert len(items) == 1
    assert items[0].quantity == 2
    assert items[0].unit_price == 350.5

    session.refresh(product)
    assert product.stock == 98


def test_create_sale_con_varios_items(session):
    customer = _create_customer(session)
    product_a = _create_product(session, sku="ABC123", stock="100", unit_price="350.50")
    product_b = _create_product(session, sku="XYZ999", stock="50", unit_price="200")

    sale = repository_venta.create_sale(
        session,
        customer,
        [(product_a, 2, 350.5), (product_b, 3, 200.0)],
    )

    assert sale.total == 2 * 350.5 + 3 * 200.0

    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    assert len(items) == 2

    session.refresh(product_a)
    session.refresh(product_b)
    assert product_a.stock == 98
    assert product_b.stock == 47


def test_create_sale_no_consolida_items_con_el_mismo_producto(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="100", unit_price="350.50")

    sale = repository_venta.create_sale(
        session,
        customer,
        [(product, 2, 350.5), (product, 3, 350.5)],
    )

    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    assert len(items) == 2
    assert sale.total == 2 * 350.5 + 3 * 350.5

    session.refresh(product)
    assert product.stock == 100 - 2 - 3
