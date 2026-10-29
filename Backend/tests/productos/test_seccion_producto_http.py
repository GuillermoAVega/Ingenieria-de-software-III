"""HTTP de la asignación de sección a Plato, Bebida y Postre (CAT-S y SEC-30)."""
from sqlalchemy import func, select

from src.productos.models import Producto

CUERPO_PLATO = {"nombre": "Milanesa", "precio": "1500.00", "cant_personas": 2}


def _plato(**cambios):
    return {**CUERPO_PLATO, **cambios}


def _crear_plato(cliente, **cambios):
    respuesta = cliente.post("/productos/platos", json=_plato(**cambios))
    assert respuesta.status_code == 201
    return respuesta.json()


def test_cat_s_06_modificar_la_seccion_de_un_plato(cliente, crear_seccion, persistir):
    uno, otro = persistir(crear_seccion("Uno"), crear_seccion("Otro"))
    plato = _crear_plato(cliente, seccion_id=uno)

    respuesta = cliente.put(f"/productos/platos/{plato['id']}", json=_plato(seccion_id=otro))

    assert respuesta.status_code == 200
    assert respuesta.json()["seccion_id"] == otro


def test_cat_s_07_put_sin_seccion_id_desasigna_la_seccion(cliente, crear_seccion, persistir):
    plato = _crear_plato(cliente, seccion_id=persistir(crear_seccion()))

    respuesta = cliente.put(f"/productos/platos/{plato['id']}", json=_plato())

    assert respuesta.status_code == 200
    assert respuesta.json()["seccion_id"] is None
    assert cliente.get(f"/productos/platos/{plato['id']}").json()["seccion_id"] is None


def test_cat_s_08_put_con_seccion_inexistente_responde_422_y_conserva_la_seccion(
    cliente, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion())
    plato = _crear_plato(cliente, seccion_id=seccion_id)

    respuesta = cliente.put(f"/productos/platos/{plato['id']}", json=_plato(seccion_id=999))

    assert respuesta.status_code == 422
    assert respuesta.json() == {
        "detail": [
            {
                "loc": ["body", "seccion_id"],
                "msg": respuesta.json()["detail"][0]["msg"],
                "type": "seccion_inexistente",
                "ids": [999],
            }
        ]
    }
    assert cliente.get(f"/productos/platos/{plato['id']}").json()["seccion_id"] == seccion_id


def test_cat_s_09_bebida_y_postre_aceptan_y_rechazan_seccion_id_en_el_put(
    cliente, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion())
    casos = {
        "bebidas": {"nombre": "Cerveza", "precio": "800.00", "es_alcoholica": True},
        "postres": {"nombre": "Flan", "precio": "600.00"},
    }
    for ruta, cuerpo in casos.items():
        creado = cliente.post(f"/productos/{ruta}", json=cuerpo).json()
        url = f"/productos/{ruta}/{creado['id']}"

        valido = cliente.put(url, json={**cuerpo, "seccion_id": seccion_id})
        invalido = cliente.put(url, json={**cuerpo, "seccion_id": 999})

        assert valido.status_code == 200
        assert valido.json()["seccion_id"] == seccion_id
        assert invalido.status_code == 422


def test_cat_s_10_la_consulta_por_id_expone_seccion_id(cliente, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion())
    postre = cliente.post(
        "/productos/postres",
        json={"nombre": "Flan", "precio": "600.00", "seccion_id": seccion_id},
    ).json()

    respuesta = cliente.get(f"/productos/postres/{postre['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json()["seccion_id"] == seccion_id


def test_cat_s_11_asignar_seccion_a_un_postre_dado_de_baja(
    cliente, crear_seccion, crear_postre, persistir
):
    seccion_id = persistir(crear_seccion())
    postre = crear_postre()
    postre.dado_de_baja = True
    postre_id = persistir(postre)

    respuesta = cliente.put(
        f"/productos/postres/{postre_id}",
        json={"nombre": "Flan", "precio": "600.00", "dado_de_baja": True, "seccion_id": seccion_id},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert respuesta.json()["seccion_id"] == seccion_id


def test_cat_s_12_la_seccion_no_afecta_la_unicidad_del_nombre(
    cliente, crear_seccion, persistir
):
    dos, tres = persistir(crear_seccion("Dos"), crear_seccion("Tres"))
    _crear_plato(cliente, seccion_id=dos)

    respuesta = cliente.post("/productos/platos", json=_plato(seccion_id=tres))

    assert respuesta.status_code == 409


def test_cat_s_13_seccion_id_de_tipo_invalido_responde_422(cliente):
    respuesta = cliente.post("/productos/platos", json=_plato(seccion_id="abc"))

    assert respuesta.status_code == 422


def test_cat_s_14_el_404_tiene_prioridad_sobre_el_422_de_seccion(cliente):
    respuesta = cliente.put("/productos/platos/999", json=_plato(seccion_id=888))

    assert respuesta.status_code == 404


def test_cat_s_15_el_422_de_esquema_tiene_prioridad_sobre_el_de_seccion(
    cliente, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion())
    plato = _crear_plato(cliente, seccion_id=seccion_id)

    respuesta = cliente.put(
        f"/productos/platos/{plato['id']}", json=_plato(precio="0", seccion_id=999)
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] != "seccion_inexistente"
    assert cliente.get(f"/productos/platos/{plato['id']}").json() == plato


def test_cat_s_18_la_seccion_inexistente_tiene_prioridad_sobre_el_nombre_duplicado(cliente):
    _crear_plato(cliente, nombre="Milanesa")
    tarta = _crear_plato(cliente, nombre="Tarta")

    respuesta = cliente.put(
        f"/productos/platos/{tarta['id']}", json=_plato(nombre="Milanesa", seccion_id=999)
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "seccion_inexistente"


def test_sec_30_el_put_de_la_seccion_no_altera_los_productos_asignados(cliente):
    seccion = cliente.post("/secciones", json={"nombre": "Entradas"}).json()
    plato = _crear_plato(cliente, seccion_id=seccion["id"])

    modificada = cliente.put(f"/secciones/{seccion['id']}", json={"nombre": "Aperitivos"})
    assert modificada.status_code == 200

    # Un PUT del plato que no toca la sección (la reenvía) la conserva
    reenviado = cliente.put(
        f"/productos/platos/{plato['id']}", json=_plato(seccion_id=seccion["id"])
    )
    assert reenviado.status_code == 200
    assert cliente.get(f"/productos/platos/{plato['id']}").json()["seccion_id"] == seccion["id"]


def test_cat_s_03_no_crea_producto_con_seccion_inexistente_en_ningun_subtipo(cliente, sesion):
    cuerpos = {
        "platos": _plato(seccion_id=999),
        "bebidas": {"nombre": "Cerveza", "precio": "800.00", "es_alcoholica": True, "seccion_id": 999},
        "postres": {"nombre": "Flan", "precio": "600.00", "seccion_id": 999},
    }
    for ruta, cuerpo in cuerpos.items():
        assert cliente.post(f"/productos/{ruta}", json=cuerpo).status_code == 422

    assert sesion.scalar(select(func.count()).select_from(Producto)) == 0
