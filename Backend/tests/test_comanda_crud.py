from datetime import date, datetime, timedelta

import pytest

from src.atencion.models import Atencion
from src.cliente.models import Cliente
from src.mesa.models import Mesa
from src.mozo.models import Mozo
from src.reserva.estados import EstadoReserva
from src.reserva.models import Reserva, ReservaMesa
from src.sector.models import Sector


@pytest.fixture
def escenario(sesion):
    """Dos sectores con un mozo cada uno y 3 mesas en el primero, 1 en el segundo."""
    sector = Sector(nombre="Salón", apto_fumadores=False, piso=1)
    otro_sector = Sector(nombre="Terraza", apto_fumadores=True, piso=1)
    mozo = Mozo(nombre="Luis", nro_legajo=1)
    mozo_otro = Mozo(nombre="Ana", nro_legajo=2)
    mesas = [Mesa(capacidad=4, disponible=True, sector=sector) for _ in range(3)]
    mesa_otro = Mesa(capacidad=4, disponible=True, sector=otro_sector)
    cli = Cliente(dni="1", nombre="Ana", apellido="P", telefono="1")
    sesion.add_all([sector, otro_sector, mozo, mozo_otro, *mesas, mesa_otro, cli])
    sesion.flush()
    sesion.add_all([
        Atencion(fecha_desde=date(2020, 1, 1), mozo_id=mozo.id, sector_id=sector.id),
        Atencion(fecha_desde=date(2020, 1, 1), mozo_id=mozo_otro.id, sector_id=otro_sector.id),
    ])
    sesion.commit()
    datos = {
        "mesas": [m.id for m in mesas],
        "mesa_otro": mesa_otro.id,
        "mozo": mozo.id,
        "mozo_otro": mozo_otro.id,
        "cliente": cli.id,
    }
    sesion.close()
    return datos


def _disponible(sesion, mesa_id):
    valor = sesion.get(Mesa, mesa_id).disponible
    sesion.close()  # el motor de pruebas comparte conexión: no dejar transacción abierta
    return valor


def _estado_reserva(sesion, reserva_id):
    valor = sesion.get(Reserva, reserva_id).estado
    sesion.close()
    return valor


def test_crear_sin_mesas_da_mensaje_claro(cliente, escenario):
    r = cliente.post("/comandas", json={})
    assert r.status_code == 400
    assert "al menos una mesa" in r.json()["detail"]


def test_crear_cliente_inexistente(cliente, escenario):
    r = cliente.post("/comandas", json={"mesa_id": escenario["mesas"][0], "cliente_id": 999})
    assert r.status_code == 400


def test_put_mesa_ids_ya_no_da_500_y_sincroniza(cliente, sesion, escenario):
    m1, m2, m3 = escenario["mesas"]
    c = cliente.post("/comandas", json={"mesa_id": m1}).json()
    assert _disponible(sesion, m1) is False

    r = cliente.put(f"/comandas/{c['id']}", json={"mesa_ids": [m2, m3]})

    assert r.status_code == 200
    assert r.json()["mesa_ids"] == [m2, m3]
    assert r.json()["mesa_id"] == m2
    assert _disponible(sesion, m1) is True
    assert _disponible(sesion, m2) is False
    assert _disponible(sesion, m3) is False


def test_put_mesa_id_distinta_cambia_mesa(cliente, sesion, escenario):
    m1, m2, _ = escenario["mesas"]
    c = cliente.post("/comandas", json={"mesa_id": m1}).json()
    r = cliente.put(f"/comandas/{c['id']}", json={"mesa_id": m2})
    assert r.status_code == 200
    assert r.json()["mesa_ids"] == [m2]
    assert _disponible(sesion, m1) is True
    assert _disponible(sesion, m2) is False


def test_put_mismas_mesas_no_cambia_nada(cliente, sesion, escenario):
    m1, _, _ = escenario["mesas"]
    c = cliente.post("/comandas", json={"mesa_id": m1}).json()
    r = cliente.put(f"/comandas/{c['id']}", json={"mesa_id": m1, "mozo_id": escenario["mozo"]})
    assert r.status_code == 200
    assert _disponible(sesion, m1) is False


def test_put_mesa_ocupada_o_de_otro_sector_se_rechaza(cliente, sesion, escenario):
    m1, m2, _ = escenario["mesas"]
    cliente.post("/comandas", json={"mesa_id": m2})
    c = cliente.post("/comandas", json={"mesa_id": m1}).json()

    assert cliente.put(f"/comandas/{c['id']}", json={"mesa_ids": [m2]}).status_code == 400
    assert cliente.put(f"/comandas/{c['id']}", json={"mesa_ids": [m1, escenario["mesa_otro"]]}).status_code == 400
    assert _disponible(sesion, m1) is False  # sin cambios


def test_put_valida_mozo_cliente_y_reserva(cliente, escenario):
    c = cliente.post("/comandas", json={"mesa_id": escenario["mesas"][0]}).json()
    url = f"/comandas/{c['id']}"

    assert cliente.put(url, json={"mozo_id": 999}).status_code == 400
    assert cliente.put(url, json={"mozo_id": escenario["mozo_otro"]}).status_code == 400  # otro sector
    assert cliente.put(url, json={"cliente_id": 999}).status_code == 400
    assert cliente.put(url, json={"reserva_id": 999}).status_code == 400
    assert cliente.put(url, json={"mozo_id": escenario["mozo"], "cliente_id": escenario["cliente"]}).status_code == 200
    assert cliente.put(url, json={"cliente_id": None}).json()["cliente_id"] is None


def test_delete_libera_mesas(cliente, sesion, escenario):
    m1, m2, _ = escenario["mesas"]
    c = cliente.post("/comandas", json={"mesa_ids": [m1, m2]}).json()
    assert cliente.delete(f"/comandas/{c['id']}").status_code == 204
    assert _disponible(sesion, m1) is True
    assert _disponible(sesion, m2) is True
    assert cliente.get(f"/comandas/{c['id']}").status_code == 404


def test_delete_con_factura_activa_sigue_bloqueado(cliente, sesion, escenario, crear_postre):
    m1 = escenario["mesas"][0]
    c = cliente.post("/comandas", json={"mesa_id": m1}).json()
    p = crear_postre()
    sesion.add(p)
    sesion.flush()
    pid = p.id
    sesion.commit()
    sesion.close()
    d = cliente.post(f"/comandas/{c['id']}/detalles", json={"producto_id": pid, "cantidad": 1})
    if d.status_code not in (200, 201):  # ruta de alta de detalle distinta
        d = cliente.post("/detalles-comanda", json={"comanda_id": c["id"], "producto_id": pid, "cantidad": 1})
    cliente.put(f"/detalles-comanda/{d.json()['id']}", json={"entregado": True})
    assert cliente.put(f"/comandas/{c['id']}", json={"estado": "cerrada"}).status_code == 200
    assert cliente.post("/facturas", json={"comanda_id": c["id"], "importe_total": 0}).status_code in (200, 201)

    r = cliente.delete(f"/comandas/{c['id']}")

    assert r.status_code == 400
    assert "factura" in r.json()["detail"]


def test_delete_comanda_de_reserva_revierte_reserva(cliente, sesion, escenario):
    m1 = escenario["mesas"][0]
    momento = datetime.now().replace(microsecond=0) + timedelta(minutes=5)
    reserva = Reserva(
        fecha=momento.date(),
        hora=momento.time(),
        cant_comensales=2,
        cliente_id=escenario["cliente"],
        mesas_asociadas=[ReservaMesa(mesa_id=m1)],
    )
    sesion.add(reserva)
    sesion.commit()
    reserva_id = reserva.id
    sesion.close()

    c = cliente.post("/comandas", json={"reserva_id": reserva_id})
    assert c.status_code == 201
    assert _estado_reserva(sesion, reserva_id) == EstadoReserva.CON_COMANDA

    assert cliente.delete(f"/comandas/{c.json()['id']}").status_code == 204

    assert _estado_reserva(sesion, reserva_id) == EstadoReserva.PENDIENTE
    assert _disponible(sesion, m1) is True
    # y se puede volver a crear la comanda desde esa reserva
    assert cliente.post("/comandas", json={"reserva_id": reserva_id}).status_code == 201


def test_comanda_cerrada_no_permite_volver_a_pendiente(cliente, sesion, escenario, crear_postre):
    c = cliente.post("/comandas", json={"mesa_id": escenario["mesas"][0]}).json()
    p = crear_postre()
    sesion.add(p)
    sesion.flush()
    pid = p.id
    sesion.commit()
    sesion.close()
    d = cliente.post("/detalles-comanda", json={"comanda_id": c["id"], "producto_id": pid, "cantidad": 1}).json()
    url = f"/detalles-comanda/{d['id']}"
    assert cliente.put(url, json={"entregado": True}).status_code == 200
    assert cliente.put(f"/comandas/{c['id']}", json={"estado": "cerrada"}).status_code == 200

    r = cliente.put(url, json={"entregado": False})
    assert r.status_code == 400
    assert "pendiente" in r.json()["detail"]
    assert cliente.put(url, json={"entregado": True}).status_code == 200

    assert cliente.put(f"/comandas/{c['id']}", json={"estado": "abierta"}).status_code == 200
    assert cliente.put(url, json={"entregado": False}).status_code == 200
