from decimal import Decimal

import pytest

from src.promociones.services import calcular_precio_final


@pytest.mark.parametrize(
    "precio, cantidad, descuento, esperado",
    [
        ("100.00", 3, "15.00", Decimal("255.00")),  # PRO-43
        ("10.00", 1, "33.33", Decimal("6.67")),  # PRO-44
        ("10.00", 1, "100.00", Decimal("0.00")),  # PRO-45
        ("10.00", 2, "0", Decimal("20.00")),  # sin promoción
        ("0.05", 1, "50.00", Decimal("0.03")),  # half-up (0.025 -> 0.03)
    ],
)
def test_calcular_precio_final(precio, cantidad, descuento, esperado):
    resultado = calcular_precio_final(Decimal(precio), cantidad, Decimal(descuento))
    assert resultado == esperado
    assert resultado.as_tuple().exponent == -2
