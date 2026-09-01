from datetime import datetime

from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import (
    ClientStatus,
    Customer,
    Product,
    ProductStatus,
    Sale,
    SaleItem,
    SaleStatus,
)


def test_crear_tablas_sin_errores():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)


def test_crear_venta_y_sus_items_sin_errores():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()

    customer = Customer(
        dni=30111222,
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
        status=ClientStatus.ACTIVE,
    )
    session.add(customer)
    session.flush()

    product = Product(
        sku="ABC123",
        name="Coca-Cola 500ml",
        brand="Coca-Cola",
        description="",
        unit_price=350.5,
        stock=100,
        status=ProductStatus.ACTIVE,
    )
    session.add(product)
    session.flush()

    sale = Sale(
        customer_id=customer.id,
        sale_date=datetime(2026, 9, 1, 12, 0, 0),
        total=701.0,
        status=SaleStatus.CONFIRMED,
    )
    session.add(sale)
    session.flush()

    session.add(
        SaleItem(sale_id=sale.id, product_id=product.id, quantity=2, unit_price=350.5)
    )
    session.commit()

    stored_sale = session.query(Sale).filter_by(id=sale.id).one()
    stored_items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    assert stored_sale.status == SaleStatus.CONFIRMED
    assert len(stored_items) == 1
    assert stored_items[0].quantity == 2


def test_sku_no_es_unico_a_nivel_de_base():
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
            status=ProductStatus.INACTIVE,
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
            status=ProductStatus.ACTIVE,
        )
    )
    session.commit()

    stored = session.query(Product).filter_by(sku="ABC123").all()
    assert len(stored) == 2


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


def test_venta_puede_persistirse_anulada():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()

    customer = Customer(
        dni=30111222,
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
        status=ClientStatus.ACTIVE,
    )
    session.add(customer)
    session.flush()

    sale = Sale(
        customer_id=customer.id,
        sale_date=datetime(2026, 9, 1, 12, 0, 0),
        total=701.0,
        status=SaleStatus.CANCELLED,
    )
    session.add(sale)
    session.commit()

    stored = session.query(Sale).filter_by(id=sale.id).one()
    assert stored.status == SaleStatus.CANCELLED
