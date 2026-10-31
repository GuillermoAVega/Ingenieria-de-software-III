from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.main import app
from src.secciones.exceptions import (
    NombreSeccionDuplicado,
    PosicionSeccionDuplicada,
    SeccionNoEncontrada,
)
from src.secciones.router import MANEJADORES_EXCEPCIONES


def _app_con_manejadores(excepcion: Exception) -> TestClient:
    """App mínima: registra los manejadores y expone una ruta que lanza `excepcion`."""
    aplicacion = FastAPI()
    for tipo, manejador in MANEJADORES_EXCEPCIONES.items():
        aplicacion.add_exception_handler(tipo, manejador)

    @aplicacion.get("/falla")
    def falla():
        raise excepcion

    return TestClient(aplicacion)


def test_seccion_no_encontrada_responde_404_solo_con_detail():
    respuesta = _app_con_manejadores(SeccionNoEncontrada()).get("/falla")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": SeccionNoEncontrada.MENSAJE}


def test_nombre_seccion_duplicado_responde_409_solo_con_detail():
    respuesta = _app_con_manejadores(NombreSeccionDuplicado()).get("/falla")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": NombreSeccionDuplicado.MENSAJE}


def test_pos_12_posicion_seccion_duplicada_responde_409_solo_con_detail():
    respuesta = _app_con_manejadores(PosicionSeccionDuplicada()).get("/falla")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "Ya existe una sección en esa posición"}


def test_posicion_duplicada_y_nombre_duplicado_comparten_la_forma_del_cuerpo():
    por_posicion = _app_con_manejadores(PosicionSeccionDuplicada()).get("/falla")
    por_nombre = _app_con_manejadores(NombreSeccionDuplicado()).get("/falla")

    assert por_posicion.status_code == por_nombre.status_code == 409
    assert set(por_posicion.json()) == set(por_nombre.json()) == {"detail"}


def test_posicion_duplicada_figura_en_los_manejadores():
    assert PosicionSeccionDuplicada in MANEJADORES_EXCEPCIONES


def test_main_registra_los_manejadores_de_secciones():
    for tipo in MANEJADORES_EXCEPCIONES:
        assert tipo in app.exception_handlers
