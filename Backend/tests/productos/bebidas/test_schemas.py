import pytest
from pydantic import ValidationError

from src.productos.bebidas.schemas import BebidaActualizar, BebidaCrear, BebidaRespuesta


def datos_bebida(**cambios):
    datos = {"nombre": "Cerveza", "precio": "800.00", "es_alcoholica": True}
    datos.update(cambios)
    return datos


def test_bebida_sin_es_alcoholica_se_rechaza():
    datos = datos_bebida()
    del datos["es_alcoholica"]
    with pytest.raises(ValidationError):
        BebidaCrear(**datos)


def test_bebida_valida():
    assert BebidaCrear(**datos_bebida(es_alcoholica=False)).es_alcoholica is False


def test_actualizar_agrega_dado_de_baja_opcional():
    assert BebidaActualizar(**datos_bebida()).dado_de_baja is None
    assert BebidaActualizar(**datos_bebida(dado_de_baja=False)).dado_de_baja is False


def test_respuesta_se_construye_desde_el_modelo(crear_bebida):
    bebida = crear_bebida()
    bebida.id = 3
    bebida.dado_de_baja = False
    respuesta = BebidaRespuesta.model_validate(bebida)
    assert respuesta.tipo == "bebida"
    assert respuesta.es_alcoholica is True
