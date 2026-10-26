from decimal import Decimal

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import class_mapper, configure_mappers

from src.productos.bebidas.models import Bebida
from src.productos.combos.models import ComboPromocion
from src.productos.constants import (
    TIPO_BEBIDA,
    TIPO_MAX,
    TIPO_PLATO,
    TIPO_POSTRE,
)
from src.productos.menus_ejecutivos.models import MenuEjecutivo
from src.productos.models import Producto
from src.productos.platos.models import Plato
from src.productos.postres.models import Postre


def test_instanciacion_directa_rechazada():
    with pytest.raises(TypeError):
        Producto(nombre="X", nombre_normalizado="x", precio=Decimal("1.00"))


def test_create_all_crea_tablas_con_columnas_del_diseno(motor):
    inspector = inspect(motor)
    tablas = set(inspector.get_table_names())
    assert {"producto", "plato", "bebida", "postre"} <= tablas

    columnas_producto = {c["name"]: c for c in inspector.get_columns("producto")}
    assert set(columnas_producto) == {
        "id", "tipo", "nombre", "nombre_normalizado", "precio",
        "descripcion", "imagen", "dado_de_baja",
    }
    for obligatoria in ("tipo", "nombre", "nombre_normalizado", "precio", "dado_de_baja"):
        assert columnas_producto[obligatoria]["nullable"] is False
    for opcional in ("descripcion", "imagen"):
        assert columnas_producto[opcional]["nullable"] is True
    assert columnas_producto["tipo"]["type"].length == TIPO_MAX

    assert {c["name"] for c in inspector.get_columns("plato")} == {"id", "cant_personas"}
    assert {c["name"] for c in inspector.get_columns("bebida")} == {"id", "es_alcoholica"}
    assert {c["name"] for c in inspector.get_columns("postre")} == {"id"}


def test_persistir_y_releer_con_el_tipo_correcto(
    sesion, crear_plato, crear_bebida, crear_postre
):
    sesion.add_all([crear_plato(), crear_bebida(), crear_postre()])
    sesion.commit()
    sesion.expunge_all()

    productos = sesion.scalars(select(Producto).order_by(Producto.id)).all()
    assert [type(p) for p in productos] == [Plato, Bebida, Postre]
    assert [p.tipo for p in productos] == [TIPO_PLATO, TIPO_BEBIDA, TIPO_POSTRE]
    assert productos[0].cant_personas == 2
    assert productos[1].es_alcoholica is True
    assert productos[0].precio == Decimal("1500.00")
    assert productos[0].dado_de_baja is False


def test_check_precio_positivo_rechazado_por_la_bd(sesion, crear_postre):
    sesion.add(crear_postre(precio="0.00"))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_indice_parcial_existe(motor):
    indices = {i["name"]: i for i in inspect(motor).get_indexes("producto")}
    assert "ux_producto_nombre_activo" in indices
    assert indices["ux_producto_nombre_activo"]["unique"]
    assert indices["ux_producto_nombre_activo"]["column_names"] == ["nombre_normalizado"]


def test_indice_parcial_rechaza_dos_activos_con_igual_nombre_normalizado(
    sesion, crear_plato, crear_bebida
):
    sesion.add(crear_plato(nombre="Pizza"))
    sesion.commit()
    sesion.add(crear_bebida(nombre="PIZZA"))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_reutilizacion_del_nombre_tras_la_baja_permitida(sesion, crear_plato):
    primero = crear_plato(nombre="Pizza")
    sesion.add(primero)
    sesion.commit()
    primero.dado_de_baja = True
    sesion.commit()

    sesion.add(crear_plato(nombre="Pizza"))
    sesion.commit()

    cantidad = len(sesion.scalars(select(Producto)).all())
    assert cantidad == 2


def test_los_mappers_se_configuran_con_los_cinco_subtipos():
    configure_mappers()

    for subtipo in (Plato, Bebida, Postre, MenuEjecutivo, ComboPromocion):
        class_mapper(subtipo)
