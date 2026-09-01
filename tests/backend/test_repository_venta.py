from datetime import date, datetime, timezone

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


def _create_confirmed_sale(session, customer, product, quantity=1, sale_date=None):
    sale = repository_venta.create_sale(session, customer, [(product, quantity, product.unit_price)])
    if sale_date is not None:
        sale.sale_date = sale_date
        session.commit()
    repository_venta.close_sale(session, sale.id)
    session.refresh(sale)
    return sale


def test_list_sales_excluye_borrador_y_anulada_y_ordena_por_fecha_desc(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="1000")

    older = _create_confirmed_sale(
        session, customer, product, sale_date=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    newer = _create_confirmed_sale(
        session, customer, product, sale_date=datetime(2026, 2, 1, tzinfo=timezone.utc)
    )
    draft = repository_venta.create_sale(session, customer, [(product, 1, product.unit_price)])
    cancelled = _create_confirmed_sale(
        session, customer, product, sale_date=datetime(2026, 3, 1, tzinfo=timezone.utc)
    )
    repository_venta.cancel_sale(session, cancelled.id)

    rows, has_next = repository_venta.list_sales(session)

    assert [sale.id for sale, _ in rows] == [newer.id, older.id]
    assert has_next is False
    assert draft.id not in [sale.id for sale, _ in rows]
    assert cancelled.id not in [sale.id for sale, _ in rows]


def test_list_sales_filtra_por_rango_de_fechas_con_extremos_inclusivos(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="1000")

    in_lower_bound = _create_confirmed_sale(
        session, customer, product, sale_date=datetime(2026, 1, 10, tzinfo=timezone.utc)
    )
    in_upper_bound = _create_confirmed_sale(
        session, customer, product, sale_date=datetime(2026, 1, 20, tzinfo=timezone.utc)
    )
    outside = _create_confirmed_sale(
        session, customer, product, sale_date=datetime(2026, 2, 1, tzinfo=timezone.utc)
    )

    rows, _ = repository_venta.list_sales(
        session, date_from=date(2026, 1, 10), date_to=date(2026, 1, 20)
    )

    ids = {sale.id for sale, _ in rows}
    assert ids == {in_lower_bound.id, in_upper_bound.id}
    assert outside.id not in ids


def test_list_sales_con_un_solo_extremo_de_fecha(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="1000")

    early = _create_confirmed_sale(
        session, customer, product, sale_date=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    late = _create_confirmed_sale(
        session, customer, product, sale_date=datetime(2026, 3, 1, tzinfo=timezone.utc)
    )

    only_from, _ = repository_venta.list_sales(session, date_from=date(2026, 2, 1))
    only_to, _ = repository_venta.list_sales(session, date_to=date(2026, 2, 1))

    assert {sale.id for sale, _ in only_from} == {late.id}
    assert {sale.id for sale, _ in only_to} == {early.id}


def test_list_sales_filtra_por_dni_parcial(session):
    customer_a = _create_customer(session, dni="30111222")
    customer_b = _create_customer(session, dni="40222333")
    product = _create_product(session, stock="1000")
    sale_a = _create_confirmed_sale(session, customer_a, product)
    _create_confirmed_sale(session, customer_b, product)

    rows, _ = repository_venta.list_sales(session, dni="3011")

    assert [sale.id for sale, _ in rows] == [sale_a.id]


def test_list_sales_combina_fecha_y_dni_con_and(session):
    customer_a = _create_customer(session, dni="30111222")
    customer_b = _create_customer(session, dni="40222333")
    product = _create_product(session, stock="1000")
    matches_both = _create_confirmed_sale(
        session, customer_a, product, sale_date=datetime(2026, 1, 15, tzinfo=timezone.utc)
    )
    matches_only_dni = _create_confirmed_sale(
        session, customer_a, product, sale_date=datetime(2026, 5, 1, tzinfo=timezone.utc)
    )
    matches_only_date = _create_confirmed_sale(
        session, customer_b, product, sale_date=datetime(2026, 1, 15, tzinfo=timezone.utc)
    )

    rows, _ = repository_venta.list_sales(
        session, dni="3011", date_from=date(2026, 1, 1), date_to=date(2026, 1, 31)
    )

    assert [sale.id for sale, _ in rows] == [matches_both.id]
    assert matches_only_dni.id not in [sale.id for sale, _ in rows]
    assert matches_only_date.id not in [sale.id for sale, _ in rows]


def test_list_sales_sin_coincidencias_devuelve_lista_vacia(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="1000")
    _create_confirmed_sale(session, customer, product)

    rows, has_next = repository_venta.list_sales(session, dni="99999999")

    assert rows == []
    assert has_next is False


def test_list_sales_pagina_de_a_veinte(session):
    customer = _create_customer(session)
    product = _create_product(session, stock="1000")
    for i in range(25):
        _create_confirmed_sale(
            session, customer, product, sale_date=datetime(2026, 1, i + 1, tzinfo=timezone.utc)
        )

    page_1, has_next_1 = repository_venta.list_sales(session, page=1)
    page_2, has_next_2 = repository_venta.list_sales(session, page=2)

    assert len(page_1) == 20
    assert has_next_1 is True
    assert len(page_2) == 5
    assert has_next_2 is False
    ids_1 = {sale.id for sale, _ in page_1}
    ids_2 = {sale.id for sale, _ in page_2}
    assert ids_1.isdisjoint(ids_2)
