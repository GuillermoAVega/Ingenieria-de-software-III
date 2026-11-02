COMANDA = {"fecha": "2026-10-22", "hora": "21:00:00", "mozo_id": 1, "mesa_id": 3}


def _comanda_con_factura(client):
    comanda = client.post(
        "/comandas",
        json={**COMANDA, "detalles": [{"cantidad": 2, "producto_id": 10, "observaciones": "sin sal"}]},
    ).json()
    assert client.post("/facturas", json={"comanda_id": comanda["id"]}).status_code == 400  # abierta
    assert client.put(f"/comandas/{comanda['id']}", json={"estado": "cerrada"}).status_code == 200
    factura = client.post("/facturas", json={"comanda_id": comanda["id"]}).json()
    return comanda, factura


def test_medio_pago_crud(client):
    r = client.post("/medios-pago", json={"descripcion": "Efectivo"})
    assert r.status_code == 201
    id = r.json()["id"]
    assert client.post("/medios-pago", json={"descripcion": "Efectivo"}).status_code == 400
    assert client.put(f"/medios-pago/{id}", json={"descripcion": "Tarjeta"}).json()["descripcion"] == "Tarjeta"
    assert client.delete(f"/medios-pago/{id}").status_code == 204
    assert client.get(f"/medios-pago/{id}").status_code == 404


def test_comanda_con_detalles_y_baja(client):
    comanda = client.post(
        "/comandas", json={**COMANDA, "detalles": [{"cantidad": 1, "producto_id": 5}]}
    ).json()
    assert len(comanda["detalles"]) == 1
    assert client.post("/detalles-comanda", json={"comanda_id": comanda["id"], "cantidad": 3, "producto_id": 6}).status_code == 201
    assert len(client.get(f"/comandas/{comanda['id']}/detalles").json()) == 2
    assert client.post("/detalles-comanda", json={"comanda_id": 999, "cantidad": 1, "producto_id": 1}).status_code == 404
    assert client.post("/detalles-comanda", json={"comanda_id": comanda["id"], "cantidad": 0, "producto_id": 1}).status_code == 422
    assert client.delete(f"/comandas/{comanda['id']}").status_code == 204
    assert client.get(f"/comandas/{comanda['id']}").status_code == 404


def test_factura_total_y_comprobantes(client):
    comanda, factura = _comanda_con_factura(client)
    assert client.post("/facturas", json={"comanda_id": comanda["id"]}).status_code == 400  # una por comanda
    dc = comanda["detalles"][0]["id"]
    d = client.post(
        "/detalles-factura",
        json={"factura_id": factura["id"], "detalle_comanda_id": dc, "precio_unitario": 50, "cantidad": 2},
    )
    assert d.status_code == 201 and d.json()["precio_final"] == 100
    assert client.get(f"/facturas/{factura['id']}").json()["importe_total"] == 100
    client.put(f"/detalles-factura/{d.json()['id']}", json={"cantidad": 3})
    assert client.get(f"/facturas/{factura['id']}").json()["importe_total"] == 150

    medio = client.post("/medios-pago", json={"descripcion": "Efectivo"}).json()
    pago = {"factura_id": factura["id"], "medio_pago_id": medio["id"], "importe": 100}
    c = client.post("/comprobantes-pago", json=pago)
    assert c.status_code == 201
    assert client.post("/comprobantes-pago", json={**pago, "importe": 60}).status_code == 400  # excede total
    assert client.delete(f"/medios-pago/{medio['id']}").status_code == 400  # en uso
    assert client.delete(f"/facturas/{factura['id']}").status_code == 400  # con comprobante activo
    assert client.delete(f"/comprobantes-pago/{c.json()['id']}").status_code == 204
    assert client.delete(f"/facturas/{factura['id']}").status_code == 204
    assert client.delete(f"/comandas/{comanda['id']}").status_code == 204


def test_comanda_oculta_detalles_quitados_y_permite_limpiar_cliente(client):
    comanda = client.post(
        "/comandas",
        json={**COMANDA, "cliente_id": 4, "detalles": [{"cantidad": 1, "producto_id": 5}, {"cantidad": 1, "producto_id": 6}]},
    ).json()
    client.delete(f"/detalles-comanda/{comanda['detalles'][0]['id']}")
    r = client.put(f"/comandas/{comanda['id']}", json={"cliente_id": None}).json()
    assert r["cliente_id"] is None and len(r["detalles"]) == 1
    assert client.put(f"/comandas/{comanda['id']}", json={"estado": "cerrada"}).json()["estado"] == "cerrada"


def test_comanda_cerrada_no_admite_cambios_en_productos(client):
    comanda = client.post(
        "/comandas", json={**COMANDA, "detalles": [{"cantidad": 1, "producto_id": 5}]}
    ).json()
    det = comanda["detalles"][0]["id"]
    client.put(f"/comandas/{comanda['id']}", json={"estado": "cerrada"})
    assert client.post("/detalles-comanda", json={"comanda_id": comanda["id"], "cantidad": 1, "producto_id": 7}).status_code == 400
    assert client.put(f"/detalles-comanda/{det}", json={"cantidad": 5}).status_code == 400
    assert client.delete(f"/detalles-comanda/{det}").status_code == 400
    assert client.put(f"/comandas/{comanda['id']}", json={"mesa_id": 9}).status_code == 400
    assert client.put(f"/detalles-comanda/{det}", json={"entregado": True}).status_code == 200
    client.put(f"/comandas/{comanda['id']}", json={"estado": "abierta"})
    assert client.post("/detalles-comanda", json={"comanda_id": comanda["id"], "cantidad": 1, "producto_id": 7}).status_code == 201
