import ast
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import Date, Integer, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import configure_mappers

from src.productos.models import Producto
from src.productos.registro import MenuDelDia, ProductoMenu


def test_mdd_01_mappers_se_configuran_con_la_nueva_entidad():
    configure_mappers()


def test_mdd_01_relacion_bidireccional(sesion, crear_menu_del_dia):
    menu = crear_menu_del_dia()
    registro = ProductoMenu(fecha=date(2026, 6, 15))
    registro.menu_del_dia = menu
    assert registro in menu.fechas

    otro = crear_menu_del_dia(nombre="Menú del martes")
    otra = ProductoMenu(fecha=date(2026, 6, 16))
    otro.fechas.append(otra)
    assert otra.menu_del_dia is otro

    sesion.add_all([menu, otro])
    sesion.commit()
    assert sesion.get(ProductoMenu, registro.id).menu_del_dia is menu


def test_mdd_03_menu_sin_fechas_tiene_coleccion_vacia(sesion, crear_menu_del_dia):
    menu = crear_menu_del_dia()
    sesion.add(menu)
    sesion.commit()

    assert menu.fechas == []


def test_fechas_del_menu_ordenadas_por_fecha(sesion, crear_menu_del_dia):
    menu = crear_menu_del_dia()
    sesion.add(menu)
    sesion.commit()
    sesion.add_all(
        [
            ProductoMenu(menu_del_dia_id=menu.id, fecha=date(2026, 6, 20)),
            ProductoMenu(menu_del_dia_id=menu.id, fecha=date(2026, 6, 10)),
        ]
    )
    sesion.commit()

    assert [r.fecha for r in menu.fechas] == [date(2026, 6, 10), date(2026, 6, 20)]


def test_tabla_producto_menu_con_las_columnas_del_diseno(motor):
    inspector = inspect(motor)
    assert "producto_menu" in inspector.get_table_names()

    columnas = {c["name"]: c for c in inspector.get_columns("producto_menu")}
    assert set(columnas) == {"id", "menu_del_dia_id", "fecha"}
    assert isinstance(columnas["id"]["type"], Integer)
    assert isinstance(columnas["menu_del_dia_id"]["type"], Integer)
    assert isinstance(columnas["fecha"]["type"], Date)
    assert columnas["menu_del_dia_id"]["nullable"] is False
    assert columnas["fecha"]["nullable"] is False


def test_menu_del_dia_id_y_fecha_son_obligatorios(sesion, crear_menu_del_dia):
    menu = crear_menu_del_dia()
    sesion.add(menu)
    sesion.commit()

    sesion.add(ProductoMenu(menu_del_dia_id=menu.id))
    with pytest.raises(IntegrityError):
        sesion.commit()
    sesion.rollback()

    sesion.add(ProductoMenu(fecha=date(2026, 6, 15)))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_fk_a_menu_del_dia_sin_clausula_on_delete(motor):
    claves = inspect(motor).get_foreign_keys("producto_menu")
    assert len(claves) == 1
    assert claves[0]["constrained_columns"] == ["menu_del_dia_id"]
    assert claves[0]["referred_table"] == "menu_del_dia"
    assert claves[0]["referred_columns"] == ["id"]
    assert not claves[0].get("options", {}).get("ondelete")


def test_indice_simple_sobre_menu_del_dia_id(motor):
    indices = inspect(motor).get_indexes("producto_menu")
    simples = [i for i in indices if i["column_names"] == ["menu_del_dia_id"]]
    assert len(simples) == 1
    assert not simples[0]["unique"]


def test_indice_ux_producto_menu_fecha_es_unico(motor):
    indices = {i["name"]: i for i in inspect(motor).get_indexes("producto_menu")}
    assert indices["ux_producto_menu_fecha"]["unique"]
    assert indices["ux_producto_menu_fecha"]["column_names"] == ["fecha"]


def test_indice_unico_rechaza_fecha_repetida(sesion, crear_menu_del_dia):
    uno, otro = crear_menu_del_dia(), crear_menu_del_dia(nombre="Otro")
    sesion.add_all([uno, otro])
    sesion.commit()
    sesion.add(ProductoMenu(menu_del_dia_id=uno.id, fecha=date(2026, 6, 15)))
    sesion.commit()

    sesion.add(ProductoMenu(menu_del_dia_id=otro.id, fecha=date(2026, 6, 15)))
    with pytest.raises(IntegrityError) as error:
        sesion.commit()
    assert "producto_menu.fecha" in str(error.value.orig)


def test_mdd_24_un_menu_con_varias_fechas(sesion, crear_menu_del_dia):
    menu = crear_menu_del_dia()
    sesion.add(menu)
    sesion.commit()
    sesion.add_all(
        [
            ProductoMenu(menu_del_dia_id=menu.id, fecha=date(2026, 6, 15)),
            ProductoMenu(menu_del_dia_id=menu.id, fecha=date(2026, 6, 16)),
        ]
    )
    sesion.commit()

    assert len(sesion.scalars(select(ProductoMenu)).all()) == 2
    assert {m.fecha for m in menu.fechas} == {date(2026, 6, 15), date(2026, 6, 16)}


def test_producto_menu_no_tiene_producto_id_ni_producto_no_tiene_menus_del_dia():
    assert not hasattr(ProductoMenu, "producto_id")
    assert not hasattr(Producto, "menus_del_dia")


def test_menu_del_dia_fechas_sin_cascada_delete():
    relacion = inspect(MenuDelDia).relationships["fechas"]
    assert "delete" not in relacion.cascade


def test_models_de_productos_menu_no_importa_productos():
    ruta = Path(__file__).parents[2] / "src" / "productos_menu" / "models.py"
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    modulos = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos += [a.name for a in nodo.names]
        elif isinstance(nodo, ast.ImportFrom):
            modulos.append(nodo.module or "")
    assert not [m for m in modulos if m == "src.productos" or m.startswith("src.productos.")]


def test_registro_expone_producto_menu():
    from src.productos import registro

    assert "ProductoMenu" in registro.__all__
    assert registro.ProductoMenu is ProductoMenu
