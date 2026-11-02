import pytest
from sqlalchemy.exc import IntegrityError


def test_check_cant_personas_minima_rechazado_por_la_bd(sesion, crear_plato):
    sesion.add(crear_plato(cant_personas=0))
    with pytest.raises(IntegrityError):
        sesion.commit()
