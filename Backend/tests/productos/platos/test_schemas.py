import pytest
from pydantic import ValidationError

from src.productos.platos.schemas import PlatoActualizar, PlatoCrear, PlatoRespuesta


def datos_plato(**cambios):
    datos = {"nombre": "Milanesa", "precio": "1500.00", "cant_personas": 2}
    datos.update(cambios)
    return datos


def test_cant_personas_cero_se_rechaza():
    with pytest.raises(ValidationError):
        PlatoCrear(**datos_plato(cant_personas=0))


def test_cant_personas_ausente_se_rechaza():
    datos = datos_plato()
    del datos["cant_personas"]
    with pytest.raises(ValidationError):
        PlatoCrear(**datos)


def test_plato_valido_con_un_solo_comensal():
    assert PlatoCrear(**datos_plato(cant_personas=1)).cant_personas == 1


def test_actualizar_agrega_dado_de_baja_opcional():
    assert PlatoActualizar(**datos_plato()).dado_de_baja is None
    assert PlatoActualizar(**datos_plato(dado_de_baja=True)).dado_de_baja is True


def test_respuesta_se_construye_desde_el_modelo(crear_plato):
    plato = crear_plato()
    plato.id = 5
    plato.dado_de_baja = False
    respuesta = PlatoRespuesta.model_validate(plato)
    assert respuesta.id == 5
    assert respuesta.tipo == "plato"
    assert respuesta.cant_personas == 2
    assert respuesta.dado_de_baja is False
