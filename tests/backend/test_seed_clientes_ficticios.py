from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import Customer
from app.backend.scripts.seed_clientes_ficticios import (
    FICTITIOUS_CUSTOMERS,
    seed_clientes_ficticios,
)


def _session():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return create_session_factory(engine)()


def test_seed_inserta_todos_los_registros_ficticios():
    session = _session()

    inserted = seed_clientes_ficticios(session)

    assert inserted == len(FICTITIOUS_CUSTOMERS)
    assert session.query(Customer).count() == len(FICTITIOUS_CUSTOMERS)


def test_seed_es_idempotente_no_duplica_en_segunda_corrida():
    session = _session()

    seed_clientes_ficticios(session)
    count_after_first_run = session.query(Customer).count()

    inserted_second_run = seed_clientes_ficticios(session)
    count_after_second_run = session.query(Customer).count()

    assert inserted_second_run == 0
    assert count_after_second_run == count_after_first_run
