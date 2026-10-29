import pytest

RUTA = "/secciones"


def _crear(cliente, **cuerpo):
    return cliente.post(RUTA, json={"nombre": "Entradas", **cuerpo})


def test_sec_02_la_respuesta_no_incluye_productos_ni_estado_de_baja(cliente):
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
    }


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
        pytest.param("entradas", id="sec_12_mayusculas"),
        pytest.param("  Entradas ", id="sec_13_espacios"),
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


def test_sec_23_obtener_una_seccion_inexistente_responde_404(cliente):
    respuesta = cliente.get(f"{RUTA}/999")

    assert respuesta.status_code == 404
    assert "detail" in respuesta.json()


def test_sec_24_no_existe_el_listado_de_secciones(cliente):
    assert cliente.get(RUTA).status_code == 405


def test_la_ruta_por_id_exige_un_entero(cliente):
    assert cliente.get(f"{RUTA}/abc").status_code == 404
    assert cliente.put(f"{RUTA}/abc", json={"nombre": "x"}).status_code == 404
    assert cliente.delete(f"{RUTA}/abc").status_code == 404


def test_sec_25_modificar_una_seccion(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}", json={"nombre": "Aperitivos", "subtitulo": "Para compartir"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": creada["id"],
        "nombre": "Aperitivos",
        "subtitulo": "Para compartir",
    }
    assert cliente.get(f"{RUTA}/{creada['id']}").json() == respuesta.json()


def test_sec_26_el_put_es_un_reemplazo_completo(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()

    respuesta = cliente.put(f"{RUTA}/{creada['id']}", json={"nombre": "Entradas"})

    assert respuesta.status_code == 200
    assert respuesta.json()["subtitulo"] is None


def test_sec_27_actualizar_una_seccion_inexistente_responde_404(cliente):
    assert cliente.put(f"{RUTA}/999", json={"nombre": "Entradas"}).status_code == 404


def test_sec_28_el_422_tiene_prioridad_sobre_el_404_en_la_modificacion(cliente):
    assert cliente.put(f"{RUTA}/999", json={"nombre": ""}).status_code == 422


def test_sec_29_el_404_tiene_prioridad_sobre_el_409_en_la_modificacion(cliente):
    _crear(cliente)

    assert cliente.put(f"{RUTA}/999", json={"nombre": "Entradas"}).status_code == 404


def test_sec_15_nombre_duplicado_en_la_modificacion_responde_409_sin_cambios(cliente):
    _crear(cliente, nombre="Entradas")
    postres = _crear(cliente, nombre="Postres", subtitulo="Dulces").json()

    respuesta = cliente.put(f"{RUTA}/{postres['id']}", json={"nombre": "entradas"})

    assert respuesta.status_code == 409
    assert cliente.get(f"{RUTA}/{postres['id']}").json() == postres


def test_sec_16_la_modificacion_conserva_el_propio_nombre(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}", json={"nombre": "Entradas", "subtitulo": "Nuevo"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["subtitulo"] == "Nuevo"


def test_sec_17_la_modificacion_puede_cambiar_solo_las_mayusculas(cliente):
    creada = _crear(cliente).json()

    respuesta = cliente.put(f"{RUTA}/{creada['id']}", json={"nombre": "ENTRADAS"})

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "ENTRADAS"


def test_sec_44_el_put_recorta_y_normaliza_el_subtitulo(cliente):
    creada = _crear(cliente, subtitulo="Para comenzar").json()

    respuesta = cliente.put(
        f"{RUTA}/{creada['id']}", json={"nombre": "Entradas", "subtitulo": "   "}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["subtitulo"] is None


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
