from decimal import Decimal

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from src.productos.registro import Plato, Seccion
from src.secciones.constants import NOMBRE_MAX, SUBTITULO_MAX


def test_create_all_crea_la_tabla_seccion_con_las_columnas_del_diseno(motor):
    inspector = inspect(motor)
    assert "seccion" in inspector.get_table_names()

    columnas = {c["name"]: c for c in inspector.get_columns("seccion")}
    assert set(columnas) == {"id", "nombre", "nombre_normalizado", "subtitulo"}
    assert columnas["nombre"]["nullable"] is False
    assert columnas["nombre_normalizado"]["nullable"] is False
    assert columnas["subtitulo"]["nullable"] is True
    assert columnas["nombre"]["type"].length == NOMBRE_MAX
    assert columnas["nombre_normalizado"]["type"].length == NOMBRE_MAX
    assert columnas["subtitulo"]["type"].length == SUBTITULO_MAX


def test_indice_unico_rechaza_dos_secciones_con_el_mismo_nombre_normalizado(sesion):
    sesion.add(Seccion(nombre="Entradas", nombre_normalizado="entradas"))
    sesion.commit()

    sesion.add(Seccion(nombre="ENTRADAS", nombre_normalizado="entradas"))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_indice_ux_seccion_nombre_normalizado_es_unico(motor):
    indices = {i["name"]: i for i in inspect(motor).get_indexes("seccion")}
    assert indices["ux_seccion_nombre_normalizado"]["unique"]
    assert indices["ux_seccion_nombre_normalizado"]["column_names"] == ["nombre_normalizado"]


def test_producto_tiene_seccion_id_anulable_con_fk_set_null(motor):
    inspector = inspect(motor)
    columnas = {c["name"]: c for c in inspector.get_columns("producto")}
    assert columnas["seccion_id"]["nullable"] is True

    fks = [
        fk for fk in inspector.get_foreign_keys("producto")
        if fk["constrained_columns"] == ["seccion_id"]
    ]
    assert len(fks) == 1
    assert fks[0]["referred_table"] == "seccion"
    assert fks[0]["referred_columns"] == ["id"]
    assert fks[0]["options"]["ondelete"] == "SET NULL"


def _plato():
    return Plato(
        nombre="Milanesa",
        nombre_normalizado="milanesa",
        precio=Decimal("1500.00"),
        cant_personas=2,
    )


def test_relacion_bidireccional_asignando_desde_el_producto(sesion):
    seccion = Seccion(nombre="Entradas", nombre_normalizado="entradas")
    plato = _plato()
    plato.seccion = seccion
    sesion.add_all([seccion, plato])
    sesion.commit()

    assert seccion.productos == [plato]
    assert plato.seccion_id == seccion.id


def test_relacion_bidireccional_asignando_desde_la_seccion(sesion):
    seccion = Seccion(nombre="Entradas", nombre_normalizado="entradas")
    plato = _plato()
    seccion.productos.append(plato)
    sesion.add(seccion)
    sesion.commit()

    assert plato.seccion is seccion
    assert plato.seccion_id == seccion.id
