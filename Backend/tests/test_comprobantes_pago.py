from datetime import date

import pytest

from src.atencion.models import Atencion
from src.mesa.models import Mesa
from src.mozo.models import Mozo
from src.sector.models import Sector


@pytest.fixture
def factura(cliente, sesion, crear_plato):
    """Factura de $100 (2 x $50) de una comanda cerrada; devuelve su id."""
    sector = Sector(nombre="Salón", apto_fumadores=False, piso=1)
    mozo = Mozo(nombre="Luis", nro_legajo=1)
    mesa = Mesa(capacidad=4, disponible=True, sector=sector)
    plato = crear_plato(nombre="Milanesa", precio="50.00")
    sesion.add_all([sector, mozo, mesa, plato])
    sesion.flush()
    sesion.add(Atencion(fecha_desde=date(2020, 1, 1), mozo_id=mozo.id, sector_id=sector.id))
    mesa_id, plato_id = mesa.id, plato.id
    sesion.commit()
    sesion.close()

    comanda = cliente.post(
        "/comandas",
        json={"mesa_id": mesa_id, "detalles": [{"producto_id": plato_id, "cantidad": 2}]},
    ).json()
    for detalle in comanda["detalles"]:
        cliente.put(f"/detalles-comanda/{detalle['id']}", json={"entregado": True})
    assert cliente.put(f"/comandas/{comanda['id']}", json={"estado": "cerrada"}).status_code == 200
    factura = cliente.post("/facturas", json={"comanda_id": comanda["id"]}).json()
    linea = cliente.post(
        "/detalles-factura",
        json={
            "factura_id": factura["id"],
            "detalle_comanda_id": comanda["detalles"][0]["id"],
            "cantidad": 2,
        },
    )
    assert linea.status_code == 201
    assert cliente.get(f"/facturas/{factura['id']}").json()["importe_total"] == 100
    return factura["id"]


@pytest.fixture
def medio(cliente):
    return cliente.post("/medios-pago", json={"descripcion": "Efectivo"}).json()["id"]


def _pagar(cliente, factura, medio, importe):
    return cliente.post(
        "/comprobantes-pago",
        json={"factura_id": factura, "medio_pago_id": medio, "importe": importe},
    )


def test_pago_parcial_y_total(cliente, factura, medio):
    assert _pagar(cliente, factura, medio, 40).status_code == 201
    assert _pagar(cliente, factura, medio, 60).status_code == 201
    comprobantes = cliente.get(f"/facturas/{factura}/comprobantes").json()
    assert sorted(c["importe"] for c in comprobantes) == [40, 60]


def test_pago_que_excede_el_saldo_da_mensaje_claro(cliente, factura, medio):
    _pagar(cliente, factura, medio, 70)
    r = _pagar(cliente, factura, medio, 40)
    assert r.status_code == 400
    assert "saldo pendiente" in r.json()["detail"]
    assert "30.00" in r.json()["detail"]


def test_importe_debe_ser_positivo(cliente, factura, medio):
    assert _pagar(cliente, factura, medio, 0).status_code == 422
    assert _pagar(cliente, factura, medio, -5).status_code == 422


def test_medio_de_pago_dado_de_baja_no_se_puede_usar(cliente, factura, medio):
    assert cliente.delete(f"/medios-pago/{medio}").status_code == 204
    assert _pagar(cliente, factura, medio, 10).status_code == 404


def test_anular_pago_libera_saldo(cliente, factura, medio):
    pago = _pagar(cliente, factura, medio, 100).json()
    assert _pagar(cliente, factura, medio, 1).status_code == 400
    assert cliente.delete(f"/comprobantes-pago/{pago['id']}").status_code == 204
    assert _pagar(cliente, factura, medio, 100).status_code == 201


def test_factura_con_pago_activo_no_se_da_de_baja(cliente, factura, medio):
    pago = _pagar(cliente, factura, medio, 10).json()
    assert cliente.delete(f"/facturas/{factura}").status_code == 400
    assert cliente.delete(f"/comprobantes-pago/{pago['id']}").status_code == 204
    assert cliente.delete(f"/facturas/{factura}").status_code == 204
