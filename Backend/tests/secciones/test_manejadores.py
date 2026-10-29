from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.main import app
from src.secciones.exceptions import NombreSeccionDuplicado, SeccionNoEncontrada
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


def test_main_registra_los_manejadores_de_secciones():
    for tipo in MANEJADORES_EXCEPCIONES:
        assert tipo in app.exception_handlers
