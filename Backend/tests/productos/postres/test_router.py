def _cuerpo(**cambios):
    return {"nombre": "Flan", "precio": "600.00", **cambios}


def test_cat_07_crear_postre_responde_201_con_id(cliente):
    respuesta = cliente.post("/productos/postres", json=_cuerpo())

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert isinstance(cuerpo["id"], int)
    assert cuerpo["tipo"] == "postre"
    assert cuerpo["dado_de_baja"] is False


def test_cat_10_get_de_postre_dado_de_baja_responde_200_con_dado_de_baja(
    cliente, crear_postre, persistir
):
    postre = crear_postre()
    postre.dado_de_baja = True
    postre_id = persistir(postre)

    respuesta = cliente.get(f"/productos/postres/{postre_id}")

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert respuesta.json()["id"] == postre_id


def test_cat_08_get_de_postre_con_id_de_una_bebida_responde_404(cliente):
    bebida = cliente.post(
        "/productos/bebidas",
        json={"nombre": "Cerveza", "precio": "800.00", "es_alcoholica": True},
    ).json()

    assert cliente.get(f"/productos/postres/{bebida['id']}").status_code == 404


def test_get_de_postre_desconocido_responde_404(cliente):
    assert cliente.get("/productos/postres/999").status_code == 404


def test_cat_11_put_de_postre_desconocido_responde_404(cliente):
    assert cliente.put("/productos/postres/999", json=_cuerpo()).status_code == 404


def test_cat_12_put_sin_dado_de_baja_conserva_el_estado_del_postre(
    cliente, crear_postre, persistir
):
    postre = crear_postre()
    postre.dado_de_baja = True
    postre_id = persistir(postre)

    respuesta = cliente.put(f"/productos/postres/{postre_id}", json=_cuerpo(descripcion="Nueva"))

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert respuesta.json()["descripcion"] == "Nueva"


def test_cat_13_put_de_postre_es_reemplazo_completo(cliente):
    creado = cliente.post(
        "/productos/postres", json=_cuerpo(descripcion="Casero", imagen="f.png")
    ).json()

    respuesta = cliente.put(f"/productos/postres/{creado['id']}", json=_cuerpo(precio="650.00"))

    assert respuesta.status_code == 200
    assert respuesta.json()["precio"] == "650.00"
    assert respuesta.json()["descripcion"] is None
    assert respuesta.json()["imagen"] is None


def test_cat_s_21_el_postre_acepta_seccion_id_ademas_de_los_campos_comunes(
    cliente, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion())

    respuesta = cliente.post(
        "/productos/postres",
        json=_cuerpo(descripcion="Casero", imagen="f.png", seccion_id=seccion_id),
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["seccion_id"] == seccion_id
    assert respuesta.json()["descripcion"] == "Casero"


def test_cat_s_05_crear_postre_con_seccion_inexistente_responde_422(cliente):
    assert cliente.post("/productos/postres", json=_cuerpo(seccion_id=999)).status_code == 422
