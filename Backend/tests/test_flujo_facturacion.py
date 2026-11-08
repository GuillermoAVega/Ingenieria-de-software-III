import pytest

COMANDA = {"fecha": "2026-10-22", "hora": "21:00:00", "mozo_id": 1, "mesa_id": 3}


@pytest.fixture
def productos(persistir, crear_plato, crear_bebida, crear_postre):
    """Tres productos reales (ids autogenerados); devuelve sus ids."""
    return persistir(
        crear_plato(nombre="Milanesa", precio="50.00"),
        crear_bebida(nombre="Cerveza", precio="30.00"),
        crear_postre(nombre="Flan", precio="20.00"),
    )


def _comanda_con_factura(cliente, producto_id):
    comanda = cliente.post(
        "/comandas",
        json={**COMANDA, "detalles": [{"cantidad": 2, "producto_id": producto_id, "observaciones": "sin sal"}]},
    ).json()
    assert cliente.post("/facturas", json={"comanda_id": comanda["id"]}).status_code == 400  # abierta
    assert cliente.put(f"/comandas/{comanda['id']}", json={"estado": "cerrada"}).status_code == 200
    factura = cliente.post("/facturas", json={"comanda_id": comanda["id"]}).json()
    return comanda, factura


def test_medio_pago_crud(cliente):
    r = cliente.post("/medios-pago", json={"descripcion": "Efectivo"})
    assert r.status_code == 201
    id = r.json()["id"]
    assert cliente.post("/medios-pago", json={"descripcion": "Efectivo"}).status_code == 400
    assert cliente.put(f"/medios-pago/{id}", json={"descripcion": "Tarjeta"}).json()["descripcion"] == "Tarjeta"
    assert cliente.delete(f"/medios-pago/{id}").status_code == 204
    assert cliente.get(f"/medios-pago/{id}").status_code == 404


def test_comanda_con_detalles_y_baja(cliente, productos):
    plato, bebida, postre = productos
    comanda = cliente.post(
        "/comandas", json={**COMANDA, "detalles": [{"cantidad": 1, "producto_id": plato}]}
    ).json()
    assert len(comanda["detalles"]) == 1
    assert cliente.post("/detalles-comanda", json={"comanda_id": comanda["id"], "cantidad": 3, "producto_id": bebida}).status_code == 201
    assert len(cliente.get(f"/comandas/{comanda['id']}/detalles").json()) == 2
    assert cliente.post("/detalles-comanda", json={"comanda_id": 999, "cantidad": 1, "producto_id": plato}).status_code == 404
    assert cliente.post("/detalles-comanda", json={"comanda_id": comanda["id"], "cantidad": 0, "producto_id": plato}).status_code == 422
    assert cliente.delete(f"/comandas/{comanda['id']}").status_code == 204
    assert cliente.get(f"/comandas/{comanda['id']}").status_code == 404


def test_factura_total_y_comprobantes(cliente, productos):
    comanda, factura = _comanda_con_factura(cliente, productos[0])
    assert cliente.post("/facturas", json={"comanda_id": comanda["id"]}).status_code == 400  # una por comanda
    dc = comanda["detalles"][0]["id"]
    d = cliente.post(
        "/detalles-factura",
        json={"factura_id": factura["id"], "detalle_comanda_id": dc, "cantidad": 2},
    )
    assert d.status_code == 201 and d.json()["precio_final"] == 100
    assert cliente.get(f"/facturas/{factura['id']}").json()["importe_total"] == 100
    cliente.put(f"/detalles-factura/{d.json()['id']}", json={"cantidad": 3})
    assert cliente.get(f"/facturas/{factura['id']}").json()["importe_total"] == 150

    medio = cliente.post("/medios-pago", json={"descripcion": "Efectivo"}).json()
    pago = {"factura_id": factura["id"], "medio_pago_id": medio["id"], "importe": 100}
    c = cliente.post("/comprobantes-pago", json=pago)
    assert c.status_code == 201
    assert cliente.post("/comprobantes-pago", json={**pago, "importe": 60}).status_code == 400  # excede total
    assert cliente.delete(f"/medios-pago/{medio['id']}").status_code == 400  # en uso
    assert cliente.delete(f"/facturas/{factura['id']}").status_code == 400  # con comprobante activo
    assert cliente.delete(f"/comprobantes-pago/{c.json()['id']}").status_code == 204
    assert cliente.delete(f"/facturas/{factura['id']}").status_code == 204
    assert cliente.delete(f"/comandas/{comanda['id']}").status_code == 204


def test_comanda_oculta_detalles_quitados_y_permite_limpiar_cliente(cliente, productos):
    plato, bebida, _ = productos
    comanda = cliente.post(
        "/comandas",
        json={**COMANDA, "cliente_id": 4, "detalles": [{"cantidad": 1, "producto_id": plato}, {"cantidad": 1, "producto_id": bebida}]},
    ).json()
    cliente.delete(f"/detalles-comanda/{comanda['detalles'][0]['id']}")
    r = cliente.put(f"/comandas/{comanda['id']}", json={"cliente_id": None}).json()
    assert r["cliente_id"] is None and len(r["detalles"]) == 1
    assert cliente.put(f"/comandas/{comanda['id']}", json={"estado": "cerrada"}).json()["estado"] == "cerrada"


def test_comanda_cerrada_no_admite_cambios_en_productos(cliente, productos):
    plato, _, postre = productos
    comanda = cliente.post(
        "/comandas", json={**COMANDA, "detalles": [{"cantidad": 1, "producto_id": plato}]}
    ).json()
    det = comanda["detalles"][0]["id"]
    cliente.put(f"/comandas/{comanda['id']}", json={"estado": "cerrada"})
    assert cliente.post("/detalles-comanda", json={"comanda_id": comanda["id"], "cantidad": 1, "producto_id": postre}).status_code == 400
    assert cliente.put(f"/detalles-comanda/{det}", json={"cantidad": 5}).status_code == 400
    assert cliente.delete(f"/detalles-comanda/{det}").status_code == 400
    assert cliente.put(f"/comandas/{comanda['id']}", json={"mesa_id": 9}).status_code == 400
    assert cliente.put(f"/detalles-comanda/{det}", json={"entregado": True}).status_code == 200
    cliente.put(f"/comandas/{comanda['id']}", json={"estado": "abierta"})
    assert cliente.post("/detalles-comanda", json={"comanda_id": comanda["id"], "cantidad": 1, "producto_id": postre}).status_code == 201
