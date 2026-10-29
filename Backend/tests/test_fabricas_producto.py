def test_fabricas_producto_disponibles_fuera_de_tests_productos(
    crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo, persistir
):
    plato = crear_plato()
    postre = crear_postre()
    bebida = crear_bebida()
    menu = crear_menu(plato, postre)
    combo = crear_combo(platos=[plato])

    ids = persistir(plato, postre, bebida, menu, combo)

    assert len(ids) == 5
    assert all(isinstance(identificador, int) for identificador in ids)
