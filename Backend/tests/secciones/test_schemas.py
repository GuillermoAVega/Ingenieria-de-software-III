from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src.secciones.schemas import SeccionActualizar, SeccionCrear, SeccionRespuesta


def crear(**cambios):
    datos = {"nombre": "Entradas"}
    datos.update(cambios)
    return SeccionCrear(**datos)


# --- nombre ---


def test_sec_03_nombre_vacio_se_rechaza():
    with pytest.raises(ValidationError):
        crear(nombre="")


def test_sec_04_nombre_solo_espacios_se_rechaza():
    with pytest.raises(ValidationError):
        crear(nombre="   ")


def test_sec_05_nombre_ausente_se_rechaza():
    with pytest.raises(ValidationError):
        SeccionCrear()


def test_sec_06_nombre_se_recorta():
    assert crear(nombre="  Entradas ").nombre == "Entradas"


def test_sec_07_nombre_de_100_caracteres_es_valido():
    assert len(crear(nombre="a" * 100).nombre) == 100


def test_sec_08_nombre_de_101_caracteres_se_rechaza():
    with pytest.raises(ValidationError):
        crear(nombre="a" * 101)


# --- subtitulo ---


def test_sec_09_subtitulo_de_200_caracteres_es_valido():
    assert len(crear(subtitulo="a" * 200).subtitulo) == 200


def test_sec_10_subtitulo_de_201_caracteres_se_rechaza():
    with pytest.raises(ValidationError):
        crear(subtitulo="a" * 201)


def test_sec_39_subtitulo_se_recorta():
    assert crear(subtitulo="  Para comenzar ").subtitulo == "Para comenzar"


def test_sec_40_subtitulo_vacio_queda_en_none():
    assert crear(subtitulo="").subtitulo is None


def test_sec_41_subtitulo_solo_espacios_queda_en_none():
    assert crear(subtitulo="   ").subtitulo is None


def test_sec_42_limite_de_subtitulo_se_verifica_tras_el_recorte():
    assert len(crear(subtitulo=" " + "a" * 200 + " ").subtitulo) == 200


def test_sec_43_subtitulo_de_201_rodeado_de_espacios_se_rechaza():
    with pytest.raises(ValidationError):
        crear(subtitulo=" " + "a" * 201 + " ")


def test_subtitulo_omitido_queda_en_none():
    assert crear().subtitulo is None


# --- actualizar y respuesta ---


def test_actualizar_equivale_a_crear():
    assert SeccionActualizar is SeccionCrear


def test_sec_02_respuesta_solo_expone_id_nombre_y_subtitulo():
    assert set(SeccionRespuesta.model_fields) == {"id", "nombre", "subtitulo"}


def test_respuesta_se_construye_desde_atributos():
    origen = SimpleNamespace(id=3, nombre="Entradas", subtitulo=None, productos=[])
    respuesta = SeccionRespuesta.model_validate(origen)
    assert respuesta.model_dump() == {"id": 3, "nombre": "Entradas", "subtitulo": None}
