from datetime import date

import pytest

PREFIJO = "/productos/combos"
AYER = date(2026, 6, 14)  # HOY fijo de las pruebas es 2026-06-15


@pytest.fixture
def componentes(crear_plato, crear_bebida, crear_postre, persistir):
    """Plato, Bebida y Postre activos ya guardados: (plato_id, bebida_id, postre_id)."""
    return persistir(
        crear_plato(nombre="Milanesa"), crear_bebida(nombre="Cerveza"), crear_postre(nombre="Flan")
    )


def _cuerpo(**cambios):
    return {
        "nombre": "Combo",
        "precio": "3000.00",
        "fecha_desde": "2026-06-01",
        "fecha_hasta": "2026-06-30",
        "platos_ids": [],
        "bebidas_ids": [],
        "postres_ids": [],
        **cambios,
    }


def _combo_vencido(crear_combo, plato, **cambios):
    """Combo con `fecha_hasta` de ayer; su precio y nombre coinciden con `_cuerpo`."""
    return crear_combo(desde=date(2026, 5, 1), hasta=AYER, platos=[plato], **cambios)


def _cuerpo_vencido(plato_id, **cambios):
    return _cuerpo(fecha_desde="2026-05-01", fecha_hasta=AYER.isoformat(), platos_ids=[plato_id], **cambios)


def test_cat_34_combo_valido_responde_201_con_los_componentes(cliente, componentes):
    plato_id, bebida_id, postre_id = componentes

    respuesta = cliente.post(
        PREFIJO,
        json=_cuerpo(platos_ids=[plato_id], bebidas_ids=[bebida_id], postres_ids=[postre_id]),
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert isinstance(cuerpo["id"], int)
    assert cuerpo["tipo"] == "combo_promocion"
    assert cuerpo["platos_ids"] == [plato_id]
    assert cuerpo["bebidas_ids"] == [bebida_id]
    assert cuerpo["postres_ids"] == [postre_id]
    assert cuerpo["fecha_desde"] == "2026-06-01"
    assert cuerpo["fecha_hasta"] == "2026-06-30"
    assert cuerpo["dado_de_baja"] is False


def test_cat_34_combo_con_fecha_hasta_igual_a_hoy_se_acepta(cliente, componentes):
    plato_id, *_ = componentes

    respuesta = cliente.post(PREFIJO, json=_cuerpo(fecha_hasta="2026-06-15", platos_ids=[plato_id]))

    assert respuesta.status_code == 201


def test_obtener_combo_por_id_devuelve_el_combo(cliente, componentes):
    plato_id, *_ = componentes
    creado = cliente.post(PREFIJO, json=_cuerpo(platos_ids=[plato_id])).json()

    respuesta = cliente.get(f"{PREFIJO}/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_cat_08_get_de_combo_con_id_de_un_plato_responde_404(cliente, componentes):
    plato_id, *_ = componentes

    assert cliente.get(f"{PREFIJO}/{plato_id}").status_code == 404


def test_cat_35_combo_con_las_tres_listas_vacias_responde_422(cliente):
    assert cliente.post(PREFIJO, json=_cuerpo()).status_code == 422


def test_cat_36_combo_con_un_unico_componente_responde_201(cliente, componentes):
    _, bebida_id, _ = componentes

    respuesta = cliente.post(PREFIJO, json=_cuerpo(bebidas_ids=[bebida_id]))

    assert respuesta.status_code == 201
    assert respuesta.json()["bebidas_ids"] == [bebida_id]
    assert respuesta.json()["platos_ids"] == []


def test_cat_37_ids_duplicados_en_una_lista_responden_422(cliente, componentes):
    plato_id, *_ = componentes

    respuesta = cliente.post(PREFIJO, json=_cuerpo(platos_ids=[plato_id, plato_id]))

    assert respuesta.status_code == 422


def test_cat_38_bebidas_ids_con_un_plato_responde_422_con_los_ids(cliente, componentes):
    plato_id, *_ = componentes

    respuesta = cliente.post(PREFIJO, json=_cuerpo(bebidas_ids=[plato_id]))

    assert respuesta.status_code == 422
    error = respuesta.json()["detail"][0]
    assert error["loc"] == ["body", "bebidas_ids"]
    assert error["ids"] == [plato_id]


def test_cat_38_bebidas_ids_con_un_id_inexistente_responde_422_con_los_ids(cliente):
    respuesta = cliente.post(PREFIJO, json=_cuerpo(bebidas_ids=[999]))

    assert respuesta.status_code == 422
    error = respuesta.json()["detail"][0]
    assert error["loc"] == ["body", "bebidas_ids"]
    assert error["ids"] == [999]


def test_cat_39_bebida_inactiva_responde_409_con_los_ids(cliente, crear_bebida, persistir):
    bebida = crear_bebida()
    bebida.dado_de_baja = True
    bebida_id = persistir(bebida)

    respuesta = cliente.post(PREFIJO, json=_cuerpo(bebidas_ids=[bebida_id]))

    assert respuesta.status_code == 409
    assert respuesta.json()["ids"] == [bebida_id]


def test_cat_40_fecha_hasta_anterior_a_hoy_responde_422_sobre_fecha_hasta(cliente, componentes):
    plato_id, *_ = componentes

    respuesta = cliente.post(
        PREFIJO, json=_cuerpo(fecha_desde="2026-05-01", fecha_hasta="2026-06-14", platos_ids=[plato_id])
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["loc"] == ["body", "fecha_hasta"]


def test_cat_29_rango_de_fechas_invertido_responde_422(cliente, componentes):
    plato_id, *_ = componentes

    respuesta = cliente.post(
        PREFIJO, json=_cuerpo(fecha_desde="2026-07-01", fecha_hasta="2026-06-20", platos_ids=[plato_id])
    )

    assert respuesta.status_code == 422


def test_cat_21_combo_con_nombre_de_producto_activo_responde_409(cliente, componentes):
    plato_id, *_ = componentes

    respuesta = cliente.post(PREFIJO, json=_cuerpo(nombre="milanesa", platos_ids=[plato_id]))

    assert respuesta.status_code == 409


def test_cat_45_editar_un_combo_vencido_responde_409(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    plato_id, combo_id = persistir(plato, _combo_vencido(crear_combo, plato))

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}", json=_cuerpo_vencido(plato_id, descripcion="Nueva")
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"{PREFIJO}/{combo_id}").json()["descripcion"] is None


def test_cat_46_reactivar_un_combo_vencido_responde_409(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    combo = _combo_vencido(crear_combo, plato)
    combo.dado_de_baja = True
    plato_id, combo_id = persistir(plato, combo)

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}", json=_cuerpo_vencido(plato_id, dado_de_baja=False)
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"{PREFIJO}/{combo_id}").json()["dado_de_baja"] is True


def test_cat_47_baja_via_put_de_un_combo_vencido_activo_responde_200_de_baja(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    plato_id, combo_id = persistir(plato, _combo_vencido(crear_combo, plato))

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}", json=_cuerpo_vencido(plato_id, dado_de_baja=True)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert cliente.get(f"{PREFIJO}/{combo_id}").json()["dado_de_baja"] is True


def test_cat_48_baja_repetida_via_put_de_un_combo_vencido_responde_200_sin_cambios(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    combo = _combo_vencido(crear_combo, plato)
    combo.dado_de_baja = True
    plato_id, combo_id = persistir(plato, combo)
    antes = cliente.get(f"{PREFIJO}/{combo_id}").json()

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}", json=_cuerpo_vencido(plato_id, dado_de_baja=True)
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == antes
    assert cliente.get(f"{PREFIJO}/{combo_id}").json() == antes


def test_cat_49_baja_via_put_de_un_combo_vencido_con_nuevo_precio_responde_409_sin_cambios(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    plato_id, combo_id = persistir(plato, _combo_vencido(crear_combo, plato))
    antes = cliente.get(f"{PREFIJO}/{combo_id}").json()

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}",
        json=_cuerpo_vencido(plato_id, dado_de_baja=True, precio="3500.00"),
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"{PREFIJO}/{combo_id}").json() == antes


def test_ld_17_delete_de_un_combo_vencido_responde_204_y_queda_de_baja(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    _, combo_id = persistir(plato, _combo_vencido(crear_combo, plato))

    respuesta = cliente.delete(f"{PREFIJO}/{combo_id}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert cliente.get(f"{PREFIJO}/{combo_id}").json()["dado_de_baja"] is True


def test_delete_de_combo_desconocido_responde_404(cliente):
    assert cliente.delete(f"{PREFIJO}/999").status_code == 404


def test_ld_18_baja_via_put_de_un_combo_no_vencido_responde_200_de_baja(cliente, componentes):
    plato_id, *_ = componentes
    creado = cliente.post(PREFIJO, json=_cuerpo(platos_ids=[plato_id])).json()

    respuesta = cliente.put(
        f"{PREFIJO}/{creado['id']}", json=_cuerpo(platos_ids=[plato_id], dado_de_baja=True)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True


def test_ld_20_reactivar_combo_con_componentes_activos_responde_200(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    combo = crear_combo(platos=[plato])
    combo.dado_de_baja = True
    plato_id, combo_id = persistir(plato, combo)

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}", json=_cuerpo(platos_ids=[plato_id], dado_de_baja=False)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is False


def test_put_de_combo_activo_con_componente_inactivo_responde_409_con_ids(
    cliente, crear_plato, crear_bebida, persistir
):
    plato = crear_plato()
    bebida = crear_bebida()
    bebida.dado_de_baja = True
    plato_id, bebida_id = persistir(plato, bebida)
    creado = cliente.post(PREFIJO, json=_cuerpo(platos_ids=[plato_id])).json()

    respuesta = cliente.put(
        f"{PREFIJO}/{creado['id']}", json=_cuerpo(platos_ids=[plato_id], bebidas_ids=[bebida_id])
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["ids"] == [bebida_id]


def test_cat_s_04_crear_combo_con_seccion(cliente, componentes, crear_seccion, persistir):
    plato_id, *_ = componentes
    seccion_id = persistir(crear_seccion())

    respuesta = cliente.post(PREFIJO, json=_cuerpo(platos_ids=[plato_id], seccion_id=seccion_id))

    assert respuesta.status_code == 201
    assert respuesta.json()["seccion_id"] == seccion_id


def test_cat_s_05_crear_combo_con_seccion_inexistente_responde_422(cliente, componentes):
    plato_id, *_ = componentes

    respuesta = cliente.post(PREFIJO, json=_cuerpo(platos_ids=[plato_id], seccion_id=999))

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "seccion_inexistente"


def test_cat_s_09_put_de_combo_vigente_acepta_y_rechaza_seccion_id(
    cliente, componentes, crear_seccion, persistir
):
    plato_id, *_ = componentes
    seccion_id = persistir(crear_seccion())
    combo = cliente.post(PREFIJO, json=_cuerpo(platos_ids=[plato_id])).json()

    valido = cliente.put(
        f"{PREFIJO}/{combo['id']}", json=_cuerpo(platos_ids=[plato_id], seccion_id=seccion_id)
    )
    invalido = cliente.put(
        f"{PREFIJO}/{combo['id']}", json=_cuerpo(platos_ids=[plato_id], seccion_id=999)
    )

    assert valido.status_code == 200
    assert valido.json()["seccion_id"] == seccion_id
    assert invalido.status_code == 422


def test_cat_s_28_un_combo_vigente_puede_cambiar_de_seccion(
    cliente, componentes, crear_seccion, persistir
):
    plato_id, *_ = componentes
    dos, tres = persistir(crear_seccion("Dos"), crear_seccion("Tres"))
    combo = cliente.post(PREFIJO, json=_cuerpo(platos_ids=[plato_id], seccion_id=dos)).json()

    respuesta = cliente.put(
        f"{PREFIJO}/{combo['id']}", json=_cuerpo(platos_ids=[plato_id], seccion_id=tres)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["seccion_id"] == tres


def test_cat_s_16_el_combo_vencido_409_tiene_prioridad_sobre_la_seccion_inexistente(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    plato_id, combo_id = persistir(plato, _combo_vencido(crear_combo, plato))

    respuesta = cliente.put(f"{PREFIJO}/{combo_id}", json=_cuerpo_vencido(plato_id, seccion_id=999))

    assert respuesta.status_code == 409


def test_cat_s_20_las_referencias_inexistentes_tienen_prioridad_sobre_componentes_inactivos(
    cliente, crear_plato, crear_bebida, crear_combo, persistir
):
    plato, bebida = crear_plato(), crear_bebida()
    bebida.dado_de_baja = True
    plato_id, bebida_id, combo_id = persistir(plato, bebida, crear_combo(platos=[plato]))

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}",
        json=_cuerpo(platos_ids=[plato_id, 999], bebidas_ids=[bebida_id]),
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["type"] == "componente_invalido"


@pytest.fixture
def combo_vencido_con_seccion(crear_plato, crear_combo, crear_seccion, persistir):
    """Combo vencido activo asignado a la sección 'Dos'; hay otra sección 'Tres'."""
    plato = crear_plato()
    dos, tres = persistir(crear_seccion("Dos"), crear_seccion("Tres"))
    combo = _combo_vencido(crear_combo, plato, seccion_id=dos)
    plato_id, combo_id = persistir(plato, combo)
    return plato_id, combo_id, dos, tres


def test_cat_s_22_cambiar_seccion_en_un_combo_vencido_responde_409(
    cliente, combo_vencido_con_seccion
):
    plato_id, combo_id, dos, tres = combo_vencido_con_seccion

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}", json=_cuerpo_vencido(plato_id, seccion_id=tres)
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"{PREFIJO}/{combo_id}").json()["seccion_id"] == dos


def test_cat_s_23_asignar_seccion_a_un_combo_vencido_sin_seccion_responde_409(
    cliente, crear_plato, crear_combo, crear_seccion, persistir
):
    plato = crear_plato()
    plato_id, combo_id, seccion_id = persistir(
        plato, _combo_vencido(crear_combo, plato), crear_seccion()
    )

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}", json=_cuerpo_vencido(plato_id, seccion_id=seccion_id)
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"{PREFIJO}/{combo_id}").json()["seccion_id"] is None


def test_cat_s_24_baja_de_combo_vencido_conservando_su_seccion_responde_200(
    cliente, combo_vencido_con_seccion
):
    plato_id, combo_id, dos, _ = combo_vencido_con_seccion

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}",
        json=_cuerpo_vencido(plato_id, dado_de_baja=True, seccion_id=dos),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert respuesta.json()["seccion_id"] == dos


def test_cat_s_25_baja_de_combo_vencido_omitiendo_la_seccion_responde_409(
    cliente, combo_vencido_con_seccion
):
    plato_id, combo_id, dos, _ = combo_vencido_con_seccion

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}", json=_cuerpo_vencido(plato_id, dado_de_baja=True)
    )

    assert respuesta.status_code == 409
    actual = cliente.get(f"{PREFIJO}/{combo_id}").json()
    assert actual["dado_de_baja"] is False
    assert actual["seccion_id"] == dos


def test_cat_s_26_baja_de_combo_vencido_sin_seccion_responde_200(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    plato_id, combo_id = persistir(plato, _combo_vencido(crear_combo, plato))

    respuesta = cliente.put(
        f"{PREFIJO}/{combo_id}", json=_cuerpo_vencido(plato_id, dado_de_baja=True)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert respuesta.json()["seccion_id"] is None


def test_cat_s_27_delete_de_combo_vencido_no_altera_la_seccion(
    cliente, combo_vencido_con_seccion
):
    _, combo_id, dos, _ = combo_vencido_con_seccion

    respuesta = cliente.delete(f"{PREFIJO}/{combo_id}")

    assert respuesta.status_code == 204
    actual = cliente.get(f"{PREFIJO}/{combo_id}").json()
    assert actual["dado_de_baja"] is True
    assert actual["seccion_id"] == dos
