import pytest

from app.backend import repository
from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import ClientStatus, Customer


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


def test_insertar_cliente_persiste_con_estado_activo(session):
    customer = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    assert customer.status == ClientStatus.ACTIVE
    stored = session.query(Customer).filter_by(dni=30111222).one()
    assert stored.status == ClientStatus.ACTIVE


def test_duplicado_dni_exacto(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    assert repository.dni_exists(session, "30111222") is True


def test_duplicado_dni_normalizado_por_ceros_a_la_izquierda(session):
    repository.create_customer(
        session,
        dni="123456",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )

    assert repository.dni_exists(session, "0123456") is True


def test_duplicado_dni_con_cliente_existente_inactivo(session):
    customer = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    customer.status = ClientStatus.INACTIVE
    session.commit()

    assert repository.dni_exists(session, "30111222") is True


def test_dni_no_registrado_no_es_duplicado(session):
    assert repository.dni_exists(session, "30111222") is False


def test_active_customer_exists_with_dni_de_cliente_activo(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    assert repository.active_customer_exists_with_dni(session, "30111222") is True


def test_active_customer_exists_with_dni_de_cliente_inactivo_es_false(session):
    customer = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    customer.status = ClientStatus.INACTIVE
    session.commit()

    assert repository.active_customer_exists_with_dni(session, "30111222") is False


def test_active_customer_exists_with_dni_inexistente_es_false(session):
    assert repository.active_customer_exists_with_dni(session, "30111222") is False


def test_find_by_dni_encuentra_por_valor_exacto(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    found = repository.find_by_dni(session, "30111222")

    assert found is not None
    assert found.dni == 30111222


def test_find_by_dni_encuentra_por_ceros_a_la_izquierda(session):
    repository.create_customer(
        session,
        dni="123456",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )

    found = repository.find_by_dni(session, "0123456")

    assert found is not None
    assert found.dni == 123456


def test_find_by_dni_devuelve_none_ante_formato_invalido(session):
    assert repository.find_by_dni(session, "30.111.222") is None


def test_find_by_dni_devuelve_none_si_no_existe(session):
    assert repository.find_by_dni(session, "30111222") is None


def test_deactivate_by_dni_cambia_estado_activo_a_inactivo(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    deactivated = repository.deactivate_by_dni(session, "30111222")

    assert deactivated is not None
    assert deactivated.status == ClientStatus.INACTIVE
    stored = session.query(Customer).filter_by(dni=30111222).one()
    assert stored.status == ClientStatus.INACTIVE


def test_deactivate_by_dni_devuelve_none_si_no_existe(session):
    assert repository.deactivate_by_dni(session, "30111222") is None


def test_find_by_dni_prioriza_el_cliente_activo_ante_dni_compartido(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )
    repository.deactivate_by_dni(session, "30111222")
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    found = repository.find_by_dni(session, "30111222")

    assert found is not None
    assert found.status == ClientStatus.ACTIVE
    assert found.first_name == "Juan"


def test_dni_belongs_to_another_active_customer_true_si_otro_activo_lo_tiene(session):
    other = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    editing = repository.create_customer(
        session,
        dni="41234567",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )

    assert (
        repository.dni_belongs_to_another_active_customer(
            session, "30111222", editing.id
        )
        is True
    )
    assert other.id != editing.id


def test_dni_belongs_to_another_active_customer_false_si_es_el_propio_cliente(session):
    customer = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    assert (
        repository.dni_belongs_to_another_active_customer(
            session, "30111222", customer.id
        )
        is False
    )


def test_dni_belongs_to_another_active_customer_false_si_el_otro_esta_inactivo(session):
    other = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    repository.deactivate_by_dni(session, "30111222")
    editing = repository.create_customer(
        session,
        dni="41234567",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )

    assert (
        repository.dni_belongs_to_another_active_customer(
            session, "30111222", editing.id
        )
        is False
    )
    assert other.status == ClientStatus.INACTIVE


def test_dni_belongs_to_another_active_customer_false_si_nadie_lo_tiene(session):
    editing = repository.create_customer(
        session,
        dni="41234567",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )

    assert (
        repository.dni_belongs_to_another_active_customer(
            session, "30111222", editing.id
        )
        is False
    )


def test_update_customer_actualiza_campos_y_conserva_estado_activo(session):
    customer = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    updated = repository.update_customer(
        session,
        customer,
        dni="41234567",
        first_name="Juan Ignacio",
        last_name="Perez Gomez",
        email="juan.ignacio@dominio.com",
        phone="11-9999-8888",
    )

    assert updated.dni == 41234567
    assert updated.first_name == "Juan Ignacio"
    assert updated.status == ClientStatus.ACTIVE


def test_update_customer_conserva_estado_inactivo(session):
    customer = repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    repository.deactivate_by_dni(session, "30111222")
    session.refresh(customer)

    updated = repository.update_customer(
        session,
        customer,
        dni="30111222",
        first_name="Juan Ignacio",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    assert updated.status == ClientStatus.INACTIVE


def test_deactivate_by_dni_sobre_cliente_ya_inactivo_no_lanza_error(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    repository.deactivate_by_dni(session, "30111222")

    deactivated_again = repository.deactivate_by_dni(session, "30111222")

    assert deactivated_again is not None
    assert deactivated_again.status == ClientStatus.INACTIVE


def test_list_customers_sin_filtro_incluye_activos_e_inactivos(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    repository.create_customer(
        session,
        dni="41234567",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )
    repository.deactivate_by_dni(session, "41234567")

    customers, has_next = repository.list_customers(session, query=None, page=1)

    assert {c.dni for c in customers} == {30111222, 41234567}
    assert has_next is False


def test_list_customers_filtra_por_criterio_insensible_a_tildes(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Pérez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    repository.create_customer(
        session,
        dni="41234567",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )

    customers, _ = repository.list_customers(session, query="perez", page=1)

    assert [c.dni for c in customers] == [30111222]


def test_list_customers_filtra_por_dni_parcial(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    repository.create_customer(
        session,
        dni="41234567",
        first_name="Ana",
        last_name="Lopez",
        email="ana@dominio.com",
        phone="11-2222-3333",
    )

    customers, _ = repository.list_customers(session, query="301112", page=1)

    assert [c.dni for c in customers] == [30111222]


def test_list_customers_sin_coincidencias_devuelve_lista_vacia(session):
    repository.create_customer(
        session,
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )

    customers, has_next = repository.list_customers(session, query="gomez", page=1)

    assert customers == []
    assert has_next is False


def test_list_customers_pagina_de_a_veinte(session):
    for i in range(25):
        repository.create_customer(
            session,
            dni=str(30000000 + i),
            first_name="Cliente",
            last_name=f"Apellido{i:02d}",
            email=f"cliente{i}@dominio.com",
            phone="11-4444-5555",
        )

    page_1, has_next_1 = repository.list_customers(session, query=None, page=1)
    page_2, has_next_2 = repository.list_customers(session, query=None, page=2)

    assert len(page_1) == 20
    assert has_next_1 is True
    assert len(page_2) == 5
    assert has_next_2 is False
    assert {c.dni for c in page_1}.isdisjoint({c.dni for c in page_2})
