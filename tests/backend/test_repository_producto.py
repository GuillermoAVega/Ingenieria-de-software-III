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


def test_update_product_actualiza_campos_y_no_toca_sku_ni_estado_activo(session):
    product = _create_product(session)

    updated = repository_producto.update_product(
        session,
        product,
        name="Coca-Cola 1L",
        brand="Coca-Cola",
        description="Botella retornable",
        unit_price="399.90",
        stock="80",
    )

    assert updated.name == "Coca-Cola 1L"
    assert updated.unit_price == 399.9
    assert updated.stock == 80
    assert updated.sku == "ABC123"
    assert updated.status == ProductStatus.ACTIVE


def test_update_product_no_toca_estado_inactivo(session):
    product = _create_product(session)
    repository_producto.deactivate_by_sku(session, "ABC123")
    session.refresh(product)

    updated = repository_producto.update_product(
        session,
        product,
        name="Coca-Cola 1L",
        brand="Coca-Cola",
        description="",
        unit_price="399.90",
        stock="80",
    )

    assert updated.status == ProductStatus.INACTIVE


def test_list_products_sin_filtro_incluye_activos_e_inactivos(session):
    _create_product(session, sku="ABC123")
    _create_product(session, sku="XYZ999", name="Otro producto")
    repository_producto.deactivate_by_sku(session, "XYZ999")

    products, has_next = repository_producto.list_products(session, query=None, page=1)

    assert {p.sku for p in products} == {"ABC123", "XYZ999"}
    assert has_next is False


def test_list_products_filtra_por_criterio_insensible_a_tildes(session):
    _create_product(session, sku="ABC123", name="Limón Cola")
    _create_product(session, sku="XYZ999", name="Naranja")

    products, _ = repository_producto.list_products(session, query="limon", page=1)

    assert [p.sku for p in products] == ["ABC123"]


def test_list_products_filtra_por_sku_parcial(session):
    _create_product(session, sku="ABC123")
    _create_product(session, sku="XYZ999", name="Otro producto")

    products, _ = repository_producto.list_products(session, query="abc", page=1)

    assert [p.sku for p in products] == ["ABC123"]


def test_list_products_sin_coincidencias_devuelve_lista_vacia(session):
    _create_product(session, sku="ABC123")

    products, has_next = repository_producto.list_products(session, query="gaseosa", page=1)

    assert products == []
    assert has_next is False


def test_list_products_pagina_de_a_veinte(session):
    for i in range(25):
        _create_product(
            session,
            sku=f"SKU{i:03d}",
            name=f"Producto {i:03d}",
        )

    page_1, has_next_1 = repository_producto.list_products(session, query=None, page=1)
    page_2, has_next_2 = repository_producto.list_products(session, query=None, page=2)

    assert len(page_1) == 20
    assert has_next_1 is True
    assert len(page_2) == 5
    assert has_next_2 is False
    assert {p.sku for p in page_1}.isdisjoint({p.sku for p in page_2})


def test_search_for_venta_coincidencias_por_nombre_y_descripcion(session):
    _create_product(session, sku="ABC123", name="Coca-Cola 500ml", description="Botella descartable")
    _create_product(session, sku="XYZ999", name="Sprite 500ml", description="Lima limón")
    _create_product(session, sku="DEF456", name="Agua mineral", description="Sin gas")

    por_nombre = repository_producto.search_for_venta(session, "coca")
    por_descripcion = repository_producto.search_for_venta(session, "descartable")

    assert [p.sku for p in por_nombre] == ["ABC123"]
    assert [p.sku for p in por_descripcion] == ["ABC123"]


def test_search_for_venta_excluye_inactivos(session):
    _create_product(session, sku="ABC123", name="Coca-Cola 500ml")
    inactivo = _create_product(session, sku="XYZ999", name="Coca-Cola 1L")
    repository_producto.deactivate_by_sku(session, "XYZ999")

    results = repository_producto.search_for_venta(session, "coca")

    assert [p.sku for p in results] == ["ABC123"]
    assert inactivo.sku not in [p.sku for p in results]


def test_search_for_venta_limita_resultados(session):
    for i in range(25):
        _create_product(session, sku=f"SKU{i:03d}", name=f"Producto {i:03d}")

    results = repository_producto.search_for_venta(session, "producto")

    assert len(results) == 20


def test_search_for_venta_sin_query_devuelve_lista_vacia(session):
    _create_product(session)

    assert repository_producto.search_for_venta(session, "") == []
    assert repository_producto.search_for_venta(session, None) == []
