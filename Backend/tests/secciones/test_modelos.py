import re
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import Integer, event, inspect
from sqlalchemy.exc import IntegrityError

from src.productos.registro import (
    Bebida,
    ComboPromocion,
    MenuEjecutivo,
    Plato,
    Postre,
    Seccion,
)
from src.secciones.constants import NOMBRE_MAX, SUBTITULO_MAX


def test_create_all_crea_la_tabla_seccion_con_las_columnas_del_diseno(motor):
    inspector = inspect(motor)
    assert "seccion" in inspector.get_table_names()

    columnas = {c["name"]: c for c in inspector.get_columns("seccion")}
    assert set(columnas) == {"id", "nombre", "nombre_normalizado", "subtitulo", "posicion"}
    assert columnas["nombre"]["nullable"] is False
    assert columnas["nombre_normalizado"]["nullable"] is False
    assert columnas["subtitulo"]["nullable"] is True
    assert columnas["posicion"]["nullable"] is False
    assert isinstance(columnas["posicion"]["type"], Integer)
    assert columnas["nombre"]["type"].length == NOMBRE_MAX
    assert columnas["nombre_normalizado"]["type"].length == NOMBRE_MAX
    assert columnas["subtitulo"]["type"].length == SUBTITULO_MAX


def test_indice_unico_rechaza_dos_secciones_con_el_mismo_nombre_normalizado(sesion):
    sesion.add(Seccion(nombre="Entradas", nombre_normalizado="entradas", posicion=1))
    sesion.commit()

    sesion.add(Seccion(nombre="ENTRADAS", nombre_normalizado="entradas", posicion=2))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_indice_ux_seccion_nombre_normalizado_es_unico(motor):
    indices = {i["name"]: i for i in inspect(motor).get_indexes("seccion")}
    assert indices["ux_seccion_nombre_normalizado"]["unique"]
    assert indices["ux_seccion_nombre_normalizado"]["column_names"] == ["nombre_normalizado"]


def test_pos_11_indice_unico_rechaza_posicion_repetida(sesion):
    sesion.add(Seccion(nombre="Entradas", nombre_normalizado="entradas", posicion=1))
    sesion.commit()

    sesion.add(Seccion(nombre="Postres", nombre_normalizado="postres", posicion=1))
    with pytest.raises(IntegrityError) as error:
        sesion.commit()
    assert "seccion.posicion" in str(error.value.orig)


def test_indice_ux_seccion_posicion_es_unico(motor):
    indices = {i["name"]: i for i in inspect(motor).get_indexes("seccion")}
    assert indices["ux_seccion_posicion"]["unique"]
    assert indices["ux_seccion_posicion"]["column_names"] == ["posicion"]


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
    seccion = Seccion(nombre="Entradas", nombre_normalizado="entradas", posicion=1)
    plato = _plato()
    plato.seccion = seccion
    sesion.add_all([seccion, plato])
    sesion.commit()

    assert seccion.productos == [plato]
    assert plato.seccion_id == seccion.id


def test_relacion_bidireccional_asignando_desde_la_seccion(sesion):
    seccion = Seccion(nombre="Entradas", nombre_normalizado="entradas", posicion=1)
    plato = _plato()
    seccion.productos.append(plato)
    sesion.add(seccion)
    sesion.commit()

    assert plato.seccion is seccion
    assert plato.seccion_id == seccion.id


# --- Seccion.productos_ids ---


def _producto(clase, nombre, **cambios):
    return clase(
        nombre=nombre,
        nombre_normalizado=nombre.lower(),
        precio=Decimal("1500.00"),
        **cambios,
    )


def _seccion_con(sesion, *productos):
    seccion = Seccion(nombre="Entradas", nombre_normalizado="entradas", posicion=1)
    seccion.productos.extend(productos)
    sesion.add(seccion)
    sesion.commit()
    return seccion


def test_ids_02_seccion_sin_productos_devuelve_lista_vacia_en_el_modelo(sesion):
    sin_productos = _seccion_con(sesion)
    con_producto = Seccion(nombre="Postres", nombre_normalizado="postres", posicion=2)
    con_producto.productos.append(_producto(Plato, "Milanesa", cant_personas=2))
    sesion.add(con_producto)
    sesion.commit()

    assert sin_productos.productos_ids == []
    assert con_producto.productos_ids == [con_producto.productos[0].id]


def test_ids_06_modelo_incluye_solo_productos_activos(sesion):
    plato = _producto(Plato, "Milanesa", cant_personas=2)
    bebida = _producto(Bebida, "Cerveza", es_alcoholica=True, dado_de_baja=True)
    postre = _producto(Postre, "Flan")
    seccion = _seccion_con(sesion, plato, bebida, postre)

    assert seccion.productos_ids == [plato.id, postre.id]
    assert bebida.id not in seccion.productos_ids


def test_ids_07_modelo_con_solo_productos_dados_de_baja_devuelve_lista_vacia(sesion):
    plato_de_baja = _producto(Plato, "Milanesa", cant_personas=2, dado_de_baja=True)
    seccion = _seccion_con(sesion, plato_de_baja)

    assert seccion.productos == [plato_de_baja]
    assert seccion.productos_ids == []


def test_ids_08_modelo_devuelve_ids_ascendentes(sesion):
    # Productos con ids explícitos asignados en el orden 12, 10, 11
    doce = _producto(Plato, "Doce", cant_personas=1, id=12)
    diez = _producto(Postre, "Diez", id=10)
    once = _producto(Postre, "Once", id=11)
    seccion = Seccion(nombre="Entradas", nombre_normalizado="entradas", posicion=1)
    seccion.productos.extend([doce, diez, once])

    assert [p.id for p in seccion.productos] == [12, 10, 11]
    assert seccion.productos_ids == [10, 11, 12]


def test_ids_15_modelo_ignora_productos_de_otras_secciones_y_sin_seccion(sesion):
    plato = _producto(Plato, "Milanesa", cant_personas=2)
    postre = _producto(Postre, "Flan")
    bebida = _producto(Bebida, "Cerveza", es_alcoholica=False)
    propia = _seccion_con(sesion, plato)
    otra = Seccion(nombre="Postres", nombre_normalizado="postres", posicion=2)
    otra.productos.append(postre)
    sesion.add_all([otra, bebida])
    sesion.commit()

    assert bebida.seccion_id is None
    assert propia.productos_ids == [plato.id]
    assert otra.productos_ids == [postre.id]


def _combo(plato, **cambios):
    return ComboPromocion(
        nombre="Combo",
        nombre_normalizado="combo",
        precio=Decimal("3000.00"),
        fecha_desde=date.today() - timedelta(days=30),
        fecha_hasta=date.today() + timedelta(days=30),
        platos=[plato],
        **cambios,
    )


def test_ids_09_modelo_cuenta_los_cinco_subtipos(sesion):
    plato = _producto(Plato, "Milanesa", cant_personas=2)
    bebida = _producto(Bebida, "Cerveza", es_alcoholica=True)
    postre = _producto(Postre, "Flan")
    menu = _producto(MenuEjecutivo, "Menu", plato=plato, postre=postre)
    combo = _combo(plato)
    seccion = _seccion_con(sesion, plato, bebida, postre, menu, combo)

    ids = [plato.id, bebida.id, postre.id, menu.id, combo.id]
    assert len(set(ids)) == 5
    assert seccion.productos_ids == sorted(ids)


def test_ids_10_modelo_cuenta_combo_vencido_pero_activo(sesion):
    plato = _producto(Plato, "Milanesa", cant_personas=2)
    combo = _combo(plato)
    combo.fecha_hasta = date.today() - timedelta(days=1)
    seccion = _seccion_con(sesion, combo)

    assert combo.dado_de_baja is False
    assert seccion.productos_ids == [combo.id]


def test_productos_ids_emite_un_unico_select_sobre_producto(sesion, motor):
    plato = _producto(Plato, "Milanesa", cant_personas=2)
    bebida = _producto(Bebida, "Cerveza", es_alcoholica=True)
    postre = _producto(Postre, "Flan")
    menu = _producto(MenuEjecutivo, "Menu", plato=plato, postre=postre)
    combo = _combo(plato)
    seccion = _seccion_con(sesion, plato, bebida, postre, menu, combo)
    esperados = sorted([plato.id, bebida.id, postre.id, menu.id, combo.id])
    sesion.expire_all()  # fuerza la carga diferida de `productos`
    assert seccion.id  # recarga los atributos de la sección fuera de la medición

    sentencias = []

    def registrar(_conexion, _cursor, sentencia, *_resto):
        sentencias.append(sentencia)

    event.listen(motor, "before_cursor_execute", registrar)
    try:
        ids = seccion.productos_ids
    finally:
        event.remove(motor, "before_cursor_execute", registrar)

    assert ids == esperados
    selects = [s for s in sentencias if s.lstrip().upper().startswith("SELECT")]
    assert len(selects) == 1
    assert len(sentencias) == 1
    tablas_de_subtipo = r"\b(plato|bebida|postre|menu_ejecutivo|combo_promocion)\b"
    assert not re.search(tablas_de_subtipo, selects[0])
