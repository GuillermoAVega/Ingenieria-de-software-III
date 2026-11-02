import pytest

from src.productos import services
from src.productos.bebidas import services as servicios_bebidas
from src.productos.bebidas.models import Bebida
from src.productos.platos import services as servicios_platos
from src.productos.platos.models import Plato
from src.productos.postres import services as servicios_postres
from src.productos.postres.models import Postre

CUERPOS = {
    "/productos/platos": {"nombre": "Milanesa", "precio": "1500.00", "cant_personas": 2},
    "/productos/bebidas": {"nombre": "Cerveza", "precio": "800.00", "es_alcoholica": True},
    "/productos/postres": {"nombre": "Flan", "precio": "600.00"},
}

SERVICIOS = {
    "/productos/platos": (servicios_platos.listar_platos, Plato),
    "/productos/bebidas": (servicios_bebidas.listar_bebidas, Bebida),
    "/productos/postres": (servicios_postres.listar_postres, Postre),
}


@pytest.mark.parametrize("prefijo", list(CUERPOS))
def test_listado_vacio_devuelve_una_lista_vacia(cliente, prefijo):
    respuesta = cliente.get(prefijo)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


@pytest.mark.parametrize("prefijo", list(CUERPOS))
def test_listado_devuelve_los_productos_activos_ordenados_por_id(cliente, prefijo):
    primero = cliente.post(prefijo, json={**CUERPOS[prefijo], "nombre": "Primero"})
    segundo = cliente.post(prefijo, json={**CUERPOS[prefijo], "nombre": "Segundo"})
    dado_de_baja = cliente.post(prefijo, json={**CUERPOS[prefijo], "nombre": "Baja"})
    assert primero.status_code == 201
    assert segundo.status_code == 201
    assert dado_de_baja.status_code == 201
    assert cliente.delete(f"{prefijo}/{dado_de_baja.json()['id']}").status_code == 204

    respuesta = cliente.get(prefijo)

    assert respuesta.status_code == 200
    assert [producto["id"] for producto in respuesta.json()] == [
        primero.json()["id"],
        segundo.json()["id"],
    ]


@pytest.mark.parametrize("prefijo", list(CUERPOS))
def test_listado_no_mezcla_subtipos(cliente, prefijo):
    otro = next(candidato for candidato in CUERPOS if candidato != prefijo)
    ajeno = cliente.post(otro, json=CUERPOS[otro])
    assert ajeno.status_code == 201

    respuesta = cliente.get(prefijo)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


@pytest.mark.parametrize("prefijo", list(CUERPOS))
def test_servicio_listar_excluye_las_bajas_y_ordena_por_id(
    sesion, crear_plato, crear_bebida, crear_postre, persistir, prefijo
):
    construir = {
        "/productos/platos": crear_plato,
        "/productos/bebidas": crear_bebida,
        "/productos/postres": crear_postre,
    }[prefijo]
    listar, _modelo = SERVICIOS[prefijo]
    primero = construir(nombre="Primero")
    baja = construir(nombre="Baja")
    baja.dado_de_baja = True
    segundo = construir(nombre="Segundo")
    ids = persistir(primero, baja, segundo)

    productos = listar(sesion)

    assert [producto.id for producto in productos] == [ids[0], ids[2]]


@pytest.mark.parametrize("prefijo", list(CUERPOS))
def test_servicio_listar_sin_filas_devuelve_lista_vacia(sesion, prefijo):
    listar, _modelo = SERVICIOS[prefijo]

    assert listar(sesion) == []


def test_servicio_listar_generico_filtra_por_modelo(sesion, crear_plato, crear_bebida, persistir):
    plato = crear_plato()
    bebida = crear_bebida()
    plato_id, bebida_id = persistir(plato, bebida)

    assert [producto.id for producto in services.listar(sesion, Plato)] == [plato_id]
    assert [producto.id for producto in services.listar(sesion, Bebida)] == [bebida_id]
