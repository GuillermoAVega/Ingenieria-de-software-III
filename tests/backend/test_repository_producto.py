import pytest

from app.backend import repository_producto
from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.models import Product, ProductStatus


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
        "unit_price": "350.50",
        "stock": "100",
    }
    defaults.update(overrides)
    return repository_producto.create_product(session, **defaults)


def test_create_product_asigna_estado_activo_por_defecto(session):
    product = _create_product(session)

    assert product.status == ProductStatus.ACTIVE


def test_sku_exists_detecta_duplicado_exacto(session):
    _create_product(session, sku="ABC123")

    assert repository_producto.sku_exists(session, "ABC123") is True


def test_sku_exists_detecta_duplicado_insensible_a_mayusculas(session):
    _create_product(session, sku="ABC123")

    assert repository_producto.sku_exists(session, "abc123") is True


def test_sku_exists_false_si_no_esta_registrado(session):
    assert repository_producto.sku_exists(session, "XYZ999") is False


def test_sku_exists_false_si_el_unico_dueno_esta_inactivo(session):
    product = _create_product(session, sku="ABC123")
    product.status = ProductStatus.INACTIVE
    session.commit()

    assert repository_producto.sku_exists(session, "ABC123") is False


def test_sku_exists_true_si_hay_un_activo_aunque_tambien_haya_un_inactivo(session):
    session.add(
        Product(
            sku="ABC123",
            name="Producto viejo",
            brand="Marca",
            description="",
            unit_price=10.0,
            stock=5,
            status=ProductStatus.INACTIVE,
        )
    )
    session.commit()
    _create_product(session, sku="ABC123", name="Producto nuevo")

    assert repository_producto.sku_exists(session, "ABC123") is True


def test_create_product_persiste_con_los_valores_ingresados(session):
    product = _create_product(session, sku="ABC123", description="Botella descartable")

    assert product.sku == "ABC123"
    assert product.unit_price == 350.5
    assert product.stock == 100
    stored = session.query(Product).filter_by(sku="ABC123").one()
    assert stored.description == "Botella descartable"


def test_find_by_sku_encuentra_por_valor_exacto(session):
    _create_product(session, sku="ABC123")

    found = repository_producto.find_by_sku(session, "ABC123")

    assert found is not None
    assert found.sku == "ABC123"


def test_find_by_sku_insensible_a_mayusculas(session):
    _create_product(session, sku="ABC123")

    found = repository_producto.find_by_sku(session, "abc123")

    assert found is not None
    assert found.sku == "ABC123"


def test_find_by_sku_devuelve_none_si_no_existe(session):
    assert repository_producto.find_by_sku(session, "XYZ999") is None


def test_find_by_sku_prioriza_el_producto_activo_ante_sku_compartido(session):
    session.add(
        Product(
            sku="ABC123",
            name="Producto viejo",
            brand="Marca",
            description="",
            unit_price=10.0,
            stock=5,
            status=ProductStatus.INACTIVE,
        )
    )
    session.commit()
    _create_product(session, sku="ABC123", name="Producto nuevo")

    found = repository_producto.find_by_sku(session, "ABC123")

    assert found is not None
    assert found.status == ProductStatus.ACTIVE
    assert found.name == "Producto nuevo"


def test_deactivate_by_sku_cambia_estado_activo_a_inactivo_sin_tocar_stock(session):
    _create_product(session, sku="ABC123", stock="500")

    deactivated = repository_producto.deactivate_by_sku(session, "ABC123")

    assert deactivated is not None
    assert deactivated.status == ProductStatus.INACTIVE
    assert deactivated.stock == 500
    stored = session.query(Product).filter_by(sku="ABC123").one()
    assert stored.status == ProductStatus.INACTIVE
    assert stored.stock == 500


def test_deactivate_by_sku_devuelve_none_si_no_existe(session):
    assert repository_producto.deactivate_by_sku(session, "ABC123") is None


def test_deactivate_by_sku_sobre_producto_ya_inactivo_no_lanza_error(session):
    _create_product(session, sku="ABC123")
    repository_producto.deactivate_by_sku(session, "ABC123")

    deactivated_again = repository_producto.deactivate_by_sku(session, "ABC123")

    assert deactivated_again is not None
    assert deactivated_again.status == ProductStatus.INACTIVE


def test_create_product_permite_descripcion_vacia(session):
    product = _create_product(
        session, sku="XYZ999", name="Producto sin descripción", description=""
    )

    assert product.description == ""
