"""Regla de baja de MenuDelDia: se borran físicamente las fechas `> hoy` (servicios)."""
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from src.productos import services
from src.productos.menus_del_dia import services as servicios_menus_del_dia
from src.productos.menus_del_dia.models import MenuDelDia
from src.productos.menus_del_dia.schemas import MenuDelDiaActualizar
from src.productos.platos.models import Plato
from src.productos_menu.models import ProductoMenu

HOY = date(2026, 6, 15)
AYER = date(2026, 6, 14)
MANANA = date(2026, 6, 16)


def _fechas(sesion):
    resultado = list(sesion.scalars(select(ProductoMenu.fecha).order_by(ProductoMenu.fecha)))
    sesion.rollback()
    return resultado


def _baja(sesion, menu_id, hoy=HOY):
    services.dar_de_baja(sesion, MenuDelDia, menu_id, hoy)


def _put_baja(sesion, menu_id, hoy=HOY, **cambios):
    datos = {"nombre": "Menú del lunes", "precio": Decimal("2500.00"), "dado_de_baja": True}
    datos.update(cambios)
    return servicios_menus_del_dia.actualizar_menu_del_dia(
        sesion, menu_id, MenuDelDiaActualizar(**datos), hoy
    )


def _menu_con(persistir, crear_menu_del_dia, crear_producto_menu, *fechas):
    menu = crear_menu_del_dia()
    ids = persistir(menu, *(crear_producto_menu(menu, f) for f in fechas))
    return ids[0] if fechas else ids


def test_baja_con_fechas_futuras_las_borra_y_conserva_las_de_hoy_y_anteriores(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    menu_id = _menu_con(
        persistir, crear_menu_del_dia, crear_producto_menu, date(2026, 7, 10), AYER, HOY, MANANA
    )

    _baja(sesion, menu_id)

    assert sesion.get(MenuDelDia, menu_id).dado_de_baja is True
    assert _fechas(sesion) == [AYER, HOY]


def test_put_con_dado_de_baja_true_tambien_borra_las_fechas_futuras(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    menu_id = _menu_con(persistir, crear_menu_del_dia, crear_producto_menu, AYER, MANANA)

    menu = _put_baja(sesion, menu_id)

    assert menu.dado_de_baja is True
    assert _fechas(sesion) == [AYER]


def test_solo_fechas_pasadas_permite_la_baja_y_conserva_el_historial(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    menu_id = _menu_con(persistir, crear_menu_del_dia, crear_producto_menu, AYER, date(2026, 6, 1))

    _baja(sesion, menu_id)

    assert sesion.get(MenuDelDia, menu_id).dado_de_baja is True
    assert _fechas(sesion) == [date(2026, 6, 1), AYER]


def test_sin_fechas_permite_la_baja_por_delete_y_por_put(sesion, persistir, crear_menu_del_dia):
    uno = persistir(crear_menu_del_dia())
    otro = persistir(crear_menu_del_dia(nombre="Otro"))

    _baja(sesion, uno)
    _put_baja(sesion, otro, nombre="Otro")

    assert sesion.get(MenuDelDia, uno).dado_de_baja is True
    assert sesion.get(MenuDelDia, otro).dado_de_baja is True


def test_el_limite_depende_de_hoy(sesion, persistir, crear_menu_del_dia, crear_producto_menu):
    menu_id = _menu_con(persistir, crear_menu_del_dia, crear_producto_menu, MANANA)

    _baja(sesion, menu_id, hoy=MANANA)

    assert _fechas(sesion) == [MANANA]


def test_la_baja_repetida_es_idempotente(sesion, persistir, crear_menu_del_dia, crear_producto_menu):
    menu_id = _menu_con(persistir, crear_menu_del_dia, crear_producto_menu, AYER)

    _baja(sesion, menu_id)
    _baja(sesion, menu_id)

    assert sesion.get(MenuDelDia, menu_id).dado_de_baja is True
    assert _fechas(sesion) == [AYER]


def test_la_baja_no_toca_fechas_de_otros_menus(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    menu_id = _menu_con(persistir, crear_menu_del_dia, crear_producto_menu, MANANA)
    otro = crear_menu_del_dia(nombre="Otro")
    persistir(otro, crear_producto_menu(otro, date(2026, 7, 1)))

    _baja(sesion, menu_id)

    assert _fechas(sesion) == [date(2026, 7, 1)]


def test_otros_subtipos_se_dan_de_baja_sin_tocar_fechas(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu, crear_plato, crear_bebida, crear_postre
):
    menu = crear_menu_del_dia()
    persistir(menu, crear_producto_menu(menu, MANANA))
    plato, bebida, postre = crear_plato(), crear_bebida(), crear_postre()
    ids = persistir(plato, bebida, postre)

    for modelo, producto_id in zip((Plato, type(bebida), type(postre)), ids):
        services.dar_de_baja(sesion, modelo, producto_id, HOY)
        assert sesion.get(modelo, producto_id).dado_de_baja is True
    assert _fechas(sesion) == [MANANA]
