from datetime import date

from sqlalchemy import select

from src.productos.registro import ProductoMenu


def test_fabrica_crear_producto_menu_persiste_con_fecha_explicita(
    sesion, crear_menu_del_dia, crear_producto_menu
):
    menu = crear_menu_del_dia()
    sesion.add(menu)
    sesion.commit()

    registro = crear_producto_menu(menu, date(2026, 6, 15))
    sesion.add(registro)
    sesion.commit()

    guardado = sesion.scalars(select(ProductoMenu)).one()
    assert guardado.menu_del_dia_id == menu.id
    assert guardado.fecha == date(2026, 6, 15)


def test_fabrica_sin_fecha_usa_fechas_consecutivas_desde_2100(crear_menu_del_dia, crear_producto_menu):
    menu = crear_menu_del_dia()

    primero = crear_producto_menu(menu)
    segundo = crear_producto_menu(menu)

    assert primero.fecha == date(2100, 1, 1)
    assert segundo.fecha == date(2100, 1, 2)


def test_fabrica_dos_llamadas_sin_fecha_no_violan_el_indice_unico(
    sesion, crear_menu_del_dia, crear_producto_menu
):
    menu = crear_menu_del_dia()
    sesion.add(menu)
    sesion.add_all([crear_producto_menu(menu), crear_producto_menu(menu)])
    sesion.commit()

    assert len(sesion.scalars(select(ProductoMenu)).all()) == 2
