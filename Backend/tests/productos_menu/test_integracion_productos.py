# Integración: el menú del día referencia a un MenuDelDia y no altera a los demás productos.
from datetime import date

from sqlalchemy import select

from src.productos.menus_del_dia.models import MenuDelDia
from src.productos_menu.models import ProductoMenu

F1 = date(2026, 7, 1)
F2 = date(2026, 7, 2)


def test_la_baja_de_un_plato_no_depende_de_los_menus_del_dia(
    cliente, crear_plato, crear_menu_del_dia, crear_producto_menu, persistir
):
    menu = crear_menu_del_dia()
    persistir(menu, crear_producto_menu(menu, F1))
    plato_id = persistir(crear_plato())

    assert cliente.delete(f"/productos/platos/{plato_id}").status_code == 204


def test_los_registros_permanecen_tras_la_baja_de_un_menu_sin_fechas_vigentes(
    cliente, sesion, crear_menu_del_dia, crear_producto_menu, persistir
):
    menu = crear_menu_del_dia()
    menu_id, primero = persistir(menu, crear_producto_menu(menu, date(2026, 6, 1)))

    assert cliente.delete(f"/productos/menus-del-dia/{menu_id}").status_code == 204

    filas = set(
        sesion.execute(
            select(ProductoMenu.id, ProductoMenu.menu_del_dia_id, ProductoMenu.fecha)
        ).all()
    )
    assert filas == {(primero, menu_id, date(2026, 6, 1))}


def test_un_menu_con_dos_fechas_por_http_y_relacion(
    cliente, sesion, crear_menu_del_dia, persistir
):
    menu_id = persistir(crear_menu_del_dia())

    for fecha in (F1, F2):
        respuesta = cliente.post(
            "/productos-menu", json={"menu_del_dia_id": menu_id, "fecha": fecha.isoformat()}
        )
        assert respuesta.status_code == 201

    menu = sesion.get(MenuDelDia, menu_id)
    assert [registro.fecha for registro in menu.fechas] == [F1, F2]
