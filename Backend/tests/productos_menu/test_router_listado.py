from datetime import date

URL = "/productos-menu"
F1 = date(2026, 7, 1)
F2 = date(2026, 7, 2)
F3 = date(2026, 7, 3)

CLAVES = {
    "id",
    "menu_del_dia_id",
    "fecha",
    "menu_del_dia_nombre",
    "menu_del_dia_dado_de_baja",
}


def test_pmd_41_listado_vacio_devuelve_lista_vacia(cliente):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_pmd_42_listado_ordenado_por_fecha_descendente(
    cliente, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia()
    persistir(
        mdd,
        crear_producto_menu(mdd, F1),
        crear_producto_menu(mdd, F2),
        crear_producto_menu(mdd, F3),
    )

    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert [item["fecha"] for item in respuesta.json()] == [
        "2026-07-03",
        "2026-07-02",
        "2026-07-01",
    ]


def test_pmd_43_el_listado_incluye_los_datos_del_menu_del_dia(
    cliente, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia(nombre="Milanesa")
    menu_del_dia_id, menu_id = persistir(mdd, crear_producto_menu(mdd, F1))

    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {
            "id": menu_id,
            "menu_del_dia_id": menu_del_dia_id,
            "fecha": "2026-07-01",
            "menu_del_dia_nombre": "Milanesa",
            "menu_del_dia_dado_de_baja": False,
        }
    ]


def test_pmd_44_el_listado_incluye_productos_dados_de_baja(
    cliente, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia()
    mdd.dado_de_baja = True
    persistir(mdd, crear_producto_menu(mdd, F1))

    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.json()[0]["menu_del_dia_dado_de_baja"] is True


def test_pmd_45_el_item_expone_exactamente_las_cinco_claves(
    cliente, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia()
    persistir(mdd, crear_producto_menu(mdd, F1))

    respuesta = cliente.get(URL)

    assert set(respuesta.json()[0]) == CLAVES


def test_pmd_46_obtener_por_id_devuelve_el_detalle(
    cliente, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia(nombre="Milanesa")
    menu_del_dia_id, menu_id = persistir(mdd, crear_producto_menu(mdd, F1))

    respuesta = cliente.get(f"{URL}/{menu_id}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": menu_id,
        "menu_del_dia_id": menu_del_dia_id,
        "fecha": "2026-07-01",
        "menu_del_dia_nombre": "Milanesa",
        "menu_del_dia_dado_de_baja": False,
    }


def test_pmd_47_obtener_un_id_inexistente_responde_404(cliente):
    respuesta = cliente.get(f"{URL}/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Menú del día no encontrado"}
