from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import Sale, SaleStatus
from app.backend.scripts.seed_clientes_ficticios import seed_clientes_ficticios
from app.backend.scripts.seed_productos_ficticios import seed_productos_ficticios
from app.backend.scripts.seed_ventas_ficticias import SALE_PLANS, seed_ventas_ficticias


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
