from datetime import date

import pytest

from src.promociones.models import Promocion

RUTA = "/promociones"


def _cuerpo(productos_ids, **extra):
    return {
        "nombre": "Promo verano",
        "fecha_desde": "2026-06-01",
        "fecha_hasta": "2026-06-30",
        "tipo": "porcentaje",
        "descuento": "15.50",
        **extra,
        "productos_ids": productos_ids,
    }


@pytest.fixture
def plato_id(persistir, crear_plato):
    return persistir(crear_plato())


def _cantidad(sesion):
    return sesion.query(Promocion).count()


def test_pro_03_alta_valida(cliente, plato_id):
    respuesta = cliente.post(RUTA, json=_cuerpo([plato_id]))
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dado_de_baja"] is False
    assert cuerpo["nombre"] == "Promo verano"
    assert cuerpo["fecha_desde"] == "2026-06-01"
    assert cuerpo["fecha_hasta"] == "2026-06-30"
    assert float(cuerpo["descuento"]) == 15.5
    assert cuerpo["productos_ids"] == [plato_id]
    assert isinstance(cuerpo["id"], int)


def test_el_nombre_se_recorta(cliente, plato_id):
    respuesta = cliente.post(RUTA, json=_cuerpo([plato_id], nombre="  Promo  "))
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Promo"


def test_pro_01_productos_ids_ordenados(cliente, persistir, crear_plato, crear_bebida, crear_postre):
    ids = persistir(crear_plato(), crear_bebida(), crear_postre())
    respuesta = cliente.post(RUTA, json=_cuerpo(list(reversed(ids))))
    assert respuesta.status_code == 201
    assert respuesta.json()["productos_ids"] == sorted(ids)


def test_pro_02_un_producto_en_varias_promociones(cliente, plato_id):
    primera = cliente.post(RUTA, json=_cuerpo([plato_id]))
    segunda = cliente.post(RUTA, json=_cuerpo([plato_id], nombre="Otra"))
    assert primera.status_code == 201
    assert segunda.status_code == 201
    assert primera.json()["id"] != segunda.json()["id"]


@pytest.mark.parametrize("nombre", ["", "   "])
def test_pro_04_nombre_vacio(cliente, sesion, plato_id, nombre):
    respuesta = cliente.post(RUTA, json=_cuerpo([plato_id], nombre=nombre))
    assert respuesta.status_code == 422
    assert _cantidad(sesion) == 0


def test_pro_04_nombre_faltante(cliente, sesion, plato_id):
    cuerpo = _cuerpo([plato_id])
    del cuerpo["nombre"]
    assert cliente.post(RUTA, json=cuerpo).status_code == 422
    assert _cantidad(sesion) == 0


@pytest.mark.parametrize("descuento", ["0", "-5", "100.01"])
def test_pro_05_descuento_fuera_de_rango(cliente, sesion, plato_id, descuento):
    respuesta = cliente.post(RUTA, json=_cuerpo([plato_id], descuento=descuento))
    assert respuesta.status_code == 422
    assert _cantidad(sesion) == 0


def test_pro_06_descuento_en_el_limite_superior(cliente, plato_id):
    respuesta = cliente.post(RUTA, json=_cuerpo([plato_id], descuento="100"))
    assert respuesta.status_code == 201


def test_pro_07_descuento_con_mas_de_dos_decimales(cliente, sesion, plato_id):
    respuesta = cliente.post(RUTA, json=_cuerpo([plato_id], descuento="10.555"))
    assert respuesta.status_code == 422
    assert _cantidad(sesion) == 0


def test_pro_08_rango_de_fechas_invertido(cliente, sesion, plato_id):
    respuesta = cliente.post(
        RUTA,
        json=_cuerpo([plato_id], fecha_desde="2026-07-01", fecha_hasta="2026-06-30"),
    )
    assert respuesta.status_code == 422
    assert _cantidad(sesion) == 0


def test_pro_09_fechas_iguales_a_hoy(cliente, plato_id, HOY):
    respuesta = cliente.post(
        RUTA,
        json=_cuerpo([plato_id], fecha_desde=HOY.isoformat(), fecha_hasta=HOY.isoformat()),
    )
    assert respuesta.status_code == 201


def test_pro_10_fecha_hasta_vencida(cliente, sesion, plato_id):
    respuesta = cliente.post(
        RUTA,
        json=_cuerpo([plato_id], fecha_desde="2026-06-01", fecha_hasta="2026-06-14"),
    )
    assert respuesta.status_code == 422
    assert _cantidad(sesion) == 0


def test_pro_11_sin_productos(cliente, sesion, plato_id):
    assert cliente.post(RUTA, json=_cuerpo([])).status_code == 422
    cuerpo = _cuerpo([plato_id])
    del cuerpo["productos_ids"]
    assert cliente.post(RUTA, json=cuerpo).status_code == 422
    assert _cantidad(sesion) == 0


def test_productos_ids_duplicados(cliente, sesion, plato_id):
    respuesta = cliente.post(RUTA, json=_cuerpo([plato_id, plato_id]))
    assert respuesta.status_code == 422
    assert _cantidad(sesion) == 0


def test_pro_12_producto_inexistente(cliente, sesion, plato_id):
    respuesta = cliente.post(RUTA, json=_cuerpo([plato_id, 999, 998]))
    assert respuesta.status_code == 422
    error = respuesta.json()["detail"][0]
    assert error["type"] == "producto_inexistente"
    assert error["loc"] == ["body", "productos_ids"]
    assert error["ids"] == [998, 999]
    assert _cantidad(sesion) == 0


def test_pro_13_producto_dado_de_baja(cliente, sesion, persistir, crear_plato):
    plato = crear_plato()
    plato.dado_de_baja = True
    plato_id = persistir(plato)
    respuesta = cliente.post(RUTA, json=_cuerpo([plato_id]))
    assert respuesta.status_code == 409
    assert _cantidad(sesion) == 0


def test_pro_73_combo_en_una_promocion(cliente, persistir, crear_plato, crear_combo):
    combo_id = persistir(crear_combo(platos=[crear_plato()]))
    respuesta = cliente.post(RUTA, json=_cuerpo([combo_id]))
    assert respuesta.status_code == 201
    assert respuesta.json()["productos_ids"] == [combo_id]
