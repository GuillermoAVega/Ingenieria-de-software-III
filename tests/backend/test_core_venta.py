from datetime import date

from app.backend import core_venta


def test_is_valid_date_range_sin_extremos():
    assert core_venta.is_valid_date_range(None, None) is True


def test_is_valid_date_range_solo_desde():
    assert core_venta.is_valid_date_range(date(2026, 1, 1), None) is True


def test_is_valid_date_range_solo_hasta():
    assert core_venta.is_valid_date_range(None, date(2026, 1, 31)) is True


def test_is_valid_date_range_desde_anterior_a_hasta():
    assert core_venta.is_valid_date_range(date(2026, 1, 1), date(2026, 1, 31)) is True


def test_is_valid_date_range_desde_igual_a_hasta():
    assert core_venta.is_valid_date_range(date(2026, 1, 1), date(2026, 1, 1)) is True


def test_is_valid_date_range_desde_posterior_a_hasta_es_invalido():
    assert core_venta.is_valid_date_range(date(2026, 2, 1), date(2026, 1, 1)) is False


def test_matches_dni_coincidencia_parcial():
    assert core_venta.matches_dni(30111222, "3011") is True


def test_matches_dni_sin_coincidencia():
    assert core_venta.matches_dni(30111222, "9999") is False


def test_matches_dni_criterio_vacio_coincide_siempre():
    assert core_venta.matches_dni(30111222, "") is True
    assert core_venta.matches_dni(30111222, None) is True


def test_matches_dni_recorta_espacios():
    assert core_venta.matches_dni(30111222, "  3011  ") is True
