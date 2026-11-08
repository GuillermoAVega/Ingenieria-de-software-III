from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import Comanda, DetalleComanda, DetalleFactura, Factura
from src.promociones.models import Promocion

RUTA = "/promociones"


def _cuerpo(productos_ids, **extra):
    base = {
        "nombre": "Promo",
        "fecha_desde": "2026-06-01",
        "fecha_hasta": "2026-06-30",
        "productos_ids": productos_ids,
    }
    return {**base, **extra}


@pytest.fixture
def plato_id(persistir, crear_plato):
    return persistir(crear_plato())


def _cantidad(sesion):
    return sesion.query(Promocion).count()


def test_plc_01_alta_lleva_paga(cliente, plato_id):
    r = cliente.post(RUTA, json=_cuerpo([plato_id], tipo="lleva_paga", lleva=3, paga=2))
    assert r.status_code == 201
    cuerpo = r.json()
    assert (cuerpo["tipo"], cuerpo["lleva"], cuerpo["paga"]) == ("lleva_paga", 3, 2)
    assert cuerpo["descuento"] is None


def test_plc_02_tipo_faltante(cliente, sesion, plato_id):
    r = cliente.post(RUTA, json=_cuerpo([plato_id], descuento="10"))
    assert r.status_code == 422
    assert _cantidad(sesion) == 0


def test_plc_03_tipo_desconocido(cliente, plato_id):
    r = cliente.post(RUTA, json=_cuerpo([plato_id], tipo="otro", descuento="10"))
    assert r.status_code == 422


@pytest.mark.parametrize("extra", [{"lleva": 2}, {"paga": 1}])
def test_plc_04_porcentaje_con_lleva_o_paga(cliente, sesion, plato_id, extra):
    r = cliente.post(
        RUTA, json=_cuerpo([plato_id], tipo="porcentaje", descuento="10", **extra)
    )
    assert r.status_code == 422
    assert _cantidad(sesion) == 0


@pytest.mark.parametrize("extra", [{}, {"descuento": None}])
def test_plc_05_porcentaje_sin_descuento(cliente, plato_id, extra):
    r = cliente.post(RUTA, json=_cuerpo([plato_id], tipo="porcentaje", **extra))
    assert r.status_code == 422


def test_plc_06_lleva_paga_con_descuento(cliente, sesion, plato_id):
    r = cliente.post(
        RUTA,
        json=_cuerpo([plato_id], tipo="lleva_paga", lleva=2, paga=1, descuento="10"),
    )
    assert r.status_code == 422
    assert _cantidad(sesion) == 0


@pytest.mark.parametrize("lleva,paga", [(2, 2), (2, 3)])
def test_plc_07_lleva_no_mayor_que_paga(cliente, plato_id, lleva, paga):
    r = cliente.post(
        RUTA, json=_cuerpo([plato_id], tipo="lleva_paga", lleva=lleva, paga=paga)
    )
    assert r.status_code == 422


def test_plc_08_paga_menor_que_uno(cliente, plato_id):
    r = cliente.post(RUTA, json=_cuerpo([plato_id], tipo="lleva_paga", lleva=2, paga=0))
    assert r.status_code == 422


@pytest.mark.parametrize("extra", [{"lleva": 2}, {"paga": 1}])
def test_plc_09_falta_lleva_o_paga(cliente, plato_id, extra):
    r = cliente.post(RUTA, json=_cuerpo([plato_id], tipo="lleva_paga", **extra))
    assert r.status_code == 422


@pytest.mark.parametrize("lleva,paga", [(2.5, 1), (3, 1.5), ("3", 2)])
def test_plc_10_lleva_y_paga_no_enteros(cliente, plato_id, lleva, paga):
    r = cliente.post(
        RUTA, json=_cuerpo([plato_id], tipo="lleva_paga", lleva=lleva, paga=paga)
    )
    assert r.status_code == 422


def test_plc_11_respuesta_porcentaje(cliente, plato_id):
    r = cliente.post(RUTA, json=_cuerpo([plato_id], tipo="porcentaje", descuento="15"))
    cuerpo = cliente.get(f"{RUTA}/{r.json()['id']}").json()
    assert cuerpo["tipo"] == "porcentaje"
    assert float(cuerpo["descuento"]) == 15.0
    assert cuerpo["lleva"] is None and cuerpo["paga"] is None


def test_plc_12_combo_en_lleva_paga(cliente, persistir, crear_combo):
    combo_id = persistir(crear_combo())
    r = cliente.post(RUTA, json=_cuerpo([combo_id], tipo="lleva_paga", lleva=2, paga=1))
    assert r.status_code == 201


def test_plc_19_cambio_de_tipo_sin_uso(cliente, persistir, crear_plato, crear_promocion):
    plato = crear_plato()
    plato_id, promocion_id = persistir(plato, crear_promocion([plato]))
    r = cliente.put(
        f"{RUTA}/{promocion_id}",
        json=_cuerpo([plato_id], tipo="lleva_paga", lleva=2, paga=1),
    )
    assert r.status_code == 200
    assert r.json()["tipo"] == "lleva_paga" and r.json()["descuento"] is None


def test_plc_21_put_lleva_paga_invalido(cliente, persistir, crear_plato, crear_promocion):
    plato = crear_plato()
    plato_id, promocion_id = persistir(plato, crear_promocion([plato]))
    r = cliente.put(
        f"{RUTA}/{promocion_id}",
        json=_cuerpo([plato_id], tipo="lleva_paga", lleva=2, paga=2),
    )
    assert r.status_code == 422
    assert cliente.get(f"{RUTA}/{promocion_id}").json()["tipo"] == "porcentaje"


def test_plc_22_lleva_paga_sin_unidades_gratis_no_es_aplicacion(
    cliente, sesion, persistir, crear_plato, crear_promocion
):
    from datetime import datetime, time

    plato = crear_plato()
    promo = crear_promocion([plato], tipo="lleva_paga", descuento=None, lleva=3, paga=2)
    plato_id, promocion_id = persistir(plato, promo)
    comanda = Comanda(fecha=date(2026, 6, 15), hora=time(12), mozo_id=1, mesa_id=1)
    sesion.add(comanda)
    sesion.flush()
    detalle = DetalleComanda(comanda_id=comanda.id, producto_id=plato_id, cantidad=2)
    sesion.add(detalle)
    sesion.flush()
    factura = Factura(
        comanda_id=comanda.id, fecha_hora_emision=datetime(2026, 6, 15, 13), importe_total=0
    )
    sesion.add(factura)
    sesion.flush()
    sesion.add(
        DetalleFactura(
            factura_id=factura.id, detalle_comanda_id=detalle.id,
            precio_unitario=10.0, cantidad=2, precio_final=20.0, promocion_id=None,
        )
    )
    sesion.commit()
    r = cliente.put(
        f"{RUTA}/{promocion_id}",
        json=_cuerpo([plato_id], tipo="lleva_paga", lleva=3, paga=2, nombre="Otra"),
    )
    assert r.status_code == 200


@pytest.mark.parametrize(
    "campos",
    [
        {"tipo": "porcentaje", "descuento": None},
        {"tipo": "porcentaje", "descuento": 10, "lleva": 2, "paga": 1},
        {"tipo": "lleva_paga", "descuento": 10, "lleva": 2, "paga": 1},
        {"tipo": "lleva_paga", "descuento": None, "lleva": 2, "paga": 2},
        {"tipo": "lleva_paga", "descuento": None, "lleva": 2, "paga": 0},
        {"tipo": "lleva_paga", "descuento": None, "lleva": 2, "paga": None},
        {"tipo": "otro", "descuento": 10},
    ],
)
def test_plc_23_la_base_rechaza_tipos_inconsistentes(sesion, crear_plato, campos):
    plato = crear_plato()
    sesion.add(
        Promocion(
            nombre="P", fecha_desde=date(2026, 6, 1), fecha_hasta=date(2026, 6, 30),
            productos=[plato], **campos,
        )
    )
    with pytest.raises(IntegrityError):
        sesion.flush()


def test_plc_23_la_base_acepta_lleva_paga_valida(sesion, crear_plato):
    plato = crear_plato()
    sesion.add(
        Promocion(
            nombre="P", fecha_desde=date(2026, 6, 1), fecha_hasta=date(2026, 6, 30),
            tipo="lleva_paga", lleva=3, paga=2, productos=[plato],
        )
    )
    sesion.flush()
