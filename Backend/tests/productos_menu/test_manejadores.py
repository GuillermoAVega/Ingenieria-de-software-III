from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.productos.router import MANEJADORES_EXCEPCIONES as MANEJADORES_PRODUCTOS
from src.productos_menu.exceptions import (
    FechaMenuOcupada,
    MenuDelDiaDadoDeBaja,
    MenuDelDiaInexistente,
    ProductoMenuNoEncontrado,
    ProductoNoMenuDelDia,
)
from src.productos_menu.router import MANEJADORES_EXCEPCIONES


def _cliente_que_lanza(excepcion: Exception, con_productos: bool = False) -> TestClient:
    """App mínima: registra los manejadores y expone una ruta que lanza `excepcion`."""
    aplicacion = FastAPI()
    manejadores = dict(MANEJADORES_EXCEPCIONES)
    if con_productos:
        manejadores.update(MANEJADORES_PRODUCTOS)
    for tipo, manejador in manejadores.items():
        aplicacion.add_exception_handler(tipo, manejador)

    @aplicacion.get("/falla")
    def falla():
        raise excepcion

    return TestClient(aplicacion)


def test_pmd_13_menu_del_dia_inexistente_responde_422_con_forma_de_campo():
    respuesta = _cliente_que_lanza(MenuDelDiaInexistente(77)).get("/falla")

    assert respuesta.status_code == 422
    assert respuesta.json() == {
        "detail": [
            {
                "loc": ["body", "menu_del_dia_id"],
                "msg": MenuDelDiaInexistente.MENSAJE,
                "type": "menu_del_dia_inexistente",
                "ids": [77],
            }
        ]
    }


def test_pmd_08b_producto_no_menu_del_dia_responde_422_con_forma_de_campo():
    respuesta = _cliente_que_lanza(ProductoNoMenuDelDia(5)).get("/falla")

    assert respuesta.status_code == 422
    assert respuesta.json() == {
        "detail": [
            {
                "loc": ["body", "menu_del_dia_id"],
                "msg": "El producto indicado no es un menú del día",
                "type": "producto_no_menu_del_dia",
                "ids": [5],
            }
        ]
    }


def test_pmd_14_menu_del_dia_dado_de_baja_responde_409():
    respuesta = _cliente_que_lanza(MenuDelDiaDadoDeBaja()).get("/falla")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "El menú del día está dado de baja"}


def test_pmd_15_fecha_ocupada_responde_409():
    respuesta = _cliente_que_lanza(FechaMenuOcupada()).get("/falla")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "Ya existe un menú del día en esa fecha"}


def test_pmd_24_menu_no_encontrado_responde_404():
    respuesta = _cliente_que_lanza(ProductoMenuNoEncontrado()).get("/falla")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Menú del día no encontrado"}


def test_pmd_18_los_mensajes_de_baja_y_de_fecha_ocupada_difieren():
    baja = _cliente_que_lanza(MenuDelDiaDadoDeBaja()).get("/falla").json()
    ocupada = _cliente_que_lanza(FechaMenuOcupada()).get("/falla").json()

    assert baja["detail"] != ocupada["detail"]


def test_los_manejadores_de_productos_no_capturan_estas_excepciones():
    for excepcion in (
        MenuDelDiaInexistente(1),
        MenuDelDiaDadoDeBaja(),
        FechaMenuOcupada(),
        ProductoMenuNoEncontrado(),
    ):
        assert type(excepcion) in MANEJADORES_EXCEPCIONES
        assert not any(
            isinstance(excepcion, tipo) for tipo in MANEJADORES_PRODUCTOS
        )
