def _cuerpo(**cambios):
    return {"nombre": "Cerveza", "precio": "800.00", "es_alcoholica": True, **cambios}


def test_cat_07_crear_bebida_responde_201_con_id(cliente):
    respuesta = cliente.post("/productos/bebidas", json=_cuerpo())

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert isinstance(cuerpo["id"], int)
    assert cuerpo["tipo"] == "bebida"
    assert cuerpo["es_alcoholica"] is True
    assert cuerpo["dado_de_baja"] is False


def test_obtener_bebida_por_id_devuelve_la_bebida(cliente):
    creada = cliente.post("/productos/bebidas", json=_cuerpo()).json()

    respuesta = cliente.get(f"/productos/bebidas/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_cat_08_get_de_bebida_con_id_de_un_plato_responde_404(cliente):
    plato = cliente.post(
        "/productos/platos", json={"nombre": "Milanesa", "precio": "1500.00", "cant_personas": 2}
    ).json()

    respuesta = cliente.get(f"/productos/bebidas/{plato['id']}")

    assert respuesta.status_code == 404


def test_cat_11_put_de_bebida_desconocida_responde_404(cliente):
    assert cliente.put("/productos/bebidas/999", json=_cuerpo()).status_code == 404


def test_cat_13_put_de_bebida_es_reemplazo_completo(cliente):
    creada = cliente.post(
        "/productos/bebidas", json=_cuerpo(descripcion="Rubia", imagen="c.png")
    ).json()

    respuesta = cliente.put(
        f"/productos/bebidas/{creada['id']}", json=_cuerpo(es_alcoholica=False)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["descripcion"] is None
    assert respuesta.json()["imagen"] is None
    assert respuesta.json()["es_alcoholica"] is False


def test_cat_27_bebida_sin_es_alcoholica_responde_422(cliente):
    respuesta = cliente.post("/productos/bebidas", json={"nombre": "Cerveza", "precio": "800.00"})

    assert respuesta.status_code == 422
