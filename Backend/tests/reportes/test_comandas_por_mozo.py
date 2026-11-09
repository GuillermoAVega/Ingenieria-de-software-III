from datetime import date, datetime, time

from src.atencion import models as atencion_models  # noqa: F401
from src.models import Comanda, Factura
from src.mesa.models import Mesa
from src.mozo.models import Mozo
from src.sector.models import Sector

URL = "/reportes/comandas-por-mozo"


def test_reporte_agrupa_comandas_y_facturas_por_mozo(cliente, persistir):
    sector = Sector(nombre="Salón reporte", apto_fumadores=False, piso="Planta baja")
    mesa = Mesa(capacidad=4, disponible=True, sector=sector)
    mozo_ana = Mozo(nombre="Ana", nro_legajo=7101)
    mozo_luis = Mozo(nombre="Luis", nro_legajo=7102)
    mesa_id, ana_id, luis_id = persistir(mesa, mozo_ana, mozo_luis)

    ana_primera = Comanda(
        fecha=date(2026, 6, 1),
        hora=time(12),
        mozo_id=ana_id,
        mesa_id=mesa_id,
    )
    ana_segunda = Comanda(
        fecha=date(2026, 6, 15),
        hora=time(13),
        mozo_id=ana_id,
        mesa_id=mesa_id,
    )
    luis_comanda = Comanda(
        fecha=date(2026, 6, 15),
        hora=time(14),
        mozo_id=luis_id,
        mesa_id=mesa_id,
    )
    fuera_de_rango = Comanda(
        fecha=date(2026, 5, 31),
        hora=time(14),
        mozo_id=luis_id,
        mesa_id=mesa_id,
    )
    factura_ana = Factura(
        importe_total=1250.5,
        fecha_hora_emision=datetime(2026, 6, 1, 12),
        activo=True,
        comanda=ana_primera,
    )
    factura_luis = Factura(
        importe_total=800,
        fecha_hora_emision=datetime(2026, 6, 15, 14),
        activo=True,
        comanda=luis_comanda,
    )
    factura_anulada = Factura(
        importe_total=500,
        fecha_hora_emision=datetime(2026, 6, 15, 13),
        activo=False,
        comanda=ana_segunda,
    )
    persistir(
        ana_primera,
        ana_segunda,
        luis_comanda,
        fuera_de_rango,
        factura_ana,
        factura_luis,
        factura_anulada,
    )

    response = cliente.get(URL, params={"desde": "2026-06-01", "hasta": "2026-06-15"})

    assert response.status_code == 200
    cuerpo = response.json()
    assert cuerpo["desde"] == "2026-06-01"
    assert cuerpo["hasta"] == "2026-06-15"
    assert {
        fila["nombre"]: (fila["cantidad_comandas"], fila["importe_ventas"])
        for fila in cuerpo["por_mozo"]
    } == {
        "Ana": (2, 1250.5),
        "Luis": (1, 800),
    }


def test_reporte_excluye_comandas_inactivas(cliente, persistir):
    sector = Sector(nombre="Salón inactivo", apto_fumadores=False, piso="Planta baja")
    mesa = Mesa(capacidad=2, disponible=True, sector=sector)
    mozo = Mozo(nombre="Eva", nro_legajo=7103)
    mesa_id, mozo_id = persistir(mesa, mozo)
    comanda = Comanda(
        fecha=date(2026, 6, 10),
        hora=time(12),
        mozo_id=mozo_id,
        mesa_id=mesa_id,
        activo=False,
    )
    persistir(comanda)

    response = cliente.get(URL, params={"desde": "2026-06-01", "hasta": "2026-06-30"})

    assert response.status_code == 200
    assert response.json()["por_mozo"] == []


def test_reporte_requiere_fechas(cliente):
    assert cliente.get(URL).status_code == 422


def test_reporte_rechaza_rango_invertido(cliente):
    response = cliente.get(URL, params={"desde": "2026-06-16", "hasta": "2026-06-15"})

    assert response.status_code == 422
