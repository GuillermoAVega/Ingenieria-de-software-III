import pytest
from sqlalchemy import func, select

from src.productos.models import Producto

# Cuerpos válidos por prefijo, para las validaciones comunes a los tres subtipos simples
CUERPOS_SIMPLES = {
    "/productos/platos": {"nombre": "Milanesa", "precio": "1500.00", "cant_personas": 2},
    "/productos/bebidas": {"nombre": "Milanesa", "precio": "1500.00", "es_alcoholica": False},
    "/productos/postres": {"nombre": "Milanesa", "precio": "1500.00"},
}
PREFIJOS = list(CUERPOS_SIMPLES)


def _cuerpo(prefijo, **cambios):
    return {**CUERPOS_SIMPLES[prefijo], **cambios}


def _cuerpo_plato(**cambios):
    return _cuerpo("/productos/platos", **cambios)


def test_cat_07_crear_plato_responde_201_con_id(cliente):
    respuesta = cliente.post("/productos/platos", json=_cuerpo_plato(descripcion="Con papas"))

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert isinstance(cuerpo["id"], int)
    assert cuerpo["tipo"] == "plato"
    assert cuerpo["nombre"] == "Milanesa"
    assert cuerpo["precio"] == "1500.00"
    assert cuerpo["cant_personas"] == 2
    assert cuerpo["descripcion"] == "Con papas"
    assert cuerpo["dado_de_baja"] is False


def test_obtener_plato_por_id_devuelve_el_plato(cliente):
    creado = cliente.post("/productos/platos", json=_cuerpo_plato()).json()

    respuesta = cliente.get(f"/productos/platos/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_cat_08_get_de_plato_con_id_de_una_bebida_responde_404(cliente):
    bebida = cliente.post("/productos/bebidas", json=_cuerpo("/productos/bebidas")).json()

    respuesta = cliente.get(f"/productos/platos/{bebida['id']}")

    assert respuesta.status_code == 404


def test_cat_11_put_de_plato_desconocido_responde_404(cliente):
    respuesta = cliente.put("/productos/platos/999", json=_cuerpo_plato())

    assert respuesta.status_code == 404


def test_cat_12_put_sin_dado_de_baja_conserva_el_estado(cliente, crear_plato, persistir):
    plato_id = persistir(crear_plato(dado_de_baja=True))

    respuesta = cliente.put(
        f"/productos/platos/{plato_id}", json=_cuerpo_plato(descripcion="Nueva")
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert respuesta.json()["descripcion"] == "Nueva"


def test_cat_13_put_es_reemplazo_completo(cliente):
    creado = cliente.post(
        "/productos/platos", json=_cuerpo_plato(descripcion="Con papas", imagen="m.png")
    ).json()

    respuesta = cliente.put(f"/productos/platos/{creado['id']}", json=_cuerpo_plato())

    assert respuesta.status_code == 200
    assert respuesta.json()["descripcion"] is None
    assert respuesta.json()["imagen"] is None


def test_cat_14_precio_invalido_en_put_a_id_desconocido_responde_422_antes_que_404(cliente):
    respuesta = cliente.put("/productos/platos/999", json=_cuerpo_plato(precio="0"))

    assert respuesta.status_code == 422


@pytest.mark.parametrize("prefijo", PREFIJOS)
@pytest.mark.parametrize(
    "nombre", ["", "   "], ids=["cat_15_vacio", "cat_16_solo_espacios"]
)
def test_cat_15_16_nombre_vacio_o_de_espacios_responde_422(cliente, prefijo, nombre):
    respuesta = cliente.post(prefijo, json=_cuerpo(prefijo, nombre=nombre))

    assert respuesta.status_code == 422


@pytest.mark.parametrize("prefijo", PREFIJOS)
def test_cat_17_nombre_se_recorta_antes_de_almacenarse(cliente, prefijo):
    respuesta = cliente.post(prefijo, json=_cuerpo(prefijo, nombre="  Milanesa "))

    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Milanesa"


@pytest.mark.parametrize("prefijo", PREFIJOS)
def test_cat_18_nombre_de_101_caracteres_responde_422(cliente, prefijo):
    assert cliente.post(prefijo, json=_cuerpo(prefijo, nombre="a" * 101)).status_code == 422
    assert cliente.post(prefijo, json=_cuerpo(prefijo, nombre="a" * 100)).status_code == 201


@pytest.mark.parametrize("prefijo", PREFIJOS)
@pytest.mark.parametrize("precio", ["0", "-5.00"], ids=["cero", "negativo"])
def test_cat_19_precio_no_positivo_responde_422(cliente, prefijo, precio):
    respuesta = cliente.post(prefijo, json=_cuerpo(prefijo, precio=precio))

    assert respuesta.status_code == 422


@pytest.mark.parametrize("prefijo", PREFIJOS)
def test_cat_20_descripcion_de_501_caracteres_responde_422(cliente, prefijo):
    assert cliente.post(prefijo, json=_cuerpo(prefijo, descripcion="d" * 501)).status_code == 422
    assert cliente.post(prefijo, json=_cuerpo(prefijo, descripcion="d" * 500)).status_code == 201


@pytest.mark.parametrize(
    "nombre",
    ["Milanesa", "milanesa", "  Milanesa "],
    ids=["cat_21_exacto", "cat_22_mayusculas", "cat_23_espacios"],
)
@pytest.mark.parametrize("prefijo", PREFIJOS)
def test_cat_21_22_23_nombre_activo_duplicado_responde_409(
    cliente, sesion, crear_plato, prefijo, nombre
):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()

    respuesta = cliente.post(prefijo, json=_cuerpo(prefijo, nombre=nombre))

    assert respuesta.status_code == 409
    assert sesion.scalar(select(func.count()).select_from(Producto)) == 1


@pytest.mark.parametrize("prefijo", PREFIJOS)
def test_cat_24_las_tildes_distinguen_nombres(cliente, sesion, crear_plato, prefijo):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()

    respuesta = cliente.post(prefijo, json=_cuerpo(prefijo, nombre="Milanésa"))

    assert respuesta.status_code == 201


@pytest.mark.parametrize("prefijo", PREFIJOS)
def test_cat_25_el_nombre_de_un_producto_dado_de_baja_se_puede_reutilizar(
    cliente, sesion, crear_plato, prefijo
):
    sesion.add(crear_plato(nombre="Milanesa", dado_de_baja=True))
    sesion.commit()

    respuesta = cliente.post(prefijo, json=_cuerpo(prefijo))

    assert respuesta.status_code == 201


def test_cat_26_put_con_el_mismo_nombre_responde_200(cliente):
    creado = cliente.post("/productos/platos", json=_cuerpo_plato()).json()

    respuesta = cliente.put(
        f"/productos/platos/{creado['id']}", json=_cuerpo_plato(descripcion="Nueva")
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["descripcion"] == "Nueva"


def test_put_con_el_nombre_de_otro_producto_activo_responde_409(cliente):
    cliente.post("/productos/platos", json=_cuerpo_plato(nombre="Pizza"))
    milanesa = cliente.post("/productos/platos", json=_cuerpo_plato()).json()

    respuesta = cliente.put(
        f"/productos/platos/{milanesa['id']}", json=_cuerpo_plato(nombre="pizza")
    )

    assert respuesta.status_code == 409


def test_cat_28_cant_personas_invalido_responde_422(cliente):
    assert cliente.post("/productos/platos", json=_cuerpo_plato(cant_personas=0)).status_code == 422
    sin_cantidad = {"nombre": "Milanesa", "precio": "1500.00"}
    assert cliente.post("/productos/platos", json=sin_cantidad).status_code == 422
