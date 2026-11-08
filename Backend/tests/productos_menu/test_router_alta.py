from datetime import date, timedelta

import pytest
from sqlalchemy import select

from src.productos_menu import services
from src.productos_menu.models import ProductoMenu

URL = "/productos-menu"
F1 = date(2026, 7, 1)
F2 = date(2026, 7, 2)


def _estado(sesion):
    """Conjunto persistido (id, menu_del_dia_id, fecha); deja la transacción cerrada."""
    estado = set(
        sesion.execute(
            select(ProductoMenu.id, ProductoMenu.menu_del_dia_id, ProductoMenu.fecha)
        ).all()
    )
    sesion.rollback()
    return estado


def _de_baja(producto):
    producto.dado_de_baja = True
    return producto


def test_pmd_03_la_respuesta_expone_solo_id_producto_id_y_fecha(
    cliente, crear_menu_del_dia, persistir
):
    menu_del_dia_id = persistir(crear_menu_del_dia())

    respuesta = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 201
    assert set(respuesta.json()) == {"id", "menu_del_dia_id", "fecha"}


def test_pmd_04_alta_valida_responde_201_y_persiste(
    cliente, sesion, crear_menu_del_dia, persistir
):
    menu_del_dia_id = persistir(crear_menu_del_dia())

    respuesta = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["menu_del_dia_id"] == menu_del_dia_id
    assert cuerpo["fecha"] == "2026-07-01"
    assert _estado(sesion) == {(cuerpo["id"], menu_del_dia_id, F1)}


def _alta_con_fecha(cliente, crear_menu_del_dia, persistir, fecha):
    menu_del_dia_id = persistir(crear_menu_del_dia())
    return cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": fecha.isoformat()})


@pytest.mark.parametrize("dias", [-1, -365], ids=["ayer", "lejana"])
def test_pmd_05_fecha_pasada_responde_422_de_campo_sin_registro(
    cliente, sesion, crear_menu_del_dia, persistir, HOY, dias
):
    respuesta = _alta_con_fecha(cliente, crear_menu_del_dia, persistir, HOY + timedelta(days=dias))

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == [
        {
            "loc": ["body", "fecha"],
            "msg": "La fecha del menú del día no puede ser anterior a hoy",
            "type": "fecha_pasada",
        }
    ]
    assert sesion.scalars(select(ProductoMenu)).all() == []


def test_fecha_pasada_prevalece_sobre_menu_del_dia_dado_de_baja(
    cliente, sesion, crear_menu_del_dia, persistir, HOY
):
    mdd = crear_menu_del_dia()
    mdd.dado_de_baja = True
    menu_del_dia_id = persistir(mdd)

    respuesta = cliente.post(
        URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": (HOY - timedelta(days=1)).isoformat()}
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "fecha_pasada"


def test_menu_del_dia_inexistente_prevalece_sobre_fecha_pasada(cliente, HOY):
    respuesta = cliente.post(
        URL, json={"menu_del_dia_id": 999, "fecha": (HOY - timedelta(days=1)).isoformat()}
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "menu_del_dia_inexistente"


def test_pmd_06_fecha_de_hoy_responde_201(cliente, crear_menu_del_dia, persistir, HOY):
    respuesta = _alta_con_fecha(cliente, crear_menu_del_dia, persistir, HOY)

    assert respuesta.status_code == 201
    assert respuesta.json()["fecha"] == HOY.isoformat()


def test_pmd_07_fecha_futura_responde_201(cliente, crear_menu_del_dia, persistir, HOY):
    respuesta = _alta_con_fecha(cliente, crear_menu_del_dia, persistir, HOY + timedelta(days=1))

    assert respuesta.status_code == 201
    assert respuesta.json()["fecha"] == "2026-06-16"


def test_pmd_08_se_acepta_un_menu_del_dia(cliente, crear_menu_del_dia, persistir):
    menu_del_dia_id = persistir(crear_menu_del_dia())

    respuesta = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": F1.isoformat()})

    assert respuesta.status_code == 201, respuesta.json()


@pytest.mark.parametrize("subtipo", ["plato", "bebida", "postre", "menu", "combo"])
def test_pmd_05_producto_que_no_es_menu_del_dia_responde_422_sin_registro(
    cliente, sesion, crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo, persistir, subtipo
):
    plato, postre = crear_plato(), crear_postre()
    producto = {
        "plato": lambda: plato,
        "bebida": crear_bebida,
        "postre": lambda: postre,
        "menu": lambda: crear_menu(plato, postre),
        "combo": crear_combo,
    }[subtipo]()
    menu_del_dia_id = persistir(plato, postre, producto)[-1]

    respuesta = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": F1.isoformat()})

    assert respuesta.status_code == 422
    assert respuesta.json() == {
        "detail": [
            {
                "loc": ["body", "menu_del_dia_id"],
                "msg": "El producto indicado no es un menú del día",
                "type": "producto_no_menu_del_dia",
                "ids": [menu_del_dia_id],
            }
        ]
    }
    assert _estado(sesion) == set()


def test_pmd_05b_no_menu_del_dia_dado_de_baja_responde_422_antes_que_409(
    cliente, crear_bebida, persistir
):
    bebida = crear_bebida()
    bebida.dado_de_baja = True
    menu_del_dia_id = persistir(bebida)

    respuesta = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": F1.isoformat()})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "producto_no_menu_del_dia"


def _rechazo_422(cliente, sesion, crear_menu_del_dia, persistir, cuerpo):
    persistir(crear_menu_del_dia())
    respuesta = cliente.post(URL, json=cuerpo)
    assert respuesta.status_code == 422
    assert _estado(sesion) == set()


def test_pmd_09_producto_id_ausente_responde_422_sin_registro(
    cliente, sesion, crear_menu_del_dia, persistir
):
    _rechazo_422(cliente, sesion, crear_menu_del_dia, persistir, {"fecha": "2026-07-01"})


def test_pmd_10_producto_id_no_entero_responde_422_sin_registro(
    cliente, sesion, crear_menu_del_dia, persistir
):
    _rechazo_422(
        cliente, sesion, crear_menu_del_dia, persistir, {"menu_del_dia_id": "abc", "fecha": "2026-07-01"}
    )


def test_pmd_11_fecha_ausente_responde_422_sin_registro(
    cliente, sesion, crear_menu_del_dia, persistir
):
    _rechazo_422(cliente, sesion, crear_menu_del_dia, persistir, {"menu_del_dia_id": 1})


@pytest.mark.parametrize("fecha", ["no-es-una-fecha", "2026-02-30"])
def test_pmd_12_fecha_invalida_responde_422_sin_registro(
    cliente, sesion, crear_menu_del_dia, persistir, fecha
):
    _rechazo_422(cliente, sesion, crear_menu_del_dia, persistir, {"menu_del_dia_id": 1, "fecha": fecha})


def test_pmd_13_menu_del_dia_inexistente_responde_422_sin_registro(cliente, sesion):
    respuesta = cliente.post(URL, json={"menu_del_dia_id": 999, "fecha": "2026-07-01"})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "menu_del_dia_inexistente"
    assert _estado(sesion) == set()


def test_pmd_14_menu_del_dia_dado_de_baja_responde_409_sin_registro(
    cliente, sesion, crear_menu_del_dia, persistir
):
    menu_del_dia_id = persistir(_de_baja(crear_menu_del_dia()))

    respuesta = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 409
    assert _estado(sesion) == set()


def test_pmd_15_fecha_ocupada_responde_409_y_el_existente_queda_intacto(
    cliente, sesion, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, menu_id = persistir(mdd, crear_producto_menu(mdd, F1))
    antes = _estado(sesion)

    respuesta = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 409
    assert antes == {(menu_id, menu_del_dia_id, F1)}
    assert _estado(sesion) == antes


def test_pmd_16_esquema_invalido_prevalece_sobre_menu_del_dia_inexistente(cliente):
    respuesta = cliente.post(URL, json={"menu_del_dia_id": 999})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["loc"] == ["body", "fecha"]
    assert respuesta.json()["detail"][0]["type"] != "menu_del_dia_inexistente"


def test_pmd_17_menu_del_dia_inexistente_prevalece_sobre_fecha_ocupada(
    cliente, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia()
    persistir(mdd, crear_producto_menu(mdd, F1))

    respuesta = cliente.post(URL, json={"menu_del_dia_id": 999, "fecha": "2026-07-01"})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "menu_del_dia_inexistente"


def test_pmd_18_menu_del_dia_dado_de_baja_prevalece_sobre_fecha_ocupada(
    cliente, crear_menu_del_dia, crear_postre, crear_producto_menu, persistir
):
    activo, de_baja = crear_menu_del_dia(), _de_baja(crear_menu_del_dia())
    _, baja_id, _ = persistir(activo, de_baja, crear_producto_menu(activo, F1))

    respuesta = cliente.post(URL, json={"menu_del_dia_id": baja_id, "fecha": "2026-07-01"})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "El menú del día está dado de baja"}


def test_pmd_19_los_rechazos_422_y_409_no_cambian_lo_persistido(
    cliente, sesion, crear_menu_del_dia, crear_postre, crear_producto_menu, persistir
):
    activo, de_baja = crear_menu_del_dia(), _de_baja(crear_menu_del_dia())
    activo_id, baja_id, _ = persistir(activo, de_baja, crear_producto_menu(activo, F1))
    antes = _estado(sesion)

    rechazos = [
        ({"menu_del_dia_id": activo_id}, 422),
        ({"menu_del_dia_id": 999, "fecha": "2026-07-05"}, 422),
        ({"menu_del_dia_id": baja_id, "fecha": "2026-07-05"}, 409),
        ({"menu_del_dia_id": activo_id, "fecha": "2026-07-01"}, 409),
    ]
    for cuerpo, codigo in rechazos:
        assert cliente.post(URL, json=cuerpo).status_code == codigo
        assert _estado(sesion) == antes


def test_pmd_20_carrera_con_la_misma_fecha_responde_409_y_no_500(
    cliente, monkeypatch, crear_menu_del_dia, persistir
):
    menu_del_dia_id = persistir(crear_menu_del_dia())
    monkeypatch.setattr(services, "_verificar_fecha_libre", lambda *_a, **_k: None)
    cuerpo = {"menu_del_dia_id": menu_del_dia_id, "fecha": "2026-07-01"}

    assert cliente.post(URL, json=cuerpo).status_code == 201
    segunda = cliente.post(URL, json=cuerpo)

    assert segunda.status_code == 409
    assert segunda.json() == {"detail": "Ya existe un menú del día en esa fecha"}


def test_pmd_40_el_mismo_producto_en_dos_fechas_responde_201_ambas(
    cliente, crear_menu_del_dia, persistir
):
    menu_del_dia_id = persistir(crear_menu_del_dia())

    primera = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": "2026-07-01"})
    segunda = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": "2026-07-02"})

    assert (primera.status_code, segunda.status_code) == (201, 201)
