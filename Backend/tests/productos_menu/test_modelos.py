import ast
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import Date, Integer, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import configure_mappers

from src.productos.registro import Plato, ProductoMenu
from src.productos.models import Producto


def test_pmd_01_mappers_se_configuran_con_la_nueva_entidad():
    configure_mappers()


def test_pmd_02_relacion_bidireccional(sesion, crear_plato):
    plato = crear_plato()
    registro = ProductoMenu(fecha=date(2026, 6, 15))
    registro.producto = plato
    assert registro in plato.menus_del_dia

    otro = crear_plato(nombre="Pizza")
    otra = ProductoMenu(fecha=date(2026, 6, 16))
    otro.menus_del_dia.append(otra)
    assert otra.producto is otro

    sesion.add_all([plato, otro])
    sesion.commit()
    assert sesion.get(ProductoMenu, registro.id).producto is plato


def test_tabla_producto_menu_con_las_columnas_del_diseno(motor):
    inspector = inspect(motor)
    assert "producto_menu" in inspector.get_table_names()

    columnas = {c["name"]: c for c in inspector.get_columns("producto_menu")}
    assert set(columnas) == {"id", "producto_id", "fecha"}
    assert isinstance(columnas["id"]["type"], Integer)
    assert isinstance(columnas["producto_id"]["type"], Integer)
    assert isinstance(columnas["fecha"]["type"], Date)
    assert columnas["producto_id"]["nullable"] is False
    assert columnas["fecha"]["nullable"] is False


def test_producto_id_y_fecha_son_obligatorios(sesion, crear_plato):
    plato = crear_plato()
    sesion.add(plato)
    sesion.commit()

    sesion.add(ProductoMenu(producto_id=plato.id))
    with pytest.raises(IntegrityError):
        sesion.commit()
    sesion.rollback()

    sesion.add(ProductoMenu(fecha=date(2026, 6, 15)))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_fk_a_producto_sin_clausula_on_delete(motor):
    claves = inspect(motor).get_foreign_keys("producto_menu")
    assert len(claves) == 1
    assert claves[0]["constrained_columns"] == ["producto_id"]
    assert claves[0]["referred_table"] == "producto"
    assert claves[0]["referred_columns"] == ["id"]
    assert not claves[0].get("options", {}).get("ondelete")


def test_indice_simple_sobre_producto_id(motor):
    indices = inspect(motor).get_indexes("producto_menu")
    simples = [i for i in indices if i["column_names"] == ["producto_id"]]
    assert len(simples) == 1
    assert not simples[0]["unique"]


def test_indice_ux_producto_menu_fecha_es_unico(motor):
    indices = {i["name"]: i for i in inspect(motor).get_indexes("producto_menu")}
    assert indices["ux_producto_menu_fecha"]["unique"]
    assert indices["ux_producto_menu_fecha"]["column_names"] == ["fecha"]


def test_pmd_15_indice_unico_rechaza_fecha_repetida(sesion, crear_plato, crear_postre):
    plato, postre = crear_plato(), crear_postre()
    sesion.add_all([plato, postre])
    sesion.commit()
    sesion.add(ProductoMenu(producto_id=plato.id, fecha=date(2026, 6, 15)))
    sesion.commit()

    sesion.add(ProductoMenu(producto_id=postre.id, fecha=date(2026, 6, 15)))
    with pytest.raises(IntegrityError) as error:
        sesion.commit()
    assert "producto_menu.fecha" in str(error.value.orig)


def test_pmd_40_un_producto_con_varias_fechas(sesion, crear_plato):
    plato = crear_plato()
    sesion.add(plato)
    sesion.commit()
    sesion.add_all(
        [
            ProductoMenu(producto_id=plato.id, fecha=date(2026, 6, 15)),
            ProductoMenu(producto_id=plato.id, fecha=date(2026, 6, 16)),
        ]
    )
    sesion.commit()

    assert len(sesion.scalars(select(ProductoMenu)).all()) == 2
    assert {m.fecha for m in plato.menus_del_dia} == {date(2026, 6, 15), date(2026, 6, 16)}


def test_producto_menus_del_dia_sin_cascada_delete():
    relacion = inspect(Producto).relationships["menus_del_dia"]
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
