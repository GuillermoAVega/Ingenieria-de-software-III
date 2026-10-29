from datetime import date, timedelta

import pytest
from sqlalchemy import select

from src.productos_menu import services
from src.productos_menu.models import ProductoMenu

URL = "/productos-menu"
F1 = date(2026, 7, 1)
F2 = date(2026, 7, 2)


def _estado(sesion):
    """Conjunto persistido (id, producto_id, fecha); deja la transacción cerrada."""
    estado = set(
        sesion.execute(
            select(ProductoMenu.id, ProductoMenu.producto_id, ProductoMenu.fecha)
        ).all()
    )
    sesion.rollback()
    return estado


def _de_baja(producto):
    producto.dado_de_baja = True
    return producto


def test_pmd_03_la_respuesta_expone_solo_id_producto_id_y_fecha(
    cliente, crear_plato, persistir
):
    plato_id = persistir(crear_plato())

    respuesta = cliente.post(URL, json={"producto_id": plato_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 201
    assert set(respuesta.json()) == {"id", "producto_id", "fecha"}


def test_pmd_04_alta_valida_responde_201_y_persiste(
    cliente, sesion, crear_plato, persistir
):
    plato_id = persistir(crear_plato())

    respuesta = cliente.post(URL, json={"producto_id": plato_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["producto_id"] == plato_id
    assert cuerpo["fecha"] == "2026-07-01"
    assert _estado(sesion) == {(cuerpo["id"], plato_id, F1)}


def _alta_con_fecha(cliente, crear_plato, persistir, fecha):
    plato_id = persistir(crear_plato())
    return cliente.post(URL, json={"producto_id": plato_id, "fecha": fecha.isoformat()})


def test_pmd_05_fecha_pasada_responde_201(cliente, crear_plato, persistir):
    respuesta = _alta_con_fecha(cliente, crear_plato, persistir, date(2026, 6, 14))

    assert respuesta.status_code == 201
    assert respuesta.json()["fecha"] == "2026-06-14"


def test_pmd_06_fecha_de_hoy_responde_201(cliente, crear_plato, persistir, HOY):
    respuesta = _alta_con_fecha(cliente, crear_plato, persistir, HOY)

    assert respuesta.status_code == 201
    assert respuesta.json()["fecha"] == HOY.isoformat()


def test_pmd_07_fecha_futura_responde_201(cliente, crear_plato, persistir):
    respuesta = _alta_con_fecha(cliente, crear_plato, persistir, date(2026, 6, 16))

    assert respuesta.status_code == 201
    assert respuesta.json()["fecha"] == "2026-06-16"


def test_pmd_08_se_acepta_un_producto_de_cada_subtipo(
    cliente, crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo, persistir
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    ids = persistir(plato, postre, crear_bebida(), menu, crear_combo())

    for indice, producto_id in enumerate(ids):
        respuesta = cliente.post(
            URL,
            json={
                "producto_id": producto_id,
                "fecha": (F1 + timedelta(days=indice)).isoformat(),
            },
        )
        assert respuesta.status_code == 201, respuesta.json()


def _rechazo_422(cliente, sesion, crear_plato, persistir, cuerpo):
    persistir(crear_plato())
    respuesta = cliente.post(URL, json=cuerpo)
    assert respuesta.status_code == 422
    assert _estado(sesion) == set()


def test_pmd_09_producto_id_ausente_responde_422_sin_registro(
    cliente, sesion, crear_plato, persistir
):
    _rechazo_422(cliente, sesion, crear_plato, persistir, {"fecha": "2026-07-01"})


def test_pmd_10_producto_id_no_entero_responde_422_sin_registro(
    cliente, sesion, crear_plato, persistir
):
    _rechazo_422(
        cliente, sesion, crear_plato, persistir, {"producto_id": "abc", "fecha": "2026-07-01"}
    )


def test_pmd_11_fecha_ausente_responde_422_sin_registro(
    cliente, sesion, crear_plato, persistir
):
    _rechazo_422(cliente, sesion, crear_plato, persistir, {"producto_id": 1})


@pytest.mark.parametrize("fecha", ["no-es-una-fecha", "2026-02-30"])
def test_pmd_12_fecha_invalida_responde_422_sin_registro(
    cliente, sesion, crear_plato, persistir, fecha
):
    _rechazo_422(cliente, sesion, crear_plato, persistir, {"producto_id": 1, "fecha": fecha})


def test_pmd_13_producto_inexistente_responde_422_sin_registro(cliente, sesion):
    respuesta = cliente.post(URL, json={"producto_id": 999, "fecha": "2026-07-01"})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "producto_inexistente"
    assert _estado(sesion) == set()


def test_pmd_14_producto_dado_de_baja_responde_409_sin_registro(
    cliente, sesion, crear_plato, persistir
):
    plato_id = persistir(_de_baja(crear_plato()))

    respuesta = cliente.post(URL, json={"producto_id": plato_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 409
    assert _estado(sesion) == set()


def test_pmd_15_fecha_ocupada_responde_409_y_el_existente_queda_intacto(
    cliente, sesion, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    plato_id, menu_id = persistir(plato, crear_producto_menu(plato, F1))
    antes = _estado(sesion)

    respuesta = cliente.post(URL, json={"producto_id": plato_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 409
    assert antes == {(menu_id, plato_id, F1)}
    assert _estado(sesion) == antes


def test_pmd_16_esquema_invalido_prevalece_sobre_producto_inexistente(cliente):
    respuesta = cliente.post(URL, json={"producto_id": 999})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["loc"] == ["body", "fecha"]
    assert respuesta.json()["detail"][0]["type"] != "producto_inexistente"


def test_pmd_17_producto_inexistente_prevalece_sobre_fecha_ocupada(
    cliente, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    persistir(plato, crear_producto_menu(plato, F1))

    respuesta = cliente.post(URL, json={"producto_id": 999, "fecha": "2026-07-01"})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "producto_inexistente"


def test_pmd_18_producto_dado_de_baja_prevalece_sobre_fecha_ocupada(
    cliente, crear_plato, crear_postre, crear_producto_menu, persistir
):
    activo, de_baja = crear_plato(), _de_baja(crear_postre())
    _, baja_id, _ = persistir(activo, de_baja, crear_producto_menu(activo, F1))

    respuesta = cliente.post(URL, json={"producto_id": baja_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "El producto está dado de baja"}


def test_pmd_19_los_rechazos_422_y_409_no_cambian_lo_persistido(
    cliente, sesion, crear_plato, crear_postre, crear_producto_menu, persistir
):
    activo, de_baja = crear_plato(), _de_baja(crear_postre())
    activo_id, baja_id, _ = persistir(activo, de_baja, crear_producto_menu(activo, F1))
    antes = _estado(sesion)

    rechazos = [
        ({"producto_id": activo_id}, 422),
        ({"producto_id": 999, "fecha": "2026-07-05"}, 422),
        ({"producto_id": baja_id, "fecha": "2026-07-05"}, 409),
        ({"producto_id": activo_id, "fecha": "2026-07-01"}, 409),
    ]
    for cuerpo, codigo in rechazos:
        assert cliente.post(URL, json=cuerpo).status_code == codigo
        assert _estado(sesion) == antes


def test_pmd_20_carrera_con_la_misma_fecha_responde_409_y_no_500(
    cliente, monkeypatch, crear_plato, persistir
):
    plato_id = persistir(crear_plato())
    monkeypatch.setattr(services, "_verificar_fecha_libre", lambda *_a, **_k: None)
    cuerpo = {"producto_id": plato_id, "fecha": "2026-07-01"}

    assert cliente.post(URL, json=cuerpo).status_code == 201
    segunda = cliente.post(URL, json=cuerpo)

    assert segunda.status_code == 409
    assert segunda.json() == {"detail": "Ya existe un menú del día en esa fecha"}


def test_pmd_40_el_mismo_producto_en_dos_fechas_responde_201_ambas(
    cliente, crear_plato, persistir
):
    plato_id = persistir(crear_plato())

    primera = cliente.post(URL, json={"producto_id": plato_id, "fecha": "2026-07-01"})
    segunda = cliente.post(URL, json={"producto_id": plato_id, "fecha": "2026-07-02"})

    assert (primera.status_code, segunda.status_code) == (201, 201)
