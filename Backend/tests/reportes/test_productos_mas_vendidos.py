from datetime import date, datetime, time

import pytest

from src.atencion import models as atencion_models  # noqa: F401
from src.mesa.models import Mesa
from src.models import Comanda, DetalleComanda, DetalleFactura, Factura
from src.mozo.models import Mozo
from src.sector.models import Sector

URL = "/reportes/productos-mas-vendidos"
PERIODO = {"desde": "2026-06-01", "hasta": "2026-06-30"}


@pytest.fixture
def productos(persistir, crear_plato, crear_bebida, crear_postre):
    milanesa, cerveza, flan = persistir(
        crear_plato(nombre="Milanesa", precio="50.00"),
        crear_bebida(nombre="Cerveza", precio="30.00"),
        crear_postre(nombre="Flan", precio="20.00"),
    )
    return {"milanesa": milanesa, "cerveza": cerveza, "flan": flan}


@pytest.fixture
def facturar(persistir):
    """Crea comanda + factura con líneas [(producto_id, cantidad, precio_final, linea_activa)]."""
    sector = Sector(nombre="Salón ranking", apto_fumadores=False, piso="Planta baja")
    mesa = Mesa(capacidad=4, disponible=True, sector=sector)
    mozo = Mozo(nombre="Ana", nro_legajo=8101)
    mesa_id, mozo_id = persistir(mesa, mozo)

    def _facturar(emision, lineas, factura_activa=True):
        comanda = Comanda(fecha=emision.date(), hora=time(12), mozo_id=mozo_id, mesa_id=mesa_id)
        factura = Factura(
            importe_total=sum(precio for _, _, precio, _ in lineas),
            fecha_hora_emision=emision,
            activo=factura_activa,
            comanda=comanda,
        )
        detalles = []
        for producto_id, cantidad, precio_final, activa in lineas:
            detalle_comanda = DetalleComanda(
                comanda=comanda, producto_id=producto_id, cantidad=cantidad
            )
            detalles.append(
                DetalleFactura(
                    factura=factura,
                    detalle_comanda=detalle_comanda,
                    precio_unitario=precio_final / cantidad,
                    cantidad=cantidad,
                    precio_final=precio_final,
                    activo=activa,
                )
            )
        persistir(comanda, factura, *detalles)

    return _facturar


def _ranking(cliente, **params):
    respuesta = cliente.get(URL, params={**PERIODO, **params})
    assert respuesta.status_code == 200
    return respuesta.json()


def test_agrupa_y_ordena_por_unidades(cliente, productos, facturar):
    facturar(datetime(2026, 6, 5, 21), [(productos["milanesa"], 2, 100.0, True), (productos["cerveza"], 5, 150.0, True)])
    facturar(datetime(2026, 6, 20, 13), [(productos["milanesa"], 4, 200.0, True), (productos["flan"], 1, 20.0, True)])

    cuerpo = _ranking(cliente)

    assert cuerpo["desde"] == "2026-06-01" and cuerpo["hasta"] == "2026-06-30" and cuerpo["limite"] == 10
    assert [(p["nombre"], p["unidades"], p["importe"]) for p in cuerpo["productos"]] == [
        ("Milanesa", 6, 300.0),
        ("Cerveza", 5, 150.0),
        ("Flan", 1, 20.0),
    ]
    assert cuerpo["productos"][0]["tipo"]


def test_periodo_es_inclusivo_en_ambos_bordes(cliente, productos, facturar):
    facturar(datetime(2026, 5, 31, 23, 59, 59), [(productos["flan"], 9, 180.0, True)])
    facturar(datetime(2026, 6, 1, 0, 0, 0), [(productos["milanesa"], 1, 50.0, True)])
    facturar(datetime(2026, 6, 30, 23, 59, 59), [(productos["cerveza"], 2, 60.0, True)])
    facturar(datetime(2026, 7, 1, 0, 0, 0), [(productos["flan"], 9, 180.0, True)])

    nombres = {p["nombre"] for p in _ranking(cliente)["productos"]}

    assert nombres == {"Milanesa", "Cerveza"}


def test_ignora_facturas_y_lineas_dadas_de_baja(cliente, productos, facturar):
    facturar(datetime(2026, 6, 5, 21), [(productos["milanesa"], 3, 150.0, True)])
    facturar(datetime(2026, 6, 6, 21), [(productos["milanesa"], 50, 2500.0, True)], factura_activa=False)
    facturar(datetime(2026, 6, 7, 21), [(productos["cerveza"], 40, 1200.0, False)])

    productos_rank = _ranking(cliente)["productos"]

    assert [(p["nombre"], p["unidades"]) for p in productos_rank] == [("Milanesa", 3)]


def test_desempata_por_importe_y_luego_nombre(cliente, productos, facturar):
    facturar(
        datetime(2026, 6, 5, 21),
        [(productos["milanesa"], 2, 100.0, True), (productos["cerveza"], 2, 60.0, True), (productos["flan"], 2, 60.0, True)],
    )

    assert [p["nombre"] for p in _ranking(cliente)["productos"]] == ["Milanesa", "Cerveza", "Flan"]


def test_limite_recorta_el_ranking(cliente, productos, facturar):
    facturar(
        datetime(2026, 6, 5, 21),
        [(productos["milanesa"], 3, 150.0, True), (productos["cerveza"], 2, 60.0, True), (productos["flan"], 1, 20.0, True)],
    )

    cuerpo = _ranking(cliente, limite=2)

    assert cuerpo["limite"] == 2
    assert [p["nombre"] for p in cuerpo["productos"]] == ["Milanesa", "Cerveza"]


def test_periodo_sin_ventas_devuelve_lista_vacia(cliente):
    assert _ranking(cliente)["productos"] == []


def test_validaciones(cliente):
    assert cliente.get(URL).status_code == 422
    assert cliente.get(URL, params={"desde": "2026-06-30", "hasta": "2026-06-01"}).status_code == 422
    assert cliente.get(URL, params={**PERIODO, "limite": 0}).status_code == 422
    assert cliente.get(URL, params={**PERIODO, "limite": 51}).status_code == 422
