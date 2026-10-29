import pytest

PREFIJO = "/productos/menus-ejecutivos"


@pytest.fixture
def componentes(crear_plato, crear_postre, persistir):
    """Plato y Postre activos ya guardados: (plato_id, postre_id)."""
    return persistir(crear_plato(nombre="Milanesa"), crear_postre(nombre="Flan"))


def _cuerpo(plato_id, postre_id, **cambios):
    return {
        "nombre": "Menú del día",
        "precio": "2000.00",
        "plato_id": plato_id,
        "postre_id": postre_id,
        **cambios,
    }


def _crear_menu(cliente, plato_id, postre_id, **cambios):
    respuesta = cliente.post(PREFIJO, json=_cuerpo(plato_id, postre_id, **cambios))
    assert respuesta.status_code == 201
    return respuesta.json()


def test_cat_30_menu_valido_responde_201_con_los_componentes(cliente, componentes):
    plato_id, postre_id = componentes

    respuesta = cliente.post(PREFIJO, json=_cuerpo(plato_id, postre_id))

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert isinstance(cuerpo["id"], int)
    assert cuerpo["tipo"] == "menu_ejecutivo"
    assert cuerpo["plato_id"] == plato_id
    assert cuerpo["postre_id"] == postre_id
    assert cuerpo["precio"] == "2000.00"
    assert cuerpo["dado_de_baja"] is False


def test_obtener_menu_por_id_devuelve_el_menu(cliente, componentes):
    creado = _crear_menu(cliente, *componentes)

    respuesta = cliente.get(f"{PREFIJO}/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_cat_08_get_de_menu_con_id_de_un_plato_responde_404(cliente, componentes):
    plato_id, _ = componentes

    assert cliente.get(f"{PREFIJO}/{plato_id}").status_code == 404


def test_cat_31_plato_id_de_una_bebida_responde_422_sobre_plato_id(
    cliente, crear_bebida, crear_postre, persistir
):
    bebida_id, postre_id = persistir(crear_bebida(), crear_postre())

    respuesta = cliente.post(PREFIJO, json=_cuerpo(bebida_id, postre_id))

    assert respuesta.status_code == 422
    error = respuesta.json()["detail"][0]
    assert error["loc"] == ["body", "plato_id"]
    assert error["ids"] == [bebida_id]


def test_cat_32_postre_id_inexistente_responde_422_sobre_postre_id(cliente, componentes):
    plato_id, _ = componentes

    respuesta = cliente.post(PREFIJO, json=_cuerpo(plato_id, 999))

    assert respuesta.status_code == 422
    error = respuesta.json()["detail"][0]
    assert error["loc"] == ["body", "postre_id"]
    assert error["ids"] == [999]


def test_cat_33_plato_inactivo_responde_409_con_su_id(cliente, crear_plato, crear_postre, persistir):
    plato = crear_plato()
    plato.dado_de_baja = True
    plato_id, postre_id = persistir(plato, crear_postre())

    respuesta = cliente.post(PREFIJO, json=_cuerpo(plato_id, postre_id))

    assert respuesta.status_code == 409
    assert respuesta.json()["ids"] == [plato_id]


def test_cat_41_cambiar_el_precio_de_un_plato_no_altera_el_del_menu(cliente, componentes):
    plato_id, postre_id = componentes
    menu = _crear_menu(cliente, plato_id, postre_id, precio="1000.00")

    cambio = cliente.put(
        f"/productos/platos/{plato_id}",
        json={"nombre": "Milanesa", "precio": "900.00", "cant_personas": 2},
    )

    assert cambio.status_code == 200
    assert cliente.get(f"{PREFIJO}/{menu['id']}").json()["precio"] == "1000.00"


def test_cat_42_put_de_menu_activo_con_postre_inactivo_responde_409_y_no_cambia(
    cliente, crear_postre, componentes, persistir
):
    plato_id, postre_id = componentes
    menu = _crear_menu(cliente, plato_id, postre_id)
    postre_baja = crear_postre(nombre="Helado")
    postre_baja.dado_de_baja = True
    postre_baja_id = persistir(postre_baja)

    respuesta = cliente.put(
        f"{PREFIJO}/{menu['id']}", json=_cuerpo(plato_id, postre_baja_id, descripcion="Nueva")
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["ids"] == [postre_baja_id]
    assert cliente.get(f"{PREFIJO}/{menu['id']}").json() == menu


@pytest.mark.parametrize(
    "estado", [{"dado_de_baja": True}, {}], ids=["con_dado_de_baja_true", "sin_el_campo"]
)
def test_cat_43_editar_menu_de_baja_con_plato_inactivo_manteniendolo_de_baja_responde_200(
    cliente, sesion, crear_plato, crear_postre, crear_menu, persistir, estado
):
    plato, postre = crear_plato(), crear_postre()
    plato.dado_de_baja = True
    menu = crear_menu(plato, postre)
    menu.dado_de_baja = True
    plato_id, postre_id, menu_id = persistir(plato, postre, menu)

    respuesta = cliente.put(
        f"{PREFIJO}/{menu_id}", json=_cuerpo(plato_id, postre_id, descripcion="Nueva", **estado)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert respuesta.json()["descripcion"] == "Nueva"


def test_cat_44_postre_inexistente_en_menu_de_baja_responde_422(
    cliente, crear_plato, crear_postre, crear_menu, persistir
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    menu.dado_de_baja = True
    plato_id, _, menu_id = persistir(plato, postre, menu)

    respuesta = cliente.put(
        f"{PREFIJO}/{menu_id}", json=_cuerpo(plato_id, 999, dado_de_baja=True)
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["loc"] == ["body", "postre_id"]


def test_cat_14_put_de_menu_desconocido_prioriza_422_y_luego_404_sobre_componentes(
    cliente, componentes
):
    plato_id, postre_id = componentes

    assert cliente.put(f"{PREFIJO}/999", json=_cuerpo(plato_id, postre_id, precio="0")).status_code == 422
    # Con el cuerpo válido el menú inexistente (404) gana a los componentes inexistentes (422)
    assert cliente.put(f"{PREFIJO}/999", json=_cuerpo(998, 999)).status_code == 404


def test_ld_16_delete_de_menu_responde_204_y_los_componentes_no_cambian(cliente, componentes):
    plato_id, postre_id = componentes
    menu = _crear_menu(cliente, plato_id, postre_id)

    respuesta = cliente.delete(f"{PREFIJO}/{menu['id']}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert cliente.get(f"{PREFIJO}/{menu['id']}").json()["dado_de_baja"] is True
    assert cliente.get(f"/productos/platos/{plato_id}").json()["dado_de_baja"] is False
    assert cliente.get(f"/productos/postres/{postre_id}").json()["dado_de_baja"] is False


def test_delete_de_menu_desconocido_responde_404(cliente):
    assert cliente.delete(f"{PREFIJO}/999").status_code == 404


def test_ld_19_reactivar_menu_con_plato_inactivo_responde_409_y_sigue_de_baja(
    cliente, crear_plato, crear_postre, crear_menu, persistir
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    menu.dado_de_baja = True
    plato_id, postre_id, menu_id = persistir(plato, postre, menu)
    # El plato se da de baja después, ya sin menú activo que lo bloquee
    assert cliente.delete(f"/productos/platos/{plato_id}").status_code == 204

    respuesta = cliente.put(
        f"{PREFIJO}/{menu_id}", json=_cuerpo(plato_id, postre_id, dado_de_baja=False)
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["ids"] == [plato_id]
    assert cliente.get(f"{PREFIJO}/{menu_id}").json()["dado_de_baja"] is True


def test_ld_20_reactivar_menu_con_componentes_activos_responde_200(
    cliente, crear_plato, crear_postre, crear_menu, persistir
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    menu.dado_de_baja = True
    plato_id, postre_id, menu_id = persistir(plato, postre, menu)

    respuesta = cliente.put(
        f"{PREFIJO}/{menu_id}", json=_cuerpo(plato_id, postre_id, dado_de_baja=False)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is False


def test_cat_s_04_crear_menu_con_seccion(cliente, componentes, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion())

    respuesta = cliente.post(PREFIJO, json=_cuerpo(*componentes, seccion_id=seccion_id))

    assert respuesta.status_code == 201
    assert respuesta.json()["seccion_id"] == seccion_id


def test_cat_s_05_crear_menu_con_seccion_inexistente_responde_422(cliente, componentes):
    respuesta = cliente.post(PREFIJO, json=_cuerpo(*componentes, seccion_id=999))

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["loc"] == ["body", "seccion_id"]
    assert respuesta.json()["detail"][0]["type"] == "seccion_inexistente"


def test_cat_s_09_put_de_menu_acepta_seccion_existente_y_rechaza_inexistente(
    cliente, componentes, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion())
    menu = _crear_menu(cliente, *componentes)

    valido = cliente.put(
        f"{PREFIJO}/{menu['id']}", json=_cuerpo(*componentes, seccion_id=seccion_id)
    )
    invalido = cliente.put(f"{PREFIJO}/{menu['id']}", json=_cuerpo(*componentes, seccion_id=999))

    assert valido.status_code == 200
    assert valido.json()["seccion_id"] == seccion_id
    assert invalido.status_code == 422
    assert cliente.get(f"{PREFIJO}/{menu['id']}").json()["seccion_id"] == seccion_id


def test_cat_s_17_la_seccion_inexistente_tiene_prioridad_sobre_el_componente_inactivo(
    cliente, crear_plato, crear_postre, crear_menu, persistir
):
    plato, postre = crear_plato(), crear_postre()
    postre.dado_de_baja = True
    plato_id, postre_id, menu_id = persistir(plato, postre, crear_menu(plato, postre))

    respuesta = cliente.put(
        f"{PREFIJO}/{menu_id}", json=_cuerpo(plato_id, postre_id, seccion_id=999)
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "seccion_inexistente"


def test_cat_s_19_el_componente_inactivo_tiene_prioridad_sobre_el_nombre_duplicado(
    cliente, crear_plato, crear_postre, crear_menu, persistir
):
    plato, postre = crear_plato(), crear_postre()
    postre.dado_de_baja = True
    plato_id, postre_id, menu_id = persistir(
        plato, postre, crear_menu(plato, postre, nombre="Menú A")
    )
    persistir(crear_plato(nombre="Menú B"))

    respuesta = cliente.put(
        f"{PREFIJO}/{menu_id}", json=_cuerpo(plato_id, postre_id, nombre="Menú B")
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["ids"] == [postre_id]
