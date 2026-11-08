from datetime import date, datetime
from decimal import Decimal

import pytest

from tests.promociones.ayudas import RUTA
from tests.promociones.ayudas import post as _post
from tests.promociones.ayudas import total as _total


# ---- POST -------------------------------------------------------------


def test_pro_29_campos_de_precio_ignorados(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promo = promocionar(esc["productos"], descuento="10.00")
    r = _post(cliente, esc, precio_unitario=1, precio_final=1, promocion_id=999)
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["precio_unitario"] == 100
    assert cuerpo["precio_final"] == 90
    assert cuerpo["promocion_id"] == promo


@pytest.mark.parametrize("valor", [None, "ausente"])
def test_pro_30_detalle_comanda_id_obligatorio(cliente, armar, valor):
    esc = armar()
    cuerpo = {"factura_id": esc["factura_id"], "cantidad": 1}
    if valor is None:
        cuerpo["detalle_comanda_id"] = None
    assert cliente.post(RUTA, json=cuerpo).status_code == 422


def test_pro_31_detalle_comanda_inexistente(cliente, armar):
    esc = armar()
    r = cliente.post(
        RUTA, json={"factura_id": esc["factura_id"], "detalle_comanda_id": 9999, "cantidad": 1}
    )
    assert r.status_code == 404
    assert cliente.get(RUTA).json() == []


def test_pro_32_detalle_de_otra_comanda(cliente, armar):
    esc, otra = armar(), armar()
    r = cliente.post(
        RUTA,
        json={
            "factura_id": esc["factura_id"],
            "detalle_comanda_id": otra["detalles"][0],
            "cantidad": 1,
        },
    )
    assert r.status_code == 400
    assert cliente.get(RUTA).json() == []


def test_pro_33_sin_promocion(cliente, armar):
    esc = armar(("100.00",))
    cuerpo = _post(cliente, esc, cantidad=2).json()
    assert cuerpo["promocion_id"] is None
    assert cuerpo["precio_final"] == 200


def test_pro_43_calculo_con_descuento(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promocionar(esc["productos"], descuento="15.00")
    cuerpo = _post(cliente, esc, cantidad=3).json()
    assert (cuerpo["precio_unitario"], cuerpo["precio_final"]) == (100, 255)


def test_pro_41_vigencia_usa_fecha_de_emision(cliente, armar, promocionar):
    # Vigente en HOY_FIJO (2026-06-15) pero no a la emisión (2026-05-10)
    esc = armar(("100.00",), emision=datetime(2026, 5, 10, 12, 0))
    promocionar(esc["productos"], desde=date(2026, 6, 1), hasta=date(2026, 6, 30))
    cuerpo = _post(cliente, esc).json()
    assert cuerpo["promocion_id"] is None
    assert cuerpo["precio_final"] == 100


def test_pro_42_promocion_posterior_no_afecta_lineas(cliente, armar, promocionar):
    esc = armar(("100.00",))
    linea = _post(cliente, esc).json()
    promocionar(esc["productos"], descuento="50.00")
    actual = cliente.get(f"{RUTA}/{linea['id']}").json()
    assert actual["promocion_id"] is None
    assert actual["precio_final"] == 100


def test_pro_46_snapshot_precio_unitario(cliente, armar, sesion):
    from src.productos.models import Producto

    esc = armar(("100.00",))
    linea = _post(cliente, esc).json()
    sesion.get(Producto, esc["productos"][0]).precio = Decimal("150.00")
    sesion.commit()
    sesion.close()
    assert cliente.get(f"{RUTA}/{linea['id']}").json()["precio_unitario"] == 100


# ---- PUT --------------------------------------------------------------


def test_pro_47_cambio_de_cantidad(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promo = promocionar(esc["productos"], descuento="10.00")
    linea = _post(cliente, esc).json()
    r = cliente.put(f"{RUTA}/{linea['id']}", json={"cantidad": 2}).json()
    assert r["precio_final"] == 180 and r["promocion_id"] == promo


def test_pro_48_cambio_de_cantidad_recalcula_con_candidatas_vigentes(cliente, armar, promocionar):
    esc = armar(("100.00",))
    linea = _post(cliente, esc).json()
    promo = promocionar(esc["productos"], descuento="50.00")
    r = cliente.put(f"{RUTA}/{linea['id']}", json={"cantidad": 2}).json()
    assert r["promocion_id"] == promo and r["precio_final"] == 100
    assert _total(cliente, esc["factura_id"]) == 100


def test_pro_49_cambio_de_detalle_redetecta(cliente, armar, promocionar):
    esc = armar(("100.00", "40.00"))
    promo_b = promocionar([esc["productos"][1]], descuento="25.00")
    linea = _post(cliente, esc, indice=0).json()
    r = cliente.put(
        f"{RUTA}/{linea['id']}", json={"detalle_comanda_id": esc["detalles"][1], "cantidad": 2}
    ).json()
    assert r["promocion_id"] == promo_b
    assert r["precio_unitario"] == 40
    assert r["precio_final"] == 60


def test_pro_50_mismo_detalle_conserva_el_snapshot(cliente, armar, promocionar, sesion):
    from src.productos.models import Producto

    esc = armar(("100.00",))
    linea = _post(cliente, esc).json()
    promo = promocionar(esc["productos"], descuento="50.00")
    sesion.get(Producto, esc["productos"][0]).precio = Decimal("300.00")
    sesion.commit()
    sesion.close()
    r = cliente.put(
        f"{RUTA}/{linea['id']}", json={"detalle_comanda_id": esc["detalles"][0]}
    ).json()
    # El grupo se recalcula con el snapshot existente (100), no con el precio actual (300)
    assert r["precio_unitario"] == 100
    assert r["promocion_id"] == promo and r["precio_final"] == 50


def test_pro_51_precios_en_put_ignorados(cliente, armar, promocionar):
    esc = armar(("100.00",))
    linea = _post(cliente, esc).json()
    r = cliente.put(
        f"{RUTA}/{linea['id']}",
        json={"cantidad": 2, "precio_unitario": 1, "precio_final": 1, "promocion_id": 5},
    ).json()
    assert (r["precio_unitario"], r["precio_final"], r["promocion_id"]) == (100, 200, None)


def test_pro_52_put_con_detalle_inexistente(cliente, armar):
    esc = armar(("100.00",))
    linea = _post(cliente, esc).json()
    r = cliente.put(f"{RUTA}/{linea['id']}", json={"detalle_comanda_id": 9999})
    assert r.status_code == 404
    assert cliente.get(f"{RUTA}/{linea['id']}").json() == linea


def test_put_con_detalle_comanda_null_rechazado(cliente, armar):
    esc = armar(("100.00",))
    linea = _post(cliente, esc).json()
    r = cliente.put(f"{RUTA}/{linea['id']}", json={"detalle_comanda_id": None})
    assert r.status_code == 422


def test_put_linea_inexistente(cliente):
    assert cliente.put(f"{RUTA}/999", json={"cantidad": 1}).status_code == 404


# ---- Totales ----------------------------------------------------------


def test_pro_53_total_tras_crear_lineas(cliente, armar, promocionar):
    esc = armar(("100.00", "10.00"))
    promocionar([esc["productos"][0]], descuento="15.00")
    _post(cliente, esc, indice=0, cantidad=3)
    _post(cliente, esc, indice=1)
    assert _total(cliente, esc["factura_id"]) == 265


def test_pro_54_total_tras_modificar_cantidad(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promocionar(esc["productos"], descuento="10.00")
    linea = _post(cliente, esc).json()
    assert _total(cliente, esc["factura_id"]) == 90
    cliente.put(f"{RUTA}/{linea['id']}", json={"cantidad": 2})
    assert _total(cliente, esc["factura_id"]) == 180


def test_pro_55_total_tras_eliminar_linea(cliente, armar):
    esc = armar(("100.00", "10.00"))
    primera = _post(cliente, esc, indice=0).json()
    _post(cliente, esc, indice=1)
    assert cliente.delete(f"{RUTA}/{primera['id']}").status_code == 204
    assert _total(cliente, esc["factura_id"]) == 10


def test_pro_56_total_tras_baja_de_promocion(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promo = promocionar(esc["productos"], descuento="10.00")
    linea = _post(cliente, esc).json()
    assert cliente.delete(f"/promociones/{promo}").status_code == 204
    assert _total(cliente, esc["factura_id"]) == 90
    assert cliente.get(f"{RUTA}/{linea['id']}").json() == linea


def test_pro_68_baja_de_producto_conserva_precios(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promocionar(esc["productos"], descuento="10.00")
    linea = _post(cliente, esc).json()
    r = cliente.delete(f"/productos/platos/{esc['productos'][0]}")
    assert r.status_code == 204
    assert cliente.get(f"{RUTA}/{linea['id']}").json() == linea
    assert _total(cliente, esc["factura_id"]) == 90
