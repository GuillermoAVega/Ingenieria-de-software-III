import pytest
from pydantic import ValidationError

from src.schemas.comanda import ComandaCreate


def datos_base(**cambios):
    datos = {
        "fecha": "2026-06-15",
        "hora": "20:00",
        "mesa_ids": [1],
    }
    datos.update(cambios)
    return datos


def test_comanda_sin_reserva_requiere_mozo():
    with pytest.raises(ValidationError, match="mozo es obligatorio"):
        ComandaCreate(**datos_base())


def test_comanda_con_reserva_no_acepta_mozo():
    with pytest.raises(ValidationError, match="no puede tener mozo"):
        ComandaCreate(**datos_base(reserva_id=7, mozo_id=3))


def test_comanda_con_reserva_puede_no_tener_mozo():
    comanda = ComandaCreate(**datos_base(reserva_id=7))

    assert comanda.mozo_id is None


def test_comanda_inmediata_puede_omitir_fecha_y_hora():
    datos = datos_base(mozo_id=3)
    datos.pop("fecha")
    datos.pop("hora")
    comanda = ComandaCreate(**datos)

    assert comanda.fecha is None
    assert comanda.hora is None
