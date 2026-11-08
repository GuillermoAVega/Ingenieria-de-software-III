from datetime import timedelta

PREFIJO = "/productos/menus-del-dia"


def _cuerpo(**cambios):
    return {"nombre": "Menú del lunes", "precio": "2500.00", **cambios}


def test_mdd_32_crear_responde_201_con_tipo_menu_del_dia(cliente):
    respuesta = cliente.post(PREFIJO, json=_cuerpo())

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert isinstance(cuerpo["id"], int)
    assert cuerpo["tipo"] == "menu_del_dia"
    assert cuerpo["dado_de_baja"] is False


def test_mdd_20_la_respuesta_no_contiene_fechas_ni_menus_del_dia(cliente):
    cuerpo = cliente.post(PREFIJO, json=_cuerpo()).json()

    assert "fechas" not in cuerpo
    assert "menus_del_dia" not in cuerpo


def test_mdd_33_crear_con_seccion_id(cliente, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion())

    respuesta = cliente.post(
        PREFIJO, json=_cuerpo(descripcion="Completo", imagen="m.png", seccion_id=seccion_id)
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["seccion_id"] == seccion_id
    assert respuesta.json()["descripcion"] == "Completo"


def test_mdd_34_seccion_inexistente_y_campos_invalidos_responden_422(cliente):
    assert cliente.post(PREFIJO, json=_cuerpo(seccion_id=999)).status_code == 422
    assert cliente.post(PREFIJO, json=_cuerpo(nombre="")).status_code == 422
    assert cliente.post(PREFIJO, json=_cuerpo(precio="0")).status_code == 422
    assert cliente.post(PREFIJO, json=_cuerpo(descripcion="x" * 501)).status_code == 422


def test_mdd_35_nombre_activo_duplicado_responde_409(cliente):
    assert cliente.post(PREFIJO, json=_cuerpo()).status_code == 201

    assert cliente.post(PREFIJO, json=_cuerpo(nombre=" MENÚ DEL LUNES ")).status_code == 409


def test_mdd_36_listado_solo_activos_por_id_ascendente(cliente, crear_menu_del_dia, persistir):
    inactivo = crear_menu_del_dia("Viejo")
    inactivo.dado_de_baja = True
    persistir(inactivo)
    a = cliente.post(PREFIJO, json=_cuerpo(nombre="A")).json()
    b = cliente.post(PREFIJO, json=_cuerpo(nombre="B")).json()

    respuesta = cliente.get(PREFIJO)

    assert respuesta.status_code == 200
    assert [m["id"] for m in respuesta.json()] == [a["id"], b["id"]]


def test_mdd_37_listado_vacio_con_otros_subtipos_presentes(cliente, crear_plato, persistir):
    persistir(crear_plato())
    cliente.post("/productos/postres", json={"nombre": "Flan", "precio": "600.00"})

    assert cliente.get(PREFIJO).json() == []


def test_mdd_38_get_de_un_menu_dado_de_baja_responde_200(cliente, crear_menu_del_dia, persistir):
    menu = crear_menu_del_dia()
    menu.dado_de_baja = True
    menu_id = persistir(menu)

    respuesta = cliente.get(f"{PREFIJO}/{menu_id}")

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True


def test_mdd_39_get_con_id_de_un_plato_o_inexistente_responde_404(cliente, crear_plato, persistir):
    plato_id = persistir(crear_plato())

    assert cliente.get(f"{PREFIJO}/{plato_id}").status_code == 404
    assert cliente.get(f"{PREFIJO}/999").status_code == 404


def test_mdd_40_put_es_reemplazo_completo(cliente):
    creado = cliente.post(
        PREFIJO, json=_cuerpo(descripcion="Completo", imagen="m.png")
    ).json()

    respuesta = cliente.put(f"{PREFIJO}/{creado['id']}", json=_cuerpo(precio="3000.00"))

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["precio"] == "3000.00"
    assert cuerpo["descripcion"] is None
    assert cuerpo["imagen"] is None
    assert cuerpo["seccion_id"] is None


def test_mdd_41_precio_invalido_en_put_a_id_desconocido_responde_422_antes_que_404(cliente):
    assert cliente.put(f"{PREFIJO}/999", json=_cuerpo(precio="0")).status_code == 422


def test_mdd_42_put_a_id_inexistente_responde_404(cliente):
    assert cliente.put(f"{PREFIJO}/999", json=_cuerpo()).status_code == 404


def test_mdd_43_put_con_seccion_valida_e_invalida(cliente, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion())
    creado = cliente.post(PREFIJO, json=_cuerpo()).json()

    ok = cliente.put(f"{PREFIJO}/{creado['id']}", json=_cuerpo(seccion_id=seccion_id))
    mal = cliente.put(f"{PREFIJO}/{creado['id']}", json=_cuerpo(seccion_id=999))

    assert ok.status_code == 200
    assert ok.json()["seccion_id"] == seccion_id
    assert mal.status_code == 422


def test_mdd_31_cada_ruta_responde_solo_en_la_suya(cliente, crear_plato, crear_postre, persistir):
    menu = cliente.post(PREFIJO, json=_cuerpo()).json()
    plato_id, postre_id = persistir(crear_plato(), crear_postre())
    ejecutivo = cliente.post(
        "/productos/menus-ejecutivos",
        json={"nombre": "Ejecutivo", "precio": "2000.00", "plato_id": plato_id, "postre_id": postre_id},
    ).json()

    assert cliente.get(f"/productos/menus-ejecutivos/{menu['id']}").status_code == 404
    assert cliente.get(f"{PREFIJO}/{ejecutivo['id']}").status_code == 404
    assert [m["id"] for m in cliente.get(PREFIJO).json()] == [menu["id"]]


def test_baja_por_delete_responde_204_y_deja_el_menu_dado_de_baja(cliente):
    creado = cliente.post(PREFIJO, json=_cuerpo()).json()

    assert cliente.delete(f"{PREFIJO}/{creado['id']}").status_code == 204
    assert cliente.get(f"{PREFIJO}/{creado['id']}").json()["dado_de_baja"] is True


def test_mdd_listado_incluye_proxima_fecha_desde_hoy(
    cliente, crear_menu_del_dia, crear_producto_menu, persistir, HOY
):
    con_fechas = crear_menu_del_dia("Con fechas")
    for dias in (-1, 5, 0):
        crear_producto_menu(con_fechas, HOY + timedelta(days=dias))
    solo_pasadas = crear_menu_del_dia("Solo pasadas")
    crear_producto_menu(solo_pasadas, HOY - timedelta(days=3))
    sin_fechas = crear_menu_del_dia("Sin fechas")
    for menu in (con_fechas, solo_pasadas, sin_fechas):
        persistir(menu)

    proximas = {m["nombre"]: m["proxima_fecha"] for m in cliente.get(PREFIJO).json()}

    assert proximas == {
        "Con fechas": HOY.isoformat(),
        "Solo pasadas": None,
        "Sin fechas": None,
    }
