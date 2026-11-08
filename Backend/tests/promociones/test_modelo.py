from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.promociones.models import Promocion


def _promocion(plato, desde=date(2026, 6, 1), hasta=date(2026, 6, 30), descuento="10.00"):
    return Promocion(
        nombre="Promo",
        tipo="porcentaje",
        fecha_desde=desde,
        fecha_hasta=hasta,
        descuento=Decimal(descuento),
        productos=[plato],
    )


def test_pro_28_la_base_rechaza_un_rango_de_fechas_invertido(sesion, crear_plato):
    plato = crear_plato()
    sesion.add(_promocion(plato, desde=date(2026, 7, 1), hasta=date(2026, 6, 1)))
    with pytest.raises(IntegrityError):
        sesion.flush()


def test_pro_28_la_base_acepta_fechas_iguales(sesion, crear_plato):
    plato = crear_plato()
    sesion.add(_promocion(plato, desde=date(2026, 6, 1), hasta=date(2026, 6, 1)))
    sesion.flush()


@pytest.mark.parametrize("descuento", ["0.00", "-1.00", "100.01"])
def test_la_base_rechaza_un_descuento_fuera_de_rango(sesion, crear_plato, descuento):
    plato = crear_plato()
    sesion.add(_promocion(plato, descuento=descuento))
    with pytest.raises(IntegrityError):
        sesion.flush()


@pytest.mark.parametrize("descuento", ["0.01", "100.00"])
def test_la_base_acepta_los_limites_del_descuento(sesion, crear_plato, descuento):
    plato = crear_plato()
    sesion.add(_promocion(plato, descuento=descuento))
    sesion.flush()


def test_productos_ids_es_ascendente_y_dado_de_baja_es_falso_por_defecto(
    sesion, crear_plato, crear_bebida
):
    plato, bebida = crear_plato(), crear_bebida()
    promocion = _promocion(plato)
    promocion.productos.append(bebida)
    sesion.add(promocion)
    sesion.flush()
    assert promocion.dado_de_baja is False
    assert promocion.productos_ids == sorted([plato.id, bebida.id])
