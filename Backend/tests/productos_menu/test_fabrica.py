from datetime import date

from sqlalchemy import select

from src.productos.registro import ProductoMenu


def test_fabrica_crear_producto_menu_persiste_con_fecha_explicita(
    sesion, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    sesion.add(plato)
    sesion.commit()

    registro = crear_producto_menu(plato, date(2026, 6, 15))
    sesion.add(registro)
    sesion.commit()

    guardado = sesion.scalars(select(ProductoMenu)).one()
    assert guardado.producto_id == plato.id
    assert guardado.fecha == date(2026, 6, 15)


def test_fabrica_sin_fecha_usa_fechas_consecutivas_desde_2100(crear_plato, crear_producto_menu):
    plato = crear_plato()

    primero = crear_producto_menu(plato)
    segundo = crear_producto_menu(plato)

    assert primero.fecha == date(2100, 1, 1)
    assert segundo.fecha == date(2100, 1, 2)


def test_fabrica_dos_llamadas_sin_fecha_no_violan_el_indice_unico(
    sesion, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    sesion.add(plato)
    sesion.add_all([crear_producto_menu(plato), crear_producto_menu(plato)])
    sesion.commit()

    assert len(sesion.scalars(select(ProductoMenu)).all()) == 2
