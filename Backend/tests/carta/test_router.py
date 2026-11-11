def test_carta_reune_todos_los_listados_en_una_respuesta(cliente):
    respuesta = cliente.get("/carta")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "menus_diarios": [],
        "menus_del_dia": [],
        "menus_ejecutivos": [],
        "combos": [],
        "platos": [],
        "postres": [],
        "bebidas": [],
        "secciones": [],
        "promociones": [],
    }
