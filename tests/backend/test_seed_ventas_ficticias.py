from datetime import date, datetime

from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import Sale, SaleStatus
from app.backend.scripts.seed_clientes_ficticios import seed_clientes_ficticios
from app.backend.scripts.seed_productos_ficticios import seed_productos_ficticios
from app.backend.scripts.seed_ventas_ficticias import (
    CANCELLED_SALE_INDEXES,
    SALE_DAYS_AGO,
    SALE_PLANS,
    anular_ventas_ficticias,
    aplicar_fechas_ficticias,
    seed_ventas_ficticias,
)


def _session_con_clientes_y_productos():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()
    seed_clientes_ficticios(session)
    seed_productos_ficticios(session)
    return session


def test_seed_inserta_todas_las_ventas_ficticias():
    session = _session_con_clientes_y_productos()

    created = seed_ventas_ficticias(session)

    assert created == len(SALE_PLANS)
    assert session.query(Sale).count() == len(SALE_PLANS)
    assert all(sale.status == SaleStatus.CONFIRMED for sale in session.query(Sale).all())


def test_seed_permite_varias_ventas_para_el_mismo_cliente():
    session = _session_con_clientes_y_productos()

    seed_ventas_ficticias(session)

    customer_ids = [sale.customer_id for sale in session.query(Sale).all()]
    assert len(set(customer_ids)) < len(customer_ids)


def test_seed_es_idempotente_no_duplica_en_segunda_corrida():
    session = _session_con_clientes_y_productos()

    seed_ventas_ficticias(session)
    count_after_first_run = session.query(Sale).count()

    created_second_run = seed_ventas_ficticias(session)
    count_after_second_run = session.query(Sale).count()

    assert created_second_run == 0
    assert count_after_second_run == count_after_first_run


def test_seed_reparte_las_ventas_en_distintas_fechas():
    session = _session_con_clientes_y_productos()

    seed_ventas_ficticias(session)

    fechas = {sale.sale_date.date() for sale in session.query(Sale).all()}
    assert len(fechas) > 1
    # El plan tiene días repetidos a propósito (dos ventas el mismo día),
    # así que hay menos fechas distintas que ventas.
    assert len(fechas) == len(set(SALE_DAYS_AGO))


def test_aplicar_fechas_ficticias_reescribe_las_fechas_de_ventas_existentes():
    session = _session_con_clientes_y_productos()
    seed_ventas_ficticias(session)
    for sale in session.query(Sale).all():
        sale.sale_date = datetime(2020, 1, 1, 12, 0)
    session.commit()

    updated = aplicar_fechas_ficticias(session)

    assert updated == len(SALE_PLANS)
    assert session.query(Sale).count() == len(SALE_PLANS)
    fechas = {sale.sale_date.date() for sale in session.query(Sale).all()}
    assert date(2020, 1, 1) not in fechas
    assert len(fechas) == len(set(SALE_DAYS_AGO))


def test_anular_ventas_ficticias_deja_una_mezcla_de_estados():
    session = _session_con_clientes_y_productos()
    seed_ventas_ficticias(session)

    cancelled = anular_ventas_ficticias(session)

    assert cancelled == len(CANCELLED_SALE_INDEXES)
    estados = [sale.status for sale in session.query(Sale).order_by(Sale.id).all()]
    assert estados.count(SaleStatus.CANCELLED) == len(CANCELLED_SALE_INDEXES)
    assert SaleStatus.CONFIRMED in estados


def test_anular_ventas_ficticias_es_idempotente():
    session = _session_con_clientes_y_productos()
    seed_ventas_ficticias(session)
    anular_ventas_ficticias(session)

    cancelled_segunda_corrida = anular_ventas_ficticias(session)

    assert cancelled_segunda_corrida == 0
