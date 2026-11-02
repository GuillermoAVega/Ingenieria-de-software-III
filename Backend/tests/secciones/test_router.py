import itertools
from datetime import date
from decimal import Decimal

import pytest

from src.productos.bebidas.models import Bebida
from src.productos.combos.models import ComboPromocion
from src.productos.menus_ejecutivos.models import MenuEjecutivo
from src.productos.platos.models import Plato
from src.productos.postres.models import Postre

RUTA = "/secciones"

# Posiciones autoasignadas desde 1001 para no chocar con las explícitas de las pruebas
_posiciones = itertools.count(1001)


def _crear(cliente, **cuerpo):
    return cliente.post(
        RUTA, json={"nombre": "Entradas", "posicion": next(_posiciones), **cuerpo}
    )


def _crear_plato(cliente, seccion_id=None):
    respuesta = cliente.post(
        "/productos/platos",
        json={
            "nombre": "Milanesa",
            "precio": "1500.00",
            "cant_personas": 2,
            "seccion_id": seccion_id,
        },
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_postre(cliente, seccion_id=None):
    respuesta = cliente.post(
        "/productos/postres",
        json={"nombre": "Flan", "precio": "600.00", "seccion_id": seccion_id},
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def test_sec_02_la_respuesta_incluye_productos_ids_y_no_el_estado_de_baja(cliente):
    seccion = _crear(cliente, subtitulo="Para comenzar").json()
    plato = cliente.post(
        "/productos/platos",
        json={
            "nombre": "Milanesa",
            "precio": "1500.00",
            "cant_personas": 2,
            "seccion_id": seccion["id"],
        },
    )
    assert plato.status_code == 201

    respuesta = cliente.get(f"{RUTA}/{seccion['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": seccion["id"],
        "nombre": "Entradas",
        "subtitulo": "Para comenzar",
        "posicion": seccion["posicion"],
        "productos_ids": [plato.json()["id"]],
    }
    assert "dado_de_baja" not in respuesta.json()


@pytest.mark.parametrize("nombre", ["", "   "])
def test_sec_03_04_nombre_vacio_o_de_espacios_responde_422(cliente, nombre):
    respuesta = _crear(cliente, nombre=nombre)

    assert respuesta.status_code == 422


def test_sec_03_nombre_vacio_no_crea_ninguna_seccion(cliente):
    _crear(cliente, nombre="")

    assert cliente.get(f"{RUTA}/1").status_code == 404


def test_sec_05_nombre_ausente_responde_422(cliente):
    assert cliente.post(RUTA, json={"subtitulo": "x"}).status_code == 422


def test_sec_06_el_nombre_se_recorta_antes_de_almacenarse(cliente):
    respuesta = _crear(cliente, nombre="  Entradas ")

    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Entradas"


def test_sec_07_nombre_de_100_caracteres_responde_201(cliente):
    assert _crear(cliente, nombre="a" * 100).status_code == 201


def test_sec_08_nombre_de_101_caracteres_responde_422(cliente):
    assert _crear(cliente, nombre="a" * 101).status_code == 422


def test_sec_09_subtitulo_de_200_caracteres_responde_201(cliente):
    assert _crear(cliente, subtitulo="a" * 200).status_code == 201


def test_sec_10_subtitulo_de_201_caracteres_responde_422(cliente):
    assert _crear(cliente, subtitulo="a" * 201).status_code == 422


def test_sec_39_el_subtitulo_se_recorta_antes_de_almacenarse(cliente):
    respuesta = _crear(cliente, subtitulo="  Para comenzar ")

    assert respuesta.status_code == 201
    assert respuesta.json()["subtitulo"] == "Para comenzar"


@pytest.mark.parametrize("subtitulo", ["", "   "])
def test_sec_40_41_subtitulo_vacio_o_de_espacios_se_almacena_como_null(cliente, subtitulo):
    respuesta = _crear(cliente, subtitulo=subtitulo)

    assert respuesta.status_code == 201
    assert respuesta.json()["subtitulo"] is None
    assert cliente.get(f"{RUTA}/{respuesta.json()['id']}").json()["subtitulo"] is None


def test_sec_42_el_limite_del_subtitulo_se_verifica_tras_el_recorte(cliente):
    respuesta = _crear(cliente, subtitulo=f"  {'a' * 200}  ")

    assert respuesta.status_code == 201
    assert len(respuesta.json()["subtitulo"]) == 200


def test_sec_43_subtitulo_de_201_caracteres_rodeado_de_espacios_responde_422(cliente):
    assert _crear(cliente, subtitulo=f"  {'a' * 201}  ").status_code == 422


@pytest.mark.parametrize(
    "nombre_repetido",
    [
        pytest.param("Entradas", id="sec_11_exacto"),
        pytest.param("entradas", id="test_sec_12_mayusculas"),
        pytest.param("  Entradas ", id="test_sec_13_espacios"),
    ],
)
def test_sec_11_12_13_nombre_duplicado_en_el_alta_responde_409(cliente, nombre_repetido):
    primera = _crear(cliente)

    respuesta = _crear(cliente, nombre=nombre_repetido)

    assert respuesta.status_code == 409
    assert "detail" in respuesta.json()
    # No se creó ninguna sección nueva
    assert cliente.get(f"{RUTA}/{primera.json()['id'] + 1}").status_code == 404


def test_sec_14_las_tildes_distinguen_nombres(cliente):
    _crear(cliente)

    assert _crear(cliente, nombre="Entrádas").status_code == 201


def test_sec_19_crear_seccion_con_todos_los_campos(cliente):
    respuesta = _crear(cliente, subtitulo="Para comenzar")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert isinstance(cuerpo["id"], int)
    assert cuerpo["nombre"] == "Entradas"
    assert cuerpo["subtitulo"] == "Para comenzar"


def test_sec_20_crear_seccion_sin_subtitulo(cliente):
    respuesta = _crear(cliente)

    assert respuesta.status_code == 201
    assert respuesta.json()["subtitulo"] is None


def test_sec_21_el_422_tiene_prioridad_sobre_el_409_en_el_alta(cliente):
    _crear(cliente)

    assert _crear(cliente, subtitulo="a" * 201).status_code == 422


def test_sec_22_obtener_una_seccion_existente(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()

    respuesta = cliente.get(f"{RUTA}/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_sec_22_obtener_una_seccion_existente_incluye_productos_ids(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()
    plato = _crear_plato(cliente, creada["id"])

    respuesta = cliente.get(f"{RUTA}/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": creada["id"],
        "nombre": "Entradas",
        "subtitulo": "Para comenzar",
        "posicion": creada["posicion"],
        "productos_ids": [plato["id"]],
    }


def test_ids_01_productos_ids_es_lista_de_enteros(cliente):
    seccion = _crear(cliente).json()
    _crear_plato(cliente, seccion["id"])
    _crear_postre(cliente, seccion["id"])

    cuerpo = cliente.get(f"{RUTA}/{seccion['id']}").json()

    assert len(cuerpo["productos_ids"]) == 2
    assert all(type(id_) is int for id_ in cuerpo["productos_ids"])
    assert set(cuerpo) == {"id", "nombre", "subtitulo", "posicion", "productos_ids"}
    for clave in ("precio", "dado_de_baja"):
        assert clave not in cuerpo


def test_ids_02_el_alta_devuelve_productos_ids_vacio(cliente):
    respuesta = _crear(cliente)

    assert respuesta.status_code == 201
    assert respuesta.json()["productos_ids"] == []


def test_ids_03_la_consulta_devuelve_los_ids_de_los_productos_activos(cliente):
    seccion = _crear(cliente).json()
    plato = _crear_plato(cliente, seccion["id"])

    respuesta = cliente.get(f"{RUTA}/{seccion['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json()["productos_ids"] == [plato["id"]]


def test_sec_23_obtener_una_seccion_inexistente_responde_404(cliente):
    respuesta = cliente.get(f"{RUTA}/999")

    assert respuesta.status_code == 404
    assert "detail" in respuesta.json()


def test_sec_24_el_listado_devuelve_las_secciones_ordenadas_por_posicion(cliente):
    segunda = cliente.post(RUTA, json={"nombre": "Postres", "posicion": 2})
    primera = cliente.post(RUTA, json={"nombre": "Entradas", "posicion": 1})
    assert segunda.status_code == 201
    assert primera.status_code == 201

    respuesta = cliente.get(RUTA)

    assert respuesta.status_code == 200
    assert [seccion["id"] for seccion in respuesta.json()] == [
        primera.json()["id"],
        segunda.json()["id"],
    ]
    for seccion in respuesta.json():
        assert set(seccion) == {"id", "nombre", "subtitulo", "posicion", "productos_ids"}


def test_sec_24_el_listado_vacio_devuelve_una_lista_vacia(cliente):
    respuesta = cliente.get(RUTA)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_sec_24_el_listado_incluye_los_productos_ids_de_cada_seccion(cliente):
    seccion = _crear(cliente).json()
    plato = _crear_plato(cliente, seccion["id"])

    respuesta = cliente.get(RUTA)

    assert respuesta.status_code == 200
    assert respuesta.json()[0]["productos_ids"] == [plato["id"]]


def test_la_ruta_por_id_exige_un_entero(cliente):
    assert cliente.get(f"{RUTA}/abc").status_code == 404
    assert cliente.put(f"{RUTA}/abc", json={"nombre": "x"}).status_code == 404
    assert cliente.delete(f"{RUTA}/abc").status_code == 404


def test_sec_25_modificar_una_seccion(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}",
        json={"nombre": "Aperitivos", "subtitulo": "Para compartir", "posicion": 1},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": creada["id"],
        "nombre": "Aperitivos",
        "subtitulo": "Para compartir",
        "posicion": 1,
        "productos_ids": [],
    }
    assert cliente.get(f"{RUTA}/{creada['id']}").json() == respuesta.json()


def test_sec_26_el_put_es_un_reemplazo_completo(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}", json={"nombre": "Entradas", "posicion": 1}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["subtitulo"] is None


def test_sec_27_actualizar_una_seccion_inexistente_responde_404(cliente):
    assert cliente.put(
        f"{RUTA}/999", json={"nombre": "Entradas", "posicion": 1}
    ).status_code == 404


def test_sec_28_el_422_tiene_prioridad_sobre_el_404_en_la_modificacion(cliente):
    assert cliente.put(f"{RUTA}/999", json={"nombre": ""}).status_code == 422


def test_sec_29_el_404_tiene_prioridad_sobre_el_409_en_la_modificacion(cliente):
    _crear(cliente)

    assert cliente.put(
        f"{RUTA}/999", json={"nombre": "Entradas", "posicion": 1}
    ).status_code == 404


def test_sec_15_nombre_duplicado_en_la_modificacion_responde_409_sin_cambios(cliente):
    _crear(cliente, nombre="Entradas")
    postres = _crear(cliente, nombre="Postres", subtitulo="Dulces").json()

    respuesta = cliente.put(
        f"{RUTA}/{postres['id']}", json={"nombre": "entradas", "posicion": 1}
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"{RUTA}/{postres['id']}").json() == postres


def test_sec_16_la_modificacion_conserva_el_propio_nombre(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}",
        json={"nombre": "Entradas", "subtitulo": "Nuevo", "posicion": 1},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["subtitulo"] == "Nuevo"


def test_sec_17_la_modificacion_puede_cambiar_solo_las_mayusculas(cliente):
    creada = _crear(cliente).json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}", json={"nombre": "ENTRADAS", "posicion": 1}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "ENTRADAS"


def test_sec_44_el_put_recorta_y_normaliza_el_subtitulo(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}",
        json={"nombre": "Entradas", "subtitulo": "   ", "posicion": 1},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["subtitulo"] is None


# --- Validación de posicion (422) ---


def test_pos_02_posicion_ausente_en_el_alta_responde_422_sin_crear(cliente):
    respuesta = cliente.post(RUTA, json={"nombre": "Entradas"})

    assert respuesta.status_code == 422
    assert cliente.get(f"{RUTA}/1").status_code == 404


def test_pos_03_posicion_ausente_en_la_modificacion_responde_422(cliente):
    creada = _crear(cliente, posicion=1).json()

    respuesta = cliente.put(f"{RUTA}/{creada['id']}", json={"nombre": "Entradas"})

    assert respuesta.status_code == 422


@pytest.mark.parametrize(
    "posicion",
    [
        pytest.param(0, id="pos_04_cero"),
        pytest.param(-1, id="pos_05_negativa"),
        pytest.param("abc", id="pos_07_texto"),
        pytest.param(1.5, id="pos_08_decimal"),
    ],
)
def test_pos_04_05_07_08_posicion_invalida_en_el_alta_responde_422_sin_crear(
    cliente, posicion
):
    respuesta = _crear(cliente, posicion=posicion)

    assert respuesta.status_code == 422
    assert cliente.get(f"{RUTA}/1").status_code == 404


def test_pos_06_posicion_cero_en_la_modificacion_responde_422(cliente):
    creada = _crear(cliente, posicion=1).json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}", json={"nombre": "Entradas", "posicion": 0}
    )

    assert respuesta.status_code == 422


def test_pos_10_una_modificacion_rechazada_por_validacion_no_cambia_la_seccion(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar", posicion=1).json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}",
        json={"nombre": "Aperitivos", "subtitulo": "Para compartir", "posicion": -3},
    )

    assert respuesta.status_code == 422
    conservada = cliente.get(f"{RUTA}/{creada['id']}").json()
    assert conservada["nombre"] == "Entradas"
    assert conservada["subtitulo"] == "Para comenzar"
    assert conservada["posicion"] == 1


def test_sec_31_borrar_una_seccion_responde_204_sin_cuerpo(cliente):
    creada = _crear(cliente).json()

    respuesta = cliente.delete(f"{RUTA}/{creada['id']}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert cliente.get(f"{RUTA}/{creada['id']}").status_code == 404


def test_sec_32_borrar_una_seccion_inexistente_responde_404(cliente):
    assert cliente.delete(f"{RUTA}/999").status_code == 404


def test_sec_33_el_borrado_repetido_responde_404(cliente):
    creada = _crear(cliente).json()
    cliente.delete(f"{RUTA}/{creada['id']}")

    assert cliente.delete(f"{RUTA}/{creada['id']}").status_code == 404


def test_sec_18_el_nombre_se_puede_reutilizar_tras_el_borrado(cliente):
    creada = _crear(cliente).json()
    cliente.delete(f"{RUTA}/{creada['id']}")

    assert _crear(cliente).status_code == 201


# --- Desvinculación de productos al borrar una sección (HTTP) ---

RUTAS_PRODUCTO = {
    "plato": "/productos/platos",
    "bebida": "/productos/bebidas",
    "postre": "/productos/postres",
    "menu": "/productos/menus-ejecutivos",
    "combo": "/productos/combos",
}


def _plato(nombre="Milanesa", **extra):
    return Plato(nombre=nombre, nombre_normalizado=nombre.casefold(),
                 precio=Decimal("1500.00"), cant_personas=2, **extra)


def _bebida(nombre="Cerveza", **extra):
    return Bebida(nombre=nombre, nombre_normalizado=nombre.casefold(),
                  precio=Decimal("800.00"), es_alcoholica=True, **extra)


def _postre(nombre="Flan", **extra):
    return Postre(nombre=nombre, nombre_normalizado=nombre.casefold(),
                  precio=Decimal("600.00"), **extra)


def _persistir_cinco_subtipos(
    seccion_id, persistir, vencido=False
):
    plato, bebida, postre = _plato(), _bebida(), _postre()
    menu = MenuEjecutivo(nombre="Menu", nombre_normalizado="menu",
                         precio=Decimal("2000.00"), plato=plato, postre=postre)
    hasta = date(2026, 6, 10) if vencido else date(2026, 6, 30)
    combo = ComboPromocion(nombre="Combo", nombre_normalizado="combo",
                           precio=Decimal("3000.00"), fecha_desde=date(2026, 6, 1),
                           fecha_hasta=hasta, platos=[plato])
    productos = {
        "plato": plato, "bebida": bebida, "postre": postre, "menu": menu, "combo": combo,
    }
    for producto in productos.values():
        producto.seccion_id = seccion_id
    ids = persistir(*productos.values())
    return dict(zip(productos, ids))


def _seccion_de(cliente, tipo, producto_id):
    respuesta = cliente.get(f"{RUTAS_PRODUCTO[tipo]}/{producto_id}")
    assert respuesta.status_code == 200
    return respuesta.json()["seccion_id"]


def test_sec_34_borrar_la_seccion_conserva_plato_y_bebida_con_seccion_id_nulo(
    cliente, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion())
    plato, bebida = _plato(), _bebida()
    plato.seccion_id = bebida.seccion_id = seccion_id
    plato_id, bebida_id = persistir(plato, bebida)

    assert cliente.delete(f"{RUTA}/{seccion_id}").status_code == 204

    assert _seccion_de(cliente, "plato", plato_id) is None
    assert _seccion_de(cliente, "bebida", bebida_id) is None


def test_sec_35_borrar_la_seccion_no_desvincula_los_productos_de_otra_seccion(
    cliente, crear_seccion, persistir
):
    borrada_id = persistir(crear_seccion(nombre="Entradas"))
    conservada_id = persistir(crear_seccion(nombre="Postres"))
    del_borrada = _plato(nombre="Milanesa")
    de_la_otra = _plato(nombre="Pizza")
    del_borrada.seccion_id = borrada_id
    de_la_otra.seccion_id = conservada_id
    del_borrada_id, de_la_otra_id = persistir(del_borrada, de_la_otra)

    assert cliente.delete(f"{RUTA}/{borrada_id}").status_code == 204

    assert _seccion_de(cliente, "plato", del_borrada_id) is None
    assert _seccion_de(cliente, "plato", de_la_otra_id) == conservada_id
    assert cliente.get(f"{RUTA}/{conservada_id}").status_code == 200


def test_sec_36_borrar_la_seccion_desvincula_los_cinco_subtipos(
    cliente, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion())
    ids = _persistir_cinco_subtipos(seccion_id, persistir)

    assert cliente.delete(f"{RUTA}/{seccion_id}").status_code == 204

    for tipo, producto_id in ids.items():
        assert _seccion_de(cliente, tipo, producto_id) is None


def test_sec_37_borrar_la_seccion_desvincula_un_combo_vencido(
    cliente, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion())
    ids = _persistir_cinco_subtipos(seccion_id, persistir, vencido=True)

    assert cliente.delete(f"{RUTA}/{seccion_id}").status_code == 204

    combo = cliente.get(f"{RUTAS_PRODUCTO['combo']}/{ids['combo']}").json()
    assert combo["seccion_id"] is None
    assert combo["fecha_hasta"] == "2026-06-10"
    assert combo["dado_de_baja"] is False


def test_sec_38_borrar_la_seccion_desvincula_un_postre_dado_de_baja(
    cliente, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion())
    postre = _postre()
    postre.dado_de_baja = True
    postre.seccion_id = seccion_id
    postre_id = persistir(postre)

    assert cliente.delete(f"{RUTA}/{seccion_id}").status_code == 204

    respuesta = cliente.get(f"{RUTAS_PRODUCTO['postre']}/{postre_id}")
    assert respuesta.status_code == 200
    assert respuesta.json()["seccion_id"] is None
    assert respuesta.json()["dado_de_baja"] is True


# --- posicion en la respuesta ---


def test_pos_01_la_consulta_incluye_la_posicion(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar", posicion=4).json()

    respuesta = cliente.get(f"{RUTA}/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": creada["id"],
        "nombre": "Entradas",
        "subtitulo": "Para comenzar",
        "posicion": 4,
        "productos_ids": [],
    }


def test_pos_09_posicion_en_el_limite_inferior_responde_201(cliente):
    respuesta = _crear(cliente, posicion=1)

    assert respuesta.status_code == 201
    assert respuesta.json()["posicion"] == 1


@pytest.mark.parametrize("posicion", ["3", 3.0])
def test_pos_29_posicion_como_texto_o_decimal_entero_se_devuelve_como_entero(
    cliente, posicion
):
    respuesta = _crear(cliente, posicion=posicion)

    assert respuesta.status_code == 201
    assert respuesta.json()["posicion"] == 3
    assert isinstance(respuesta.json()["posicion"], int)
    assert cliente.delete(f"{RUTA}/{respuesta.json()['id']}").status_code == 204


def test_pos_22_el_alta_devuelve_la_posicion_informada(cliente):
    respuesta = _crear(cliente, posicion=2)

    assert respuesta.status_code == 201
    assert respuesta.json()["posicion"] == 2


def test_pos_19_se_permiten_huecos_en_las_posiciones(cliente):
    respuesta = _crear(cliente, posicion=10)

    assert respuesta.status_code == 201
    assert respuesta.json()["posicion"] == 10


def test_pos_14_la_modificacion_conserva_la_propia_posicion(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar", posicion=3).json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}",
        json={"nombre": "Entradas", "subtitulo": "Nuevo", "posicion": 3},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["subtitulo"] == "Nuevo"
    assert respuesta.json()["posicion"] == 3


def test_pos_15_mover_una_seccion_a_una_posicion_libre(cliente):
    creada = _crear(cliente, posicion=1).json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}", json={"nombre": "Entradas", "posicion": 5}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["posicion"] == 5


def test_pos_25_la_modificacion_devuelve_la_nueva_posicion(cliente):
    creada = _crear(cliente, posicion=1).json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}", json={"nombre": "Entradas", "posicion": 7}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["posicion"] == 7
    assert cliente.get(f"{RUTA}/{creada['id']}").json()["posicion"] == 7


# --- posicion duplicada: 409, prioridades y atomicidad ---

MENSAJE_POSICION = "Ya existe una sección en esa posición"
MENSAJE_NOMBRE = "Ya existe una sección con ese nombre"


def _crear_con(cliente, nombre, posicion, **cuerpo):
    respuesta = cliente.post(
        RUTA, json={"nombre": nombre, "posicion": posicion, **cuerpo}
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def test_pos_11_posicion_duplicada_en_el_alta_responde_409_sin_crear_fila(cliente):
    existente = _crear_con(cliente, "Entradas", 1)

    respuesta = cliente.post(RUTA, json={"nombre": "Postres", "posicion": 1})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": MENSAJE_POSICION}
    assert cliente.get(f"{RUTA}/{existente['id']}").json() == existente
    assert cliente.get(f"{RUTA}/{existente['id'] + 1}").status_code == 404


def test_pos_12_el_409_por_posicion_usa_el_cuerpo_estandar(cliente):
    _crear_con(cliente, "Entradas", 1)

    respuesta = cliente.post(RUTA, json={"nombre": "Postres", "posicion": 1})

    assert respuesta.status_code == 409
    assert isinstance(respuesta.json(), dict)
    assert set(respuesta.json()) == {"detail"}
    assert respuesta.json()["detail"] == MENSAJE_POSICION


def test_pos_16_una_colision_no_desplaza_a_otras_secciones(cliente):
    creadas = [
        _crear_con(cliente, nombre, posicion)
        for nombre, posicion in (("Entradas", 1), ("Postres", 2), ("Bebidas", 3))
    ]

    respuesta = cliente.post(RUTA, json={"nombre": "Sopas", "posicion": 2})

    assert respuesta.status_code == 409
    assert [cliente.get(f"{RUTA}/{c['id']}").json() for c in creadas] == creadas
    assert cliente.get(f"{RUTA}/{creadas[-1]['id'] + 1}").status_code == 404


def test_pos_23_doble_colision_en_el_alta_devuelve_el_409_de_nombre(cliente):
    existente = _crear_con(cliente, "Entradas", 1)

    respuesta = cliente.post(RUTA, json={"nombre": "Entradas", "posicion": 1})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": MENSAJE_NOMBRE}
    assert cliente.get(f"{RUTA}/{existente['id']}").json() == existente
    assert cliente.get(f"{RUTA}/{existente['id'] + 1}").status_code == 404


def test_pos_24_prioridad_de_422_sobre_409_por_posicion_en_el_alta(cliente):
    existente = _crear_con(cliente, "Entradas", 1)

    respuesta = cliente.post(
        RUTA, json={"nombre": "Postres", "posicion": 1, "subtitulo": "x" * 201}
    )

    assert respuesta.status_code == 422
    assert cliente.get(f"{RUTA}/{existente['id'] + 1}").status_code == 404


def test_pos_13_posicion_duplicada_en_la_modificacion_responde_409_sin_cambios(
    cliente,
):
    a = _crear_con(cliente, "Entradas", 1)
    b = _crear_con(cliente, "Postres", 2)

    respuesta = cliente.put(f"{RUTA}/{b['id']}", json={"nombre": "Postres", "posicion": 1})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": MENSAJE_POSICION}
    assert cliente.get(f"{RUTA}/{a['id']}").json() == a
    assert cliente.get(f"{RUTA}/{b['id']}").json() == b


def test_pos_21_el_intercambio_directo_es_rechazado(cliente):
    a = _crear_con(cliente, "Entradas", 1)
    b = _crear_con(cliente, "Postres", 2)

    respuesta = cliente.put(f"{RUTA}/{a['id']}", json={"nombre": "Entradas", "posicion": 2})

    assert respuesta.status_code == 409
    assert cliente.get(f"{RUTA}/{a['id']}").json() == a
    assert cliente.get(f"{RUTA}/{b['id']}").json() == b


def test_pos_26_doble_colision_en_la_modificacion_devuelve_el_409_de_nombre(cliente):
    a = _crear_con(cliente, "Entradas", 1)
    b = _crear_con(cliente, "Postres", 2)

    respuesta = cliente.put(f"{RUTA}/{b['id']}", json={"nombre": "entradas", "posicion": 1})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": MENSAJE_NOMBRE}
    assert cliente.get(f"{RUTA}/{a['id']}").json() == a
    assert cliente.get(f"{RUTA}/{b['id']}").json() == b


def test_pos_27_prioridad_de_404_sobre_409_por_posicion_en_la_modificacion(cliente):
    a = _crear_con(cliente, "Entradas", 1)

    respuesta = cliente.put(f"{RUTA}/999", json={"nombre": "Postres", "posicion": 1})

    assert respuesta.status_code == 404
    assert cliente.get(f"{RUTA}/{a['id']}").json() == a


def test_pos_28_prioridad_de_422_sobre_409_por_posicion_en_la_modificacion(cliente):
    _crear_con(cliente, "Entradas", 1)
    b = _crear_con(cliente, "Postres", 2)

    respuesta = cliente.put(
        f"{RUTA}/{b['id']}",
        json={"nombre": "Postres", "posicion": 1, "subtitulo": "x" * 201},
    )

    assert respuesta.status_code == 422
    assert cliente.get(f"{RUTA}/{b['id']}").json() == b


# --- liberación, huecos e intercambio (caracterización) ---


def test_pos_17_reutilizacion_de_la_posicion_tras_el_borrado(cliente):
    a = _crear_con(cliente, "Entradas", 1)
    assert cliente.delete(f"{RUTA}/{a['id']}").status_code == 204

    respuesta = cliente.post(RUTA, json={"nombre": "Postres", "posicion": 1})

    assert respuesta.status_code == 201
    assert respuesta.json()["posicion"] == 1


def test_pos_18_el_borrado_no_renumera_las_demas_secciones(cliente):
    a = _crear_con(cliente, "Entradas", 1)
    b = _crear_con(cliente, "Postres", 2)
    c = _crear_con(cliente, "Bebidas", 3)

    assert cliente.delete(f"{RUTA}/{b['id']}").status_code == 204

    assert cliente.get(f"{RUTA}/{a['id']}").json()["posicion"] == 1
    assert cliente.get(f"{RUTA}/{c['id']}").json()["posicion"] == 3


def test_pos_20_intercambio_de_dos_secciones_en_tres_put(cliente):
    a = _crear_con(cliente, "Entradas", 1)
    b = _crear_con(cliente, "Postres", 2)

    pasos = [
        (a["id"], {"nombre": "Entradas", "posicion": 99}),
        (b["id"], {"nombre": "Postres", "posicion": 1}),
        (a["id"], {"nombre": "Entradas", "posicion": 2}),
    ]
    for seccion_id, cuerpo in pasos:
        assert cliente.put(f"{RUTA}/{seccion_id}", json=cuerpo).status_code == 200

    assert cliente.get(f"{RUTA}/{a['id']}").json()["posicion"] == 2
    assert cliente.get(f"{RUTA}/{b['id']}").json()["posicion"] == 1


# --- productos_ids: comportamiento HTTP (IDS-04..17) ---

_nombres = itertools.count(1)


def _cuerpo_producto(tipo, seccion_id, **extra):
    """Cuerpo mínimo válido de alta o modificación de cada subtipo."""
    n = next(_nombres)
    comun = {"nombre": f"Producto {n}", "precio": "1000.00", "seccion_id": seccion_id}
    if tipo == "plato":
        return {**comun, "cant_personas": 2, **extra}
    if tipo == "bebida":
        return {**comun, "es_alcoholica": False, **extra}
    if tipo == "postre":
        return {**comun, **extra}
    if tipo == "menu":
        return {**comun, "plato_id": extra.pop("plato_id"),
                "postre_id": extra.pop("postre_id"), **extra}
    return {
        **comun,
        "fecha_desde": "2026-06-01",
        "fecha_hasta": extra.pop("fecha_hasta", "2026-06-30"),
        "platos_ids": [extra.pop("plato_id")],
        "bebidas_ids": [],
        "postres_ids": [],
        **extra,
    }


def _alta(cliente, tipo="plato", seccion_id=None, **extra):
    respuesta = cliente.post(
        RUTAS_PRODUCTO[tipo], json=_cuerpo_producto(tipo, seccion_id, **extra)
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _mover(cliente, producto, seccion_id, tipo="plato", **extra):
    """PUT completo del producto con otra sección (reemplazo completo)."""
    cuerpo = {
        clave: producto[clave]
        for clave in ("nombre", "precio", "cant_personas", "es_alcoholica")
        if clave in producto
    }
    cuerpo.update(seccion_id=seccion_id, **extra)
    respuesta = cliente.put(f"{RUTAS_PRODUCTO[tipo]}/{producto['id']}", json=cuerpo)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _dar_de_baja(cliente, producto, tipo="plato"):
    assert cliente.delete(f"{RUTAS_PRODUCTO[tipo]}/{producto['id']}").status_code == 204


def _ids(cliente, seccion):
    respuesta = cliente.get(f"{RUTA}/{seccion['id']}")
    assert respuesta.status_code == 200
    return respuesta.json()["productos_ids"]


def test_ids_06_get_incluye_solo_productos_activos(cliente):
    seccion = _crear(cliente).json()
    plato = _alta(cliente, "plato", seccion["id"])
    bebida = _alta(cliente, "bebida", seccion["id"])
    postre = _alta(cliente, "postre", seccion["id"])
    _dar_de_baja(cliente, bebida, "bebida")

    assert _ids(cliente, seccion) == [plato["id"], postre["id"]]


def test_ids_07_seccion_con_solo_productos_dados_de_baja_devuelve_lista_vacia(cliente):
    seccion = _crear(cliente).json()
    plato = _alta(cliente, "plato", seccion["id"])
    _dar_de_baja(cliente, plato)

    assert _ids(cliente, seccion) == []


def test_ids_08_get_devuelve_ids_ascendentes(cliente):
    seccion = _crear(cliente).json()
    menor, medio, mayor = (_alta(cliente, "postre") for _ in range(3))
    assert menor["id"] < medio["id"] < mayor["id"]
    for producto in (mayor, menor, medio):  # orden de asignación 12, 10, 11
        _mover(cliente, producto, seccion["id"], "postre")

    assert _ids(cliente, seccion) == [menor["id"], medio["id"], mayor["id"]]


def test_ids_15_get_no_incluye_productos_de_otras_secciones_ni_sin_seccion(cliente):
    a = _crear(cliente, nombre="A").json()
    b = _crear(cliente, nombre="B").json()
    plato = _alta(cliente, "plato", a["id"])
    _alta(cliente, "postre", b["id"])
    _alta(cliente, "bebida", None)

    assert _ids(cliente, a) == [plato["id"]]


def _cinco_subtipos(cliente, seccion_id, fecha_hasta="2026-06-30"):
    plato = _alta(cliente, "plato", seccion_id)
    bebida = _alta(cliente, "bebida", seccion_id)
    postre = _alta(cliente, "postre", seccion_id)
    menu = _alta(cliente, "menu", seccion_id,
                 plato_id=plato["id"], postre_id=postre["id"])
    combo = _alta(cliente, "combo", seccion_id,
                  plato_id=plato["id"], fecha_hasta=fecha_hasta)
    return plato, bebida, postre, menu, combo


def test_ids_09_get_cuenta_los_cinco_subtipos(cliente):
    seccion = _crear(cliente).json()

    productos = _cinco_subtipos(cliente, seccion["id"])

    esperados = sorted(p["id"] for p in productos)
    assert len(set(esperados)) == 5
    assert _ids(cliente, seccion) == esperados


def test_ids_10_get_incluye_combo_vencido_pero_activo(
    cliente, crear_seccion, persistir
):
    # El alta HTTP rechaza combos vencidos: se persiste directamente (como SEC-37)
    seccion_id = persistir(crear_seccion())
    plato = _plato()
    combo = ComboPromocion(nombre="Combo", nombre_normalizado="combo",
                           precio=Decimal("3000.00"), fecha_desde=date(2026, 6, 1),
                           fecha_hasta=date(2026, 6, 14), platos=[plato],
                           seccion_id=seccion_id)
    combo_id = persistir(combo)

    detalle = cliente.get(f"{RUTAS_PRODUCTO['combo']}/{combo_id}").json()
    assert detalle["dado_de_baja"] is False
    assert detalle["fecha_hasta"] < "2026-06-15"  # HOY_FIJO: ya venció
    assert cliente.get(f"{RUTA}/{seccion_id}").json()["productos_ids"] == [combo_id]


def test_ids_11_dar_de_baja_un_producto_lo_quita(cliente):
    seccion = _crear(cliente).json()
    plato = _alta(cliente, "plato", seccion["id"])
    bebida = _alta(cliente, "bebida", seccion["id"])
    assert _ids(cliente, seccion) == [plato["id"], bebida["id"]]

    _dar_de_baja(cliente, plato)

    assert _ids(cliente, seccion) == [bebida["id"]]
    conservado = cliente.get(f"{RUTAS_PRODUCTO['plato']}/{plato['id']}").json()
    assert conservado["seccion_id"] == seccion["id"]
    assert conservado["dado_de_baja"] is True


def test_ids_12_reactivar_un_producto_lo_reincorpora(cliente):
    seccion = _crear(cliente).json()
    plato = _alta(cliente, "plato", seccion["id"])
    bebida = _alta(cliente, "bebida", seccion["id"])
    _dar_de_baja(cliente, plato)
    assert _ids(cliente, seccion) == [bebida["id"]]

    _mover(cliente, plato, seccion["id"], dado_de_baja=False)

    assert _ids(cliente, seccion) == [plato["id"], bebida["id"]]


def test_ids_13_cambiar_la_seccion_de_un_producto_lo_mueve(cliente):
    a = _crear(cliente, nombre="A").json()
    b = _crear(cliente, nombre="B").json()
    plato = _alta(cliente, "plato", a["id"])
    assert _ids(cliente, a) == [plato["id"]]

    _mover(cliente, plato, b["id"])

    assert _ids(cliente, a) == []
    assert _ids(cliente, b) == [plato["id"]]


def test_ids_14_desasignar_un_producto_lo_quita(cliente):
    seccion = _crear(cliente).json()
    plato = _alta(cliente, "plato", seccion["id"])
    assert _ids(cliente, seccion) == [plato["id"]]

    _mover(cliente, plato, None)

    assert _ids(cliente, seccion) == []


def test_ids_16_no_quedan_ids_obsoletos_tras_borrar_y_crear_una_seccion(cliente):
    seccion = _crear(cliente, nombre="Vieja").json()
    plato = _alta(cliente, "plato", seccion["id"])
    assert cliente.delete(f"{RUTA}/{seccion['id']}").status_code == 204

    nueva = _crear(cliente, nombre="Nueva").json()

    assert _ids(cliente, nueva) == []
    conservado = cliente.get(f"{RUTAS_PRODUCTO['plato']}/{plato['id']}")
    assert conservado.status_code == 200
    assert conservado.json()["seccion_id"] is None


def test_ids_17_no_existe_listado_de_productos_por_seccion(cliente):
    seccion = _crear(cliente).json()
    _alta(cliente, "plato", seccion["id"])

    assert cliente.get(f"{RUTA}/{seccion['id']}/productos").status_code == 404


def test_ids_02_el_alta_devuelve_lista_vacia_aunque_existan_otros_productos(cliente):
    otra = _crear(cliente, nombre="Otra").json()
    _alta(cliente, "plato", None)
    _alta(cliente, "postre", otra["id"])

    respuesta = _crear(cliente, nombre="Nueva")

    assert respuesta.status_code == 201
    assert respuesta.json()["productos_ids"] == []


def test_ids_04_el_put_devuelve_el_estado_persistido(cliente):
    seccion = _crear(cliente).json()
    plato = _alta(cliente, "plato", seccion["id"])
    postre = _alta(cliente, "postre", seccion["id"])
    _dar_de_baja(cliente, postre, "postre")

    respuesta = cliente.put(
        f"{RUTA}/{seccion['id']}",
        json={"nombre": "Entradas", "posicion": seccion["posicion"]},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["productos_ids"] == [plato["id"]]
    assert cliente.get(f"{RUTA}/{seccion['id']}").json() == respuesta.json()


def test_ids_05_enviar_productos_ids_en_el_put_no_cambia_la_asignacion(cliente):
    seccion = _crear(cliente).json()
    plato = _alta(cliente, "plato", seccion["id"])
    postre = _alta(cliente, "postre", None)

    respuesta = cliente.put(
        f"{RUTA}/{seccion['id']}",
        json={
            "nombre": "Entradas",
            "posicion": seccion["posicion"],
            "productos_ids": [postre["id"]],
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["productos_ids"] == [plato["id"]]
    plato_actual = cliente.get(f"{RUTAS_PRODUCTO['plato']}/{plato['id']}").json()
    postre_actual = cliente.get(f"{RUTAS_PRODUCTO['postre']}/{postre['id']}").json()
    assert plato_actual["seccion_id"] == seccion["id"]
    assert postre_actual["seccion_id"] is None


def test_productos_ids_el_alta_ignora_productos_ids_del_cuerpo(cliente):
    postre = _alta(cliente, "postre", None)

    respuesta = _crear(cliente, productos_ids=[postre["id"]])

    assert respuesta.status_code == 201
    assert respuesta.json()["productos_ids"] == []
    actual = cliente.get(f"{RUTAS_PRODUCTO['postre']}/{postre['id']}").json()
    assert actual["seccion_id"] is None


def test_sec_25_el_put_incluye_productos_ids_vigentes(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()
    plato = _alta(cliente, "plato", creada["id"])
    bebida = _alta(cliente, "bebida", creada["id"])

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}",
        json={"nombre": "Aperitivos", "subtitulo": "Para compartir", "posicion": 1},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": creada["id"],
        "nombre": "Aperitivos",
        "subtitulo": "Para compartir",
        "posicion": 1,
        "productos_ids": [plato["id"], bebida["id"]],
    }


def test_sec_30_la_modificacion_no_altera_los_productos_asignados(cliente):
    creada = _crear(cliente).json()
    plato = _alta(cliente, "plato", creada["id"])

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}", json={"nombre": "Aperitivos", "posicion": 1}
    )

    assert respuesta.status_code == 200
    assert plato["id"] in respuesta.json()["productos_ids"]
    actual = cliente.get(f"{RUTAS_PRODUCTO['plato']}/{plato['id']}").json()
    assert actual["seccion_id"] == creada["id"]


def test_productos_ids_solicitudes_rechazadas_no_alteran_el_get(cliente):
    seccion = _crear(cliente, nombre="Entradas", posicion=1).json()
    otra = _crear(cliente, nombre="Postres", posicion=2).json()
    plato = _alta(cliente, "plato", seccion["id"])
    antes = cliente.get(f"{RUTA}/{seccion['id']}").json()
    assert antes["productos_ids"] == [plato["id"]]

    alta_409 = cliente.post(RUTA, json={"nombre": "Entradas", "posicion": 50})
    alta_422 = cliente.post(RUTA, json={"nombre": "", "posicion": 51})
    put_409 = cliente.put(
        f"{RUTA}/{otra['id']}", json={"nombre": "Entradas", "posicion": 2}
    )
    put_422 = cliente.put(
        f"{RUTA}/{seccion['id']}", json={"nombre": "", "posicion": 1}
    )

    assert [r.status_code for r in (alta_409, alta_422, put_409, put_422)] == [
        409, 422, 409, 422,
    ]
    assert cliente.get(f"{RUTA}/{seccion['id']}").json() == antes
    assert cliente.get(f"{RUTA}/{otra['id']}").json()["productos_ids"] == []
