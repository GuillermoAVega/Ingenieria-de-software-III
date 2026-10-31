# Caracterización: el comportamiento existente de productos no cambia por el menú del día.
from datetime import date

from sqlalchemy import select

from src.productos_menu.models import ProductoMenu
from src.productos.platos.models import Plato

F1 = date(2026, 7, 1)
F2 = date(2026, 7, 2)


def test_pmd_37_la_baja_con_menu_del_dia_responde_igual_que_sin_menu(
    cliente, crear_plato, crear_producto_menu, persistir
):
    sin_menu = persistir(crear_plato(nombre="Sin menú"))
    con_menu_plato = crear_plato(nombre="Con menú")
    con_menu, _ = persistir(con_menu_plato, crear_producto_menu(con_menu_plato, F1))

    codigo_sin = cliente.delete(f"/productos/platos/{sin_menu}").status_code
    codigo_con = cliente.delete(f"/productos/platos/{con_menu}").status_code

    assert codigo_sin == codigo_con == 204
    assert cliente.get(f"/productos/platos/{con_menu}").json()["dado_de_baja"] is True


def test_pmd_38_los_registros_permanecen_tras_la_baja(
    cliente, sesion, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    plato_id, primero, segundo = persistir(
        plato, crear_producto_menu(plato, F1), crear_producto_menu(plato, F2)
    )

    assert cliente.delete(f"/productos/platos/{plato_id}").status_code == 204

    filas = set(
        sesion.execute(
            select(ProductoMenu.id, ProductoMenu.producto_id, ProductoMenu.fecha)
        ).all()
    )
    assert filas == {(primero, plato_id, F1), (segundo, plato_id, F2)}


def test_pmd_39_la_respuesta_de_producto_no_incluye_menus_del_dia(
    cliente, crear_plato, crear_producto_menu, persistir
):
    plato_sin = persistir(crear_plato(nombre="Sin menú"))
    plato = crear_plato(nombre="Con menú")
    plato_con, _ = persistir(plato, crear_producto_menu(plato, F1))

    sin_menu = cliente.get(f"/productos/platos/{plato_sin}").json()
    con_menu = cliente.get(f"/productos/platos/{plato_con}").json()

    assert set(con_menu) == set(sin_menu)
    assert "menus_del_dia" not in con_menu


def test_pmd_40_un_producto_con_dos_fechas_por_http_y_relacion(
    cliente, sesion, crear_plato, persistir
):
    plato_id = persistir(crear_plato())

    for fecha in (F1, F2):
        respuesta = cliente.post(
            "/productos-menu", json={"producto_id": plato_id, "fecha": fecha.isoformat()}
        )
        assert respuesta.status_code == 201

    plato = sesion.get(Plato, plato_id)
    assert {menu.fecha for menu in plato.menus_del_dia} == {F1, F2}
