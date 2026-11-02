from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src.secciones.schemas import SeccionActualizar, SeccionCrear, SeccionRespuesta


def crear(**cambios):
    datos = {"nombre": "Entradas", "posicion": 1}
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


# --- posicion ---


def sin_posicion():
    return {"nombre": "Entradas"}


def test_pos_02_posicion_ausente_se_rechaza_en_el_alta():
    with pytest.raises(ValidationError):
        SeccionCrear(**sin_posicion())


def test_pos_03_posicion_ausente_se_rechaza_en_la_modificacion():
    with pytest.raises(ValidationError):
        SeccionActualizar(**sin_posicion())


def test_pos_04_posicion_cero_se_rechaza():
    with pytest.raises(ValidationError):
        crear(posicion=0)


def test_pos_05_posicion_negativa_se_rechaza():
    with pytest.raises(ValidationError):
        crear(posicion=-1)


def test_pos_06_posicion_cero_se_rechaza_en_la_modificacion():
    with pytest.raises(ValidationError):
        SeccionActualizar(nombre="Entradas", posicion=0)


def test_pos_07_posicion_no_numerica_se_rechaza():
    with pytest.raises(ValidationError):
        crear(posicion="abc")


@pytest.mark.parametrize("posicion", [3.5, 1.5])
def test_pos_08_posicion_decimal_con_parte_fraccionaria_se_rechaza(posicion):
    with pytest.raises(ValidationError):
        crear(posicion=posicion)


def test_pos_09_posicion_en_el_limite_inferior_es_valida():
    assert crear(posicion=1).posicion == 1


@pytest.mark.parametrize("posicion", ["3", 3.0])
def test_pos_29_posicion_como_texto_o_decimal_entero_se_convierte_a_int(posicion):
    convertida = crear(posicion=posicion).posicion

    assert convertida == 3
    assert type(convertida) is int


def test_posicion_actualizar_valida_igual_que_crear():
    assert SeccionActualizar(nombre="Entradas", posicion=2).posicion == 2


# --- actualizar y respuesta ---


def test_actualizar_equivale_a_crear():
    assert SeccionActualizar is SeccionCrear


def test_sec_02_respuesta_solo_expone_id_nombre_subtitulo_posicion_y_productos_ids():
    assert list(SeccionRespuesta.model_fields) == [
        "id",
        "nombre",
        "subtitulo",
        "posicion",
        "productos_ids",
    ]


def test_productos_ids_esquema_expone_el_campo():
    origen = SimpleNamespace(
        id=3, nombre="Entradas", subtitulo=None, posicion=2, productos_ids=[10, 12]
    )
    respuesta = SeccionRespuesta.model_validate(origen)
    assert respuesta.productos_ids == [10, 12]


def test_respuesta_se_construye_desde_atributos():
    origen = SimpleNamespace(id=3, nombre="Entradas", subtitulo=None, posicion=2, productos_ids=[])
    respuesta = SeccionRespuesta.model_validate(origen)
    assert respuesta.model_dump() == {
        "id": 3,
        "nombre": "Entradas",
        "subtitulo": None,
        "posicion": 2,
        "productos_ids": [],
    }
