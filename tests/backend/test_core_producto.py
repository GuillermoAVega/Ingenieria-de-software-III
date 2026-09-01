from app.backend import core_producto


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
