from datetime import date

from src.productos.menus_ejecutivos.models import MenuEjecutivo

CUERPO_PLATO = {"nombre": "Milanesa", "precio": "1500.00", "cant_personas": 2}
CUERPO_BEBIDA = {"nombre": "Cerveza", "precio": "800.00", "es_alcoholica": True}
CUERPO_POSTRE = {"nombre": "Flan", "precio": "600.00"}


def _de_baja(producto):
    producto.dado_de_baja = True
    return producto


def test_ld_01_delete_de_plato_libre_responde_204_sin_cuerpo_y_queda_de_baja(
    cliente, crear_plato, persistir
):
    plato_id = persistir(crear_plato())

    respuesta = cliente.delete(f"/productos/platos/{plato_id}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert cliente.get(f"/productos/platos/{plato_id}").json()["dado_de_baja"] is True


def test_ld_02_delete_de_bebida_desconocida_responde_404(cliente):
    assert cliente.delete("/productos/bebidas/999").status_code == 404


def test_ld_02_delete_con_id_de_otro_subtipo_responde_404(cliente, crear_bebida, persistir):
    bebida_id = persistir(crear_bebida())

    assert cliente.delete(f"/productos/platos/{bebida_id}").status_code == 404
    assert cliente.get(f"/productos/bebidas/{bebida_id}").json()["dado_de_baja"] is False


def test_ld_03_delete_repetido_de_postre_responde_204_sin_cuerpo(cliente, crear_postre, persistir):
    postre_id = persistir(_de_baja(crear_postre()))

    respuesta = cliente.delete(f"/productos/postres/{postre_id}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert cliente.get(f"/productos/postres/{postre_id}").json()["dado_de_baja"] is True


def test_ld_04_put_con_baja_y_precio_invalido_responde_422_y_sigue_activo(
    cliente, crear_plato, persistir
):
    plato_id = persistir(crear_plato())

    respuesta = cliente.put(
        f"/productos/platos/{plato_id}",
        json={**CUERPO_PLATO, "dado_de_baja": True, "precio": "0"},
    )

    assert respuesta.status_code == 422
    assert cliente.get(f"/productos/platos/{plato_id}").json()["dado_de_baja"] is False


def test_ld_05_put_con_dado_de_baja_false_sobre_activo_es_una_edicion_normal(
    cliente, crear_plato, persistir
):
    plato_id = persistir(crear_plato(nombre="Milanesa"))

    respuesta = cliente.put(
        f"/productos/platos/{plato_id}",
        json={**CUERPO_PLATO, "dado_de_baja": False, "descripcion": "Nueva"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is False
    assert respuesta.json()["descripcion"] == "Nueva"


def test_ld_06_put_con_dado_de_baja_false_y_nombre_vacio_responde_422(
    cliente, crear_plato, persistir
):
    plato_id = persistir(crear_plato())

    respuesta = cliente.put(
        f"/productos/platos/{plato_id}",
        json={**CUERPO_PLATO, "dado_de_baja": False, "nombre": ""},
    )

    assert respuesta.status_code == 422


def test_ld_07_put_sin_dado_de_baja_sobre_postre_de_baja_sigue_de_baja(
    cliente, crear_postre, persistir
):
    postre_id = persistir(_de_baja(crear_postre()))

    respuesta = cliente.put(
        f"/productos/postres/{postre_id}", json={**CUERPO_POSTRE, "descripcion": "Nueva"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert respuesta.json()["descripcion"] == "Nueva"


def test_ld_08_put_con_dado_de_baja_true_da_de_baja_un_postre(cliente, crear_postre, persistir):
    postre_id = persistir(crear_postre())

    respuesta = cliente.put(
        f"/productos/postres/{postre_id}", json={**CUERPO_POSTRE, "dado_de_baja": True}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert cliente.get(f"/productos/postres/{postre_id}").json()["dado_de_baja"] is True


def test_ld_09_put_con_dado_de_baja_false_reactiva_un_plato(cliente, crear_plato, persistir):
    plato_id = persistir(_de_baja(crear_plato()))

    respuesta = cliente.put(
        f"/productos/platos/{plato_id}", json={**CUERPO_PLATO, "dado_de_baja": False}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is False


def test_ld_10_y_ld_23_delete_bloqueado_por_menu_activo_responde_409_y_nada_cambia(
    cliente, sesion, crear_plato, crear_postre, crear_menu, persistir
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    plato_id, _, menu_id = persistir(plato, postre, menu)

    respuesta = cliente.delete(f"/productos/platos/{plato_id}")

    assert respuesta.status_code == 409
    assert respuesta.json()["bloqueantes"] == [menu_id]
    assert cliente.get(f"/productos/platos/{plato_id}").json()["dado_de_baja"] is False
    assert sesion.get(MenuEjecutivo, menu_id).dado_de_baja is False


def test_ld_11_put_de_bebida_bloqueado_por_combo_activo_responde_409_con_el_combo(
    cliente, crear_bebida, crear_combo, persistir
):
    bebida = crear_bebida()
    combo = crear_combo(bebidas=[bebida])
    bebida_id, combo_id = persistir(bebida, combo)

    respuesta = cliente.put(
        f"/productos/bebidas/{bebida_id}", json={**CUERPO_BEBIDA, "dado_de_baja": True}
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["bloqueantes"] == [combo_id]
    assert cliente.get(f"/productos/bebidas/{bebida_id}").json()["dado_de_baja"] is False


def test_ld_12_combo_con_fecha_desde_futura_bloquea_la_baja_del_postre(
    cliente, crear_postre, crear_combo, persistir
):
    postre = crear_postre()
    combo = crear_combo(desde=date(2026, 7, 1), hasta=date(2026, 7, 31), postres=[postre])
    postre_id, combo_id = persistir(postre, combo)

    respuesta = cliente.delete(f"/productos/postres/{postre_id}")

    assert respuesta.status_code == 409
    assert respuesta.json()["bloqueantes"] == [combo_id]


def test_ld_13_multiples_bloqueantes_se_listan_ordenados(
    cliente, crear_plato, crear_postre, crear_menu, crear_combo, persistir
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    combo = crear_combo(platos=[plato])
    plato_id, _, menu_id, combo_id = persistir(plato, postre, menu, combo)

    respuesta = cliente.delete(f"/productos/platos/{plato_id}")

    assert respuesta.status_code == 409
    assert respuesta.json()["bloqueantes"] == sorted([menu_id, combo_id])
    assert len(respuesta.json()["bloqueantes"]) == 2


def test_ld_14_menu_de_baja_y_combo_vencido_no_bloquean_la_baja(
    cliente, crear_plato, crear_postre, crear_menu, crear_combo, persistir
):
    plato, postre = crear_plato(), crear_postre()
    menu = _de_baja(crear_menu(plato, postre))
    combo = crear_combo(desde=date(2026, 5, 1), hasta=date(2026, 5, 31), platos=[plato])
    plato_id, *_ = persistir(plato, postre, menu, combo)

    respuesta = cliente.delete(f"/productos/platos/{plato_id}")

    assert respuesta.status_code == 204
    assert cliente.get(f"/productos/platos/{plato_id}").json()["dado_de_baja"] is True


def test_ld_15_combo_vencido_pero_activo_no_bloquea_y_responde_204(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    combo = crear_combo(desde=date(2026, 5, 1), hasta=date(2026, 6, 14), platos=[plato])
    plato_id, _ = persistir(plato, combo)

    respuesta = cliente.delete(f"/productos/platos/{plato_id}")

    assert respuesta.status_code == 204
    assert cliente.get(f"/productos/platos/{plato_id}").json()["dado_de_baja"] is True


def test_ld_21_reactivar_con_nombre_en_conflicto_responde_409(cliente, crear_plato, persistir):
    baja_id, _ = persistir(_de_baja(crear_plato(nombre="Milanesa")), crear_plato(nombre="Milanesa"))

    respuesta = cliente.put(
        f"/productos/platos/{baja_id}", json={**CUERPO_PLATO, "dado_de_baja": False}
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"/productos/platos/{baja_id}").json()["dado_de_baja"] is True


def test_ld_22_reactivar_bebida_con_nombre_unico_responde_200_y_queda_activa(
    cliente, crear_bebida, persistir
):
    bebida_id = persistir(_de_baja(crear_bebida(nombre="Cerveza")))

    respuesta = cliente.put(
        f"/productos/bebidas/{bebida_id}", json={**CUERPO_BEBIDA, "dado_de_baja": False}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is False
