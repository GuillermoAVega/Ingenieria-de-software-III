import subprocess
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from src.main import app
from src.productos.bebidas.constants import PREFIJO as PREFIJO_BEBIDAS
from src.productos.combos.constants import PREFIJO as PREFIJO_COMBOS
from src.productos.combos.exceptions import ComboVencidoInmutable, FechaHastaVencida
from src.productos.exceptions import (
    BajaRestringida,
    ComponenteInactivo,
    ComponenteInvalido,
    ErrorConflicto,
    NombreDuplicado,
    ProductoNoEncontrado,
    SeccionInexistente,
)
from src.productos.menus_ejecutivos.constants import PREFIJO as PREFIJO_MENUS
from src.productos.models import Producto
from src.productos.platos.constants import PREFIJO as PREFIJO_PLATOS
from src.productos.postres.constants import PREFIJO as PREFIJO_POSTRES
from src.productos.router import MANEJADORES_EXCEPCIONES

RAIZ_BACKEND = Path(__file__).resolve().parents[2]


def _app_con_manejadores(excepcion: Exception) -> TestClient:
    """App mínima: registra los manejadores y expone una ruta que lanza `excepcion`."""
    aplicacion = FastAPI()
    for tipo, manejador in MANEJADORES_EXCEPCIONES.items():
        aplicacion.add_exception_handler(tipo, manejador)

    @aplicacion.get("/falla")
    def falla():
        raise excepcion

    return TestClient(aplicacion)


def test_cat_01_la_creacion_generica_responde_405_y_no_crea_nada(cliente, sesion):
    respuesta = cliente.post("/productos", json={"nombre": "Milanesa", "precio": "1500.00"})

    assert respuesta.status_code == 405
    assert sesion.scalar(select(func.count()).select_from(Producto)) == 0


def test_no_existe_ninguna_ruta_get_en_productos_sin_subtipo(cliente):
    # `GET /productos` y `GET /productos/{id}` quedan fuera de alcance
    rutas = app.openapi()["paths"]
    assert "get" in rutas["/productos/platos/{producto_id}"]  # la inspección ve las rutas
    assert "/productos" not in rutas
    assert "/productos/{producto_id}" not in rutas
    assert cliente.get("/productos").status_code in (404, 405)
    assert cliente.get("/productos/1").status_code == 404


def test_los_prefijos_de_los_subtipos():
    assert PREFIJO_PLATOS == "/platos"
    assert PREFIJO_BEBIDAS == "/bebidas"
    assert PREFIJO_POSTRES == "/postres"
    assert PREFIJO_MENUS == "/menus-ejecutivos"
    assert PREFIJO_COMBOS == "/combos"


def test_producto_no_encontrado_responde_404():
    respuesta = _app_con_manejadores(ProductoNoEncontrado()).get("/falla")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": ProductoNoEncontrado.MENSAJE}


def test_componente_invalido_responde_422_con_la_forma_de_pydantic():
    respuesta = _app_con_manejadores(ComponenteInvalido("plato_id", [4])).get("/falla")

    assert respuesta.status_code == 422
    assert respuesta.json() == {
        "detail": [
            {
                "loc": ["body", "plato_id"],
                "msg": ComponenteInvalido.MENSAJE,
                "type": "componente_invalido",
                "ids": [4],
            }
        ]
    }


def test_fecha_hasta_vencida_responde_422_sobre_fecha_hasta():
    respuesta = _app_con_manejadores(FechaHastaVencida()).get("/falla")

    assert respuesta.status_code == 422
    detalle = respuesta.json()["detail"]
    assert len(detalle) == 1
    assert detalle[0]["loc"] == ["body", "fecha_hasta"]
    assert detalle[0]["msg"] == FechaHastaVencida.MENSAJE
    assert detalle[0]["type"] == "fecha_hasta_vencida"


def test_seccion_inexistente_responde_422_con_la_forma_de_pydantic():
    respuesta = _app_con_manejadores(SeccionInexistente(999)).get("/falla")

    assert respuesta.status_code == 422
    assert respuesta.json() == {
        "detail": [
            {
                "loc": ["body", "seccion_id"],
                "msg": SeccionInexistente(999).mensaje,
                "type": "seccion_inexistente",
                "ids": [999],
            }
        ]
    }


def test_seccion_inexistente_no_es_capturada_por_el_manejador_de_conflicto():
    assert not issubclass(SeccionInexistente, ErrorConflicto)
    assert SeccionInexistente in MANEJADORES_EXCEPCIONES


def test_nombre_duplicado_responde_409_solo_con_detail():
    respuesta = _app_con_manejadores(NombreDuplicado()).get("/falla")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": NombreDuplicado.MENSAJE}


def test_combo_vencido_inmutable_responde_409_por_herencia_de_error_conflicto():
    respuesta = _app_con_manejadores(ComboVencidoInmutable()).get("/falla")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": ComboVencidoInmutable.MENSAJE}


def test_componente_inactivo_responde_409_con_ids():
    respuesta = _app_con_manejadores(ComponenteInactivo([3, 7])).get("/falla")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": ComponenteInactivo.MENSAJE, "ids": [3, 7]}


def test_baja_restringida_responde_409_con_bloqueantes_ordenados():
    respuesta = _app_con_manejadores(BajaRestringida([20, 10])).get("/falla")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": BajaRestringida.MENSAJE,
        "bloqueantes": [10, 20],
    }


def test_main_registra_los_manejadores_de_excepciones():
    for tipo in MANEJADORES_EXCEPCIONES:
        assert tipo in app.exception_handlers


def test_main_carga_el_registro_de_modelos_por_si_solo():
    # Proceso limpio: sin el conftest que ya importa `registro`
    codigo = (
        "import sys, src.main; "
        "sys.exit(0 if 'src.productos.registro' in sys.modules else 1)"
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=RAIZ_BACKEND,
        env={"PATH": "", "ENV": "test", "DB_URL": "sqlite://"},
        capture_output=True,
    )

    assert resultado.returncode == 0, resultado.stderr.decode()


@pytest.mark.parametrize(
    "prefijo", ["platos", "bebidas", "postres", "menus-ejecutivos", "combos"]
)
def test_las_rutas_por_id_de_los_subtipos_exigen_un_entero(cliente, prefijo):
    # Con `{producto_id:int}` un id no numérico no coincide con la ruta (404, no 422)
    assert cliente.get(f"/productos/{prefijo}/abc").status_code == 404
    assert cliente.delete(f"/productos/{prefijo}/abc").status_code == 404
    assert cliente.get(f"/productos/{prefijo}/999").status_code == 404
