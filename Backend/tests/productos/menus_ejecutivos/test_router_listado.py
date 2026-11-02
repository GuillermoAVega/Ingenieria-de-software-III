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


def test_cat_s_29_listado_vacio_devuelve_lista_vacia(cliente):
    respuesta = cliente.get(PREFIJO)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_cat_s_30_listado_devuelve_solo_menus_activos(
    cliente, componentes, crear_plato, crear_postre, crear_menu, persistir
):
    activo = cliente.post(PREFIJO, json=_cuerpo(*componentes)).json()
    plato, postre = crear_plato(nombre="Suprema"), crear_postre(nombre="Helado")
    de_baja = crear_menu(plato, postre, nombre="Menú retirado")
    de_baja.dado_de_baja = True
    persistir(plato, postre, de_baja)

    respuesta = cliente.get(PREFIJO)

    assert respuesta.status_code == 200
    assert [item["id"] for item in respuesta.json()] == [activo["id"]]


def test_cat_s_31_listado_ordenado_por_id_ascendente(cliente, componentes):
    primero = cliente.post(PREFIJO, json=_cuerpo(*componentes)).json()
    segundo = cliente.post(
        PREFIJO, json=_cuerpo(*componentes, nombre="Menú ejecutivo 2")
    ).json()

    respuesta = cliente.get(PREFIJO)

    assert respuesta.status_code == 200
    assert [item["id"] for item in respuesta.json()] == [primero["id"], segundo["id"]]


def test_cat_s_32_el_listado_no_mezcla_otros_subtipos(cliente, componentes):
    plato_id, postre_id = componentes
    cliente.post(PREFIJO, json=_cuerpo(plato_id, postre_id))

    respuesta = cliente.get(PREFIJO)

    assert respuesta.status_code == 200
    assert {item["tipo"] for item in respuesta.json()} == {"menu_ejecutivo"}
    assert {item["id"] for item in respuesta.json()} != {plato_id, postre_id}
