RUTA = "/promociones"


def test_pro_14_obtener_por_id(cliente, persistir, crear_plato, crear_promocion):
    plato = crear_plato()
    plato_id, promocion_id = persistir(plato, crear_promocion([plato], nombre="Verano"))
    respuesta = cliente.get(f"{RUTA}/{promocion_id}")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id"] == promocion_id
    assert cuerpo["nombre"] == "Verano"
    assert cuerpo["productos_ids"] == [plato_id]


def test_pro_15_id_desconocido(cliente):
    assert cliente.get(f"{RUTA}/999").status_code == 404


def test_pro_16_obtener_una_promocion_dada_de_baja(
    cliente, persistir, crear_plato, crear_promocion
):
    promocion_id = persistir(crear_promocion([crear_plato()], dado_de_baja=True))
    respuesta = cliente.get(f"{RUTA}/{promocion_id}")
    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True


def _dos_promociones(persistir, crear_plato, crear_promocion):
    plato = crear_plato()
    activa = crear_promocion([plato], nombre="Activa")
    baja = crear_promocion([plato], nombre="Baja", dado_de_baja=True)
    return persistir(activa, baja)


def test_pro_17_el_listado_oculta_las_bajas_por_defecto(
    cliente, persistir, crear_plato, crear_promocion
):
    activa_id, _ = _dos_promociones(persistir, crear_plato, crear_promocion)
    respuesta = cliente.get(RUTA)
    assert respuesta.status_code == 200
    assert [p["id"] for p in respuesta.json()] == [activa_id]


def test_pro_18_el_listado_con_bajas(cliente, persistir, crear_plato, crear_promocion):
    activa_id, baja_id = _dos_promociones(persistir, crear_plato, crear_promocion)
    respuesta = cliente.get(RUTA, params={"incluir_bajas": "true"})
    assert respuesta.status_code == 200
    assert [p["id"] for p in respuesta.json()] == [activa_id, baja_id]


def test_listado_vacio(cliente):
    respuesta = cliente.get(RUTA)
    assert respuesta.status_code == 200
    assert respuesta.json() == []
