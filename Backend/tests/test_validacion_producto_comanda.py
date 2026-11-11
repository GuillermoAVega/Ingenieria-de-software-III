"""Validación de DetalleComanda.producto_id (PRO-57 a PRO-64, PRO-67, PRO-68, PRO-72)."""
from datetime import date, time

import pytest

from src.models import Comanda, DetalleComanda

COMANDA = {"fecha": "2026-06-15", "hora": "12:00:00", "mozo_id": 1, "mesa_id": 1}


@pytest.fixture(autouse=True)
def dependencias_comanda(preparar_dependencias_comanda):
    preparar_dependencias_comanda((1,))


@pytest.fixture
def plato(persistir, crear_plato):
    return persistir(crear_plato("Activo"))


@pytest.fixture
def baja(persistir, crear_plato):
    return persistir(crear_plato("Baja", dado_de_baja=True))


@pytest.fixture
def comanda_con_detalle(persistir, plato):
    comanda = Comanda(fecha=date(2026, 6, 15), hora=time(12), mozo_id=1, mesa_id=1)
    comanda.detalles.append(DetalleComanda(cantidad=1, producto_id=plato))
    return persistir(comanda)


def _detalle(comanda_id, producto_id):
    return {"comanda_id": comanda_id, "cantidad": 1, "producto_id": producto_id}


def _tipo_error(respuesta):
    return respuesta.json()["detail"][0]["type"]


def test_pro57_detalle_suelto_inexistente(cliente, comanda_con_detalle):
    r = cliente.post("/detalles-comanda", json=_detalle(comanda_con_detalle, 9999))
    assert r.status_code == 422
    assert _tipo_error(r) == "producto_inexistente"
    assert len(cliente.get("/detalles-comanda").json()) == 1


def test_pro58_anidado_inexistente_atomico(cliente, plato):
    cuerpo = {**COMANDA, "detalles": [
        {"cantidad": 1, "producto_id": plato}, {"cantidad": 1, "producto_id": 9999}]}
    r = cliente.post("/comandas", json=cuerpo)
    assert r.status_code == 422
    assert _tipo_error(r) == "producto_inexistente"
    assert cliente.get("/comandas").json() == []
    assert cliente.get("/detalles-comanda").json() == []


def test_pro59_put_inexistente(cliente, comanda_con_detalle, plato):
    r = cliente.put("/detalles-comanda/1", json={"producto_id": 9999})
    assert r.status_code == 422
    assert _tipo_error(r) == "producto_inexistente"
    assert cliente.get("/detalles-comanda/1").json()["producto_id"] == plato


def test_pro60_detalle_suelto_baja(cliente, comanda_con_detalle, baja):
    r = cliente.post("/detalles-comanda", json=_detalle(comanda_con_detalle, baja))
    assert r.status_code == 409
    assert len(cliente.get("/detalles-comanda").json()) == 1


def test_pro61_anidado_baja(cliente, plato, baja):
    cuerpo = {**COMANDA, "detalles": [
        {"cantidad": 1, "producto_id": plato}, {"cantidad": 1, "producto_id": baja}]}
    r = cliente.post("/comandas", json=cuerpo)
    assert r.status_code == 409
    assert cliente.get("/comandas").json() == []
    assert cliente.get("/detalles-comanda").json() == []


def test_pro62_put_a_baja(cliente, comanda_con_detalle, plato, baja):
    r = cliente.put("/detalles-comanda/1", json={"producto_id": baja})
    assert r.status_code == 409
    assert cliente.get("/detalles-comanda/1").json()["producto_id"] == plato


def test_pro63_put_sin_cambiar_producto_dado_de_baja_despues(
    cliente, comanda_con_detalle, plato, sesion
):
    from src.productos.models import Producto

    sesion.get(Producto, plato).dado_de_baja = True
    sesion.commit()
    sesion.close()
    r = cliente.put("/detalles-comanda/1", json={"cantidad": 5})
    assert r.status_code == 200
    assert r.json()["producto_id"] == plato
    assert r.json()["cantidad"] == 5


def test_put_mismo_producto_dado_de_baja_no_revalida(
    cliente, comanda_con_detalle, plato, sesion
):
    from src.productos.models import Producto

    sesion.get(Producto, plato).dado_de_baja = True
    sesion.commit()
    sesion.close()
    r = cliente.put("/detalles-comanda/1", json={"producto_id": plato})
    assert r.status_code == 200


def test_pro64_producto_activo_valido(cliente, comanda_con_detalle, plato):
    r = cliente.post("/detalles-comanda", json=_detalle(comanda_con_detalle, plato))
    assert r.status_code == 201


def test_pro72_null_en_post_suelto(cliente, comanda_con_detalle):
    r = cliente.post("/detalles-comanda", json=_detalle(comanda_con_detalle, None))
    assert r.status_code == 422


def test_pro72_null_anidado(cliente):
    r = cliente.post("/comandas", json={**COMANDA, "detalles": [
        {"cantidad": 1, "producto_id": None}]})
    assert r.status_code == 422
    assert cliente.get("/comandas").json() == []


def test_pro72_null_en_put(cliente, comanda_con_detalle, plato):
    r = cliente.put("/detalles-comanda/1", json={"producto_id": None})
    assert r.status_code == 422
    assert cliente.get("/detalles-comanda/1").json()["producto_id"] == plato


def test_pro67_comanda_nueva_con_producto_dado_de_baja_por_delete(cliente, plato):
    assert cliente.delete(f"/productos/platos/{plato}").status_code == 204
    r = cliente.post("/comandas", json={**COMANDA, "detalles": [
        {"cantidad": 1, "producto_id": plato}]})
    assert r.status_code == 409


def test_pro68_baja_no_altera_lineas_existentes(cliente, comanda_con_detalle, plato):
    assert cliente.delete(f"/productos/platos/{plato}").status_code == 204
    detalle = cliente.get("/detalles-comanda/1").json()
    assert detalle["producto_id"] == plato
    assert detalle["cantidad"] == 1
