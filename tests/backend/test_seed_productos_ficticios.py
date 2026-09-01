from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import Product
from app.backend.scripts.seed_productos_ficticios import (
    FICTITIOUS_PRODUCTS,
    seed_productos_ficticios,
)


def _session():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return create_session_factory(engine)()


def test_seed_inserta_todos_los_productos_ficticios():
    session = _session()

    inserted = seed_productos_ficticios(session)

    assert inserted == len(FICTITIOUS_PRODUCTS)
    assert session.query(Product).count() == len(FICTITIOUS_PRODUCTS)


def test_seed_es_idempotente_no_duplica_en_segunda_corrida():
    session = _session()

    seed_productos_ficticios(session)
    count_after_first_run = session.query(Product).count()

    inserted_second_run = seed_productos_ficticios(session)
    count_after_second_run = session.query(Product).count()

    assert inserted_second_run == 0
    assert count_after_second_run == count_after_first_run
