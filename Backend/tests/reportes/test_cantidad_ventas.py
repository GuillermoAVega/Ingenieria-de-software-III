import itertools
from datetime import date, datetime, time

import pytest

from src.mesa.models import Mesa
from src.models import Comanda, ComprobantePago, Factura, MedioPago
from src.mozo.models import Mozo
from src.sector.models import Sector
from src.reportes.services import agrupar_ventas

URL = "/reportes/ventas/cantidad"


# --- Unidad: agrupar_ventas ---


def test_agrupar_sin_ventas_devuelve_ceros():
    r = agrupar_ventas(2025, [])
    assert [m.mes for m in r.por_mes] == list(range(1, 13))
    assert [d.dia for d in r.por_dia_semana] == list(range(7))
    assert all(m.cantidad == 0 for m in r.por_mes)
    assert all(d.cantidad == 0 for d in r.por_dia_semana)


def test_agrupar_meses_con_huecos():
    r = agrupar_ventas(2025, [datetime(2025, 3, 5), datetime(2025, 8, 9)])
    cantidades = {m.mes: m.cantidad for m in r.por_mes}
    assert cantidades[3] == 1 and cantidades[8] == 1
    assert sum(cantidades.values()) == 2


def test_agrupar_lunes_y_domingo():
    # 2025-06-02 es lunes, 2025-06-08 es domingo
    r = agrupar_ventas(2025, [datetime(2025, 6, 2), datetime(2025, 6, 8)])
    por_dia = [d.cantidad for d in r.por_dia_semana]
    assert por_dia == [1, 0, 0, 0, 0, 0, 1]


def test_agrupar_totales_consistentes():
    fechas = [datetime(2025, m, d) for m, d in [(1, 1), (2, 14), (5, 30), (12, 31)]]
    r = agrupar_ventas(2025, fechas)
    assert sum(m.cantidad for m in r.por_mes) == sum(d.cantidad for d in r.por_dia_semana) == 4


# --- Integración ---


contador = itertools.count(1)


@pytest.fixture
def crear_venta(sesion, persistir):
    def _crear(emision, activa=True, comprobantes=(True,)):
        n = next(contador)
        sector = Sector(nombre=f"Salón {n}", apto_fumadores=False, piso="Planta baja")
        mesa = Mesa(capacidad=2, disponible=True, sector=sector)
        mozo = Mozo(nombre="Luis", nro_legajo=n)
        medio = MedioPago(descripcion=f"Medio {n}")
        mesa_id, mozo_id, medio_id = persistir(mesa, mozo, medio)
        comanda = Comanda(fecha=date(2025, 1, 1), hora=time(12), mozo_id=mozo_id, mesa_id=mesa_id)
        comanda_id = persistir(comanda)
        factura = Factura(
            importe_total=0,
            fecha_hora_emision=emision,
            activo=activa,
            comanda_id=comanda_id,
        )
        sesion.add(factura)
        sesion.flush()
        for activo in comprobantes:
            sesion.add(
                ComprobantePago(
                    importe=0,
                    fecha_hora_emision=emision,
                    activo=activo,
                    factura_id=factura.id,
                    medio_pago_id=medio_id,
                )
            )
        sesion.commit()
        sesion.close()

    return _crear


def _total(cuerpo):
    return sum(m["cantidad"] for m in cuerpo["por_mes"])


def test_estructura_200(cliente):
    r = cliente.get(URL, params={"anio": 2025})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["anio"] == 2025
    assert [m["mes"] for m in cuerpo["por_mes"]] == list(range(1, 13))
    assert [d["dia"] for d in cuerpo["por_dia_semana"]] == list(range(7))


@pytest.mark.parametrize("params", [{}, {"anio": "abc"}, {"anio": 999}, {"anio": 10000}])
def test_anio_invalido_422(cliente, params):
    assert cliente.get(URL, params=params).status_code == 422


def test_anio_maximo_valido(cliente):
    assert cliente.get(URL, params={"anio": 9999}).status_code == 200


def test_un_comprobante_activo_cuenta_uno(cliente, crear_venta):
    crear_venta(datetime(2025, 3, 3, 12))
    assert _total(cliente.get(URL, params={"anio": 2025}).json()) == 1


def test_dos_comprobantes_activos_cuentan_uno(cliente, crear_venta):
    crear_venta(datetime(2025, 3, 3, 12), comprobantes=(True, True))
    assert _total(cliente.get(URL, params={"anio": 2025}).json()) == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"activa": False},
        {"comprobantes": ()},
        {"comprobantes": (False, False)},
    ],
)
def test_exclusiones(cliente, crear_venta, kwargs):
    crear_venta(datetime(2025, 3, 3, 12), **kwargs)
    assert _total(cliente.get(URL, params={"anio": 2025}).json()) == 0


def test_bordes_del_anio(cliente, crear_venta):
    crear_venta(datetime(2025, 1, 1, 0, 0, 0))
    crear_venta(datetime(2025, 12, 31, 23, 59, 59))
    crear_venta(datetime(2026, 1, 1, 0, 0, 0))
    crear_venta(datetime(2024, 12, 31, 23, 59, 59))
    cuerpo = cliente.get(URL, params={"anio": 2025}).json()
    assert _total(cuerpo) == 2
    assert cuerpo["por_mes"][0]["cantidad"] == 1
    assert cuerpo["por_mes"][11]["cantidad"] == 1
