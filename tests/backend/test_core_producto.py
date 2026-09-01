from app.backend import core, core_producto


def test_validate_positive_number_valido_con_decimales():
    assert core_producto.validate_positive_number("350.50") is True


def test_validate_positive_number_invalido_cero():
    assert core_producto.validate_positive_number("0") is False


def test_validate_positive_number_invalido_negativo():
    assert core_producto.validate_positive_number("-5") is False


def test_validate_positive_number_invalido_no_numerico():
    assert core_producto.validate_positive_number("abc") is False


def test_validate_positive_integer_valido():
    assert core_producto.validate_positive_integer("100") is True


def test_validate_positive_integer_invalido_cero():
    assert core_producto.validate_positive_integer("0") is False


def test_validate_positive_integer_invalido_negativo():
    assert core_producto.validate_positive_integer("-1") is False


def test_validate_positive_integer_invalido_decimal():
    assert core_producto.validate_positive_integer("5.5") is False


def test_validate_positive_integer_invalido_no_numerico():
    assert core_producto.validate_positive_integer("abc") is False


def test_initial_status_es_activo():
    assert core_producto.initial_status() == "Activo"


def test_matches_search_por_nombre():
    query = core.normalize_search_text("coca")
    assert core_producto.matches_search(query, sku="ABC123", name="Coca-Cola 500ml") is True


def test_matches_search_por_sku_parcial():
    query = core.normalize_search_text("abc")
    assert core_producto.matches_search(query, sku="ABC123", name="Coca-Cola 500ml") is True


def test_matches_search_insensible_a_tildes():
    query = core.normalize_search_text("cola")
    assert core_producto.matches_search(query, sku="XYZ999", name="Limón Cola") is True


def test_matches_search_sin_coincidencia():
    query = core.normalize_search_text("gaseosa")
    assert core_producto.matches_search(query, sku="ABC123", name="Coca-Cola 500ml") is False
