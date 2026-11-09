import itertools
from datetime import datetime, time

import pytest

from src.mesa.models import Mesa
from src.models import Comanda, Factura
from src.sector.models import Sector

URL = "/reportes/ventas-comparativa"
_sectores = itertools.count()


@pytest.fixture
def crear_factura(persistir):
    """Crea una factura emitida con su comanda, mesa y sector mínimos."""

    def _crear(fecha_hora: datetime, importe: float, activo: bool = True) -> int:
        numero = next(_sectores)
        sector = Sector(
            nombre=f"Sector {numero}",
            apto_fumadores=False,
            piso="Planta baja",
        )
        mesa = Mesa(capacidad=2, disponible=True, sector=sector)
        comanda = Comanda(
            fecha=fecha_hora.date(),
            hora=time(12),
            estado="cerrada",
            mesa=mesa,
        )
        factura = Factura(
            fecha_hora_emision=fecha_hora,
            importe_total=importe,
            activo=activo,
            comanda=comanda,
        )
        _, _, _, factura_id = persistir(sector, mesa, comanda, factura)
        return factura_id

    return _crear


def test_mes_actual_por_defecto(cliente):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert (cuerpo["anio"], cuerpo["mes"]) == (2026, 6)
    assert (cuerpo["anio_anterior"], cuerpo["mes_anterior"]) == (2026, 5)
    assert len(cuerpo["actual"]) == 30
    assert len(cuerpo["anterior"]) == 31
    assert all(punto["importe"] == 0 for punto in cuerpo["actual"])
    assert all(punto["importe"] == 0 for punto in cuerpo["anterior"])


def test_suma_facturas_activas_por_dia(cliente, crear_factura):
    crear_factura(datetime(2026, 6, 2, 12), 100)
    crear_factura(datetime(2026, 6, 2, 21), 75.5)
    crear_factura(datetime(2026, 6, 15, 13), 200)
    crear_factura(datetime(2026, 6, 3, 12), 999, activo=False)
    crear_factura(datetime(2026, 5, 31, 23), 40)
    crear_factura(datetime(2026, 7, 1, 0), 500)

    respuesta = cliente.get(URL, params={"anio": 2026, "mes": 6})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    actual = {punto["dia"]: punto["importe"] for punto in cuerpo["actual"]}
    anterior = {punto["dia"]: punto["importe"] for punto in cuerpo["anterior"]}
    assert actual[2] == 175.5
    assert actual[15] == 200
    assert actual[3] == 0
    assert anterior[31] == 40
    assert sum(actual.values()) == 375.5
    assert sum(anterior.values()) == 40


def test_enero_compara_con_diciembre_del_anio_anterior(cliente, crear_factura):
    crear_factura(datetime(2026, 1, 5, 12), 120)
    crear_factura(datetime(2025, 12, 20, 12), 80)
    crear_factura(datetime(2025, 11, 30, 12), 999)

    respuesta = cliente.get(URL, params={"anio": 2026, "mes": 1})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert (cuerpo["anio_anterior"], cuerpo["mes_anterior"]) == (2025, 12)
    assert len(cuerpo["actual"]) == 31
    assert len(cuerpo["anterior"]) == 31
    assert cuerpo["actual"][4]["importe"] == 120
    assert cuerpo["anterior"][19]["importe"] == 80


def test_mes_invalido_devuelve_422(cliente):
    respuesta = cliente.get(URL, params={"anio": 2026, "mes": 13})

    assert respuesta.status_code == 422


def test_anio_invalido_devuelve_422(cliente):
    respuesta = cliente.get(URL, params={"anio": 1999, "mes": 6})

    assert respuesta.status_code == 422
