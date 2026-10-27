from datetime import date, timedelta

from src.productos.services import buscar_bloqueantes


def _persistir(sesion, *objetos):
    sesion.add_all(objetos)
    sesion.commit()
    return objetos


def test_ld_10_plato_en_un_menu_activo_es_bloqueado_por_ese_menu(
    sesion, crear_plato, crear_postre, crear_menu, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    _persistir(sesion, plato, postre, menu)

    assert buscar_bloqueantes(sesion, plato, HOY) == [menu.id]


def test_ld_11_bebida_en_un_combo_activo_vigente_es_bloqueada_por_ese_combo(
    sesion, crear_bebida, crear_combo, HOY
):
    bebida = crear_bebida()
    combo = crear_combo(bebidas=[bebida], hasta=HOY + timedelta(days=5))
    _persistir(sesion, bebida, combo)

    assert buscar_bloqueantes(sesion, bebida, HOY) == [combo.id]


def test_ld_12_postre_en_un_combo_futuro_es_bloqueado(sesion, crear_postre, crear_combo, HOY):
    postre = crear_postre()
    combo = crear_combo(
        postres=[postre], desde=HOY + timedelta(days=10), hasta=HOY + timedelta(days=20)
    )
    _persistir(sesion, postre, combo)

    assert buscar_bloqueantes(sesion, postre, HOY) == [combo.id]


def test_ld_13_multiples_bloqueantes_se_devuelven_ordenados(
    sesion, crear_plato, crear_postre, crear_menu, crear_combo, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    combo = crear_combo(platos=[plato], hasta=HOY + timedelta(days=5))
    _persistir(sesion, plato, postre, menu, combo)

    assert buscar_bloqueantes(sesion, plato, HOY) == sorted([menu.id, combo.id])


def test_ld_14_menu_dado_de_baja_y_combo_vencido_no_bloquean(
    sesion, crear_plato, crear_postre, crear_menu, crear_combo, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    menu.dado_de_baja = True
    combo = crear_combo(
        platos=[plato], desde=HOY - timedelta(days=30), hasta=HOY - timedelta(days=1)
    )
    _persistir(sesion, plato, postre, menu, combo)

    assert buscar_bloqueantes(sesion, plato, HOY) == []


def test_ld_14_combo_dado_de_baja_no_bloquea(sesion, crear_bebida, crear_combo, HOY):
    bebida = crear_bebida()
    combo = crear_combo(bebidas=[bebida], hasta=HOY + timedelta(days=5))
    combo.dado_de_baja = True
    _persistir(sesion, bebida, combo)

    assert buscar_bloqueantes(sesion, bebida, HOY) == []


def test_ld_15_combo_activo_vencido_no_bloquea(sesion, crear_bebida, crear_combo, HOY):
    bebida = crear_bebida()
    combo = crear_combo(
        bebidas=[bebida], desde=HOY - timedelta(days=30), hasta=HOY - timedelta(days=1)
    )
    _persistir(sesion, bebida, combo)

    assert buscar_bloqueantes(sesion, bebida, HOY) == []


def test_combo_con_fecha_hasta_igual_a_hoy_bloquea(sesion, crear_bebida, crear_combo, HOY):
    bebida = crear_bebida()
    combo = crear_combo(bebidas=[bebida], desde=HOY - timedelta(days=5), hasta=HOY)
    _persistir(sesion, bebida, combo)

    assert buscar_bloqueantes(sesion, bebida, HOY) == [combo.id]


def test_los_componentes_ajenos_no_bloquean(
    sesion, crear_plato, crear_postre, crear_menu, crear_combo, HOY
):
    plato, otro_plato, postre = crear_plato(), crear_plato(nombre="Pizza"), crear_postre()
    menu = crear_menu(otro_plato, postre)
    combo = crear_combo(platos=[otro_plato], hasta=HOY + timedelta(days=5))
    _persistir(sesion, plato, otro_plato, postre, menu, combo)

    assert buscar_bloqueantes(sesion, plato, HOY) == []


def test_postre_en_un_menu_activo_es_bloqueado_por_ese_menu(
    sesion, crear_plato, crear_postre, crear_menu, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    _persistir(sesion, plato, postre, menu)

    assert buscar_bloqueantes(sesion, postre, HOY) == [menu.id]


def test_los_compuestos_no_tienen_restriccion(
    sesion, crear_plato, crear_postre, crear_menu, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    _persistir(sesion, plato, postre, menu)

    assert buscar_bloqueantes(sesion, menu, HOY) == []
