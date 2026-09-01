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

    assert sale.status == SaleStatus.DRAFT
    assert sale.total == 701.0
    assert sale.customer_id == customer.id

    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    assert len(items) == 1
    assert items[0].quantity == 2
    assert items[0].unit_price == 350.5

    session.refresh(product)
    assert product.stock == 100


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
    assert product_a.stock == 100
    assert product_b.stock == 50


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
    assert product.stock == 100


def test_find_by_id_encuentra_una_venta_existente(session):
    customer = _create_customer(session)
    product = _create_product(session)
    sale = repository_venta.create_sale(session, customer, [(product, 2, 350.5)])

    found = repository_venta.find_by_id(session, sale.id)

    assert found is not None
    assert found.id == sale.id


def test_find_by_id_devuelve_none_si_no_existe(session):
    assert repository_venta.find_by_id(session, 999) is None


def test_cancel_sale_repone_stock_de_varios_items_y_cambia_estado(session):
    customer = _create_customer(session)
    product_a = _create_product(session, sku="ABC123", stock="100", unit_price="350.50")
    product_b = _create_product(session, sku="XYZ999", stock="50", unit_price="200")
    sale = repository_venta.create_sale(
        session, customer, [(product_a, 2, 350.5), (product_b, 3, 200.0)]
    )
    repository_venta.close_sale(session, sale.id)
    session.refresh(product_a)
    session.refresh(product_b)
    assert product_a.stock == 98
    assert product_b.stock == 47

    cancelled_sale, error = repository_venta.cancel_sale(session, sale.id)

    assert error is None
    assert cancelled_sale is not None
    assert cancelled_sale.status == SaleStatus.CANCELLED

    session.refresh(product_a)
    session.refresh(product_b)
    assert product_a.stock == 100
    assert product_b.stock == 50


def test_cancel_sale_devuelve_none_si_no_existe(session):
    cancelled_sale, error = repository_venta.cancel_sale(session, 999)

    assert cancelled_sale is None
    assert error == "NOT_FOUND"


def test_cancel_sale_no_duplica_reposicion_si_ya_estaba_anulada(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="100", unit_price="350.50")
    sale = repository_venta.create_sale(session, customer, [(product, 2, 350.5)])
    repository_venta.close_sale(session, sale.id)

    repository_venta.cancel_sale(session, sale.id)
    session.refresh(product)
    assert product.stock == 100

    cancelled_sale, error = repository_venta.cancel_sale(session, sale.id)

    assert error == "ALREADY_CANCELLED"
    assert cancelled_sale is not None
    assert cancelled_sale.status == SaleStatus.CANCELLED

    session.refresh(product)
    assert product.stock == 100


def test_cancel_sale_no_opera_sobre_venta_en_borrador(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="100", unit_price="350.50")
    sale = repository_venta.create_sale(session, customer, [(product, 2, 350.5)])

    result_sale, error = repository_venta.cancel_sale(session, sale.id)

    assert error == "DRAFT"
    assert result_sale is not None
    assert result_sale.status == SaleStatus.DRAFT

    session.refresh(product)
    assert product.stock == 100


def test_replace_sale_items_exitoso_agrega_quita_y_recalcula_total(session):
    customer = _create_customer(session)
    product_a = _create_product(session, sku="ABC123", stock="100", unit_price="350.50")
    product_b = _create_product(session, sku="XYZ999", stock="50", unit_price="200")
    sale = repository_venta.create_sale(session, customer, [(product_a, 2, 350.5)])

    updated_sale, error = repository_venta.replace_sale_items(
        session, sale.id, [(product_b, 3, 200.0)]
    )

    assert error is None
    assert updated_sale.total == 600.0
    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    assert len(items) == 1
    assert items[0].product_id == product_b.id
    assert items[0].quantity == 3
    session.refresh(product_a)
    session.refresh(product_b)
    assert product_a.stock == 100
    assert product_b.stock == 50


def test_replace_sale_items_devuelve_not_found_si_no_existe(session):
    result_sale, error = repository_venta.replace_sale_items(session, 999, [])

    assert result_sale is None
    assert error == "NOT_FOUND"


def test_replace_sale_items_no_modifica_venta_que_no_esta_en_borrador(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="100", unit_price="350.50")
    sale = repository_venta.create_sale(session, customer, [(product, 2, 350.5)])
    repository_venta.close_sale(session, sale.id)

    result_sale, error = repository_venta.replace_sale_items(session, sale.id, [])

    assert error == "NOT_DRAFT"
    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    assert len(items) == 1


def test_replace_sale_items_admite_lista_vacia(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="100", unit_price="350.50")
    sale = repository_venta.create_sale(session, customer, [(product, 2, 350.5)])

    updated_sale, error = repository_venta.replace_sale_items(session, sale.id, [])

    assert error is None
    assert updated_sale.total == 0
    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    assert len(items) == 0


def test_close_sale_exitoso_descuenta_stock_y_confirma(session):
    customer = _create_customer(session)
    product_a = _create_product(session, sku="ABC123", stock="100", unit_price="350.50")
    product_b = _create_product(session, sku="XYZ999", stock="50", unit_price="200")
    sale = repository_venta.create_sale(
        session, customer, [(product_a, 2, 350.5), (product_b, 3, 200.0)]
    )

    closed_sale, error = repository_venta.close_sale(session, sale.id)

    assert error is None
    assert closed_sale.status == SaleStatus.CONFIRMED
    session.refresh(product_a)
    session.refresh(product_b)
    assert product_a.stock == 98
    assert product_b.stock == 47


def test_close_sale_devuelve_not_found_si_no_existe(session):
    result_sale, error = repository_venta.close_sale(session, 999)

    assert result_sale is None
    assert error == "NOT_FOUND"


def test_close_sale_no_opera_dos_veces_sobre_la_misma_venta(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="100", unit_price="350.50")
    sale = repository_venta.create_sale(session, customer, [(product, 2, 350.5)])
    repository_venta.close_sale(session, sale.id)
    session.refresh(product)
    assert product.stock == 98

    result_sale, error = repository_venta.close_sale(session, sale.id)

    assert error == "NOT_DRAFT"
    session.refresh(product)
    assert product.stock == 98


def test_close_sale_con_detalle_vacio_no_cambia_estado(session):
    customer = _create_customer(session)
    sale = repository_venta.create_sale(session, customer, [])

    result_sale, error = repository_venta.close_sale(session, sale.id)

    assert error == "EMPTY_ITEMS"
    assert result_sale.status == SaleStatus.DRAFT


def test_close_sale_con_stock_insuficiente_no_descuenta_ningun_item(session):
    customer = _create_customer(session)
    product_a = _create_product(session, sku="ABC123", stock="100", unit_price="350.50")
    product_b = _create_product(session, sku="XYZ999", stock="50", unit_price="200")
    sale = repository_venta.create_sale(
        session, customer, [(product_a, 2, 350.5), (product_b, 3, 200.0)]
    )
    product_b.stock = 1
    session.commit()

    result_sale, error = repository_venta.close_sale(session, sale.id)

    assert error == "INSUFFICIENT_STOCK"
    assert result_sale.status == SaleStatus.DRAFT
    session.refresh(product_a)
    session.refresh(product_b)
    assert product_a.stock == 100
    assert product_b.stock == 1
