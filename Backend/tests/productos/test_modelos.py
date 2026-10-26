from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import inspect, insert, select
from sqlalchemy.orm import configure_mappers
from sqlalchemy.exc import IntegrityError

from src.productos.constants import (
    TIPO_BEBIDA,
    TIPO_MAX,
    TIPO_PLATO,
    TIPO_POSTRE,
)
from src.productos.models import (
    Bebida,
    ComboPromocion,
    MenuEjecutivo,
    Plato,
    Postre,
    Producto,
    combo_bebida,
    combo_plato,
    combo_postre,
)


def crear_plato(nombre="Milanesa", precio="1500.00", cant_personas=2, **extra):
    return Plato(
        nombre=nombre,
        nombre_normalizado=nombre.strip().casefold(),
        precio=Decimal(precio),
        cant_personas=cant_personas,
        **extra,
    )


def crear_bebida(nombre="Cerveza", precio="800.00", es_alcoholica=True):
    return Bebida(
        nombre=nombre,
        nombre_normalizado=nombre.strip().casefold(),
        precio=Decimal(precio),
        es_alcoholica=es_alcoholica,
    )


def crear_postre(nombre="Flan", precio="600.00"):
    return Postre(
        nombre=nombre,
        nombre_normalizado=nombre.strip().casefold(),
        precio=Decimal(precio),
    )


# --- 1.2: Producto abstracto + Plato, Bebida, Postre ---


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


def test_persistir_y_releer_con_el_tipo_correcto(sesion):
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


def test_check_precio_positivo_rechazado_por_la_bd(sesion):
    sesion.add(crear_postre(precio="0.00"))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_check_cant_personas_minima_rechazado_por_la_bd(sesion):
    sesion.add(crear_plato(cant_personas=0))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_indice_parcial_existe(motor):
    indices = {i["name"]: i for i in inspect(motor).get_indexes("producto")}
    assert "ux_producto_nombre_activo" in indices
    assert indices["ux_producto_nombre_activo"]["unique"]
    assert indices["ux_producto_nombre_activo"]["column_names"] == ["nombre_normalizado"]


def test_indice_parcial_rechaza_dos_activos_con_igual_nombre_normalizado(sesion):
    sesion.add(crear_plato(nombre="Pizza"))
    sesion.commit()
    sesion.add(crear_bebida(nombre="PIZZA"))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_reutilizacion_del_nombre_tras_la_baja_permitida(sesion):
    primero = crear_plato(nombre="Pizza")
    sesion.add(primero)
    sesion.commit()
    primero.dado_de_baja = True
    sesion.commit()

    sesion.add(crear_plato(nombre="Pizza"))
    sesion.commit()

    cantidad = len(sesion.scalars(select(Producto)).all())
    assert cantidad == 2


# --- 1.3: MenuEjecutivo y relaciones bidireccionales ---


def crear_menu(plato, postre, nombre="Menú del día", precio="2000.00"):
    return MenuEjecutivo(
        nombre=nombre,
        nombre_normalizado=nombre.strip().casefold(),
        precio=Decimal(precio),
        plato=plato,
        postre=postre,
    )


def test_los_mappers_se_configuran_con_menu():
    configure_mappers()


def test_relacion_menu_plato_bidireccional(sesion):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    sesion.add(menu)
    sesion.commit()
    assert plato.menus == [menu]
    assert menu.plato is plato


def test_relacion_plato_menus_asignada_desde_el_otro_lado():
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(None, None)
    plato.menus.append(menu)
    postre.menus.append(menu)
    assert menu.plato is plato
    assert menu.postre is postre


def test_fk_rechaza_plato_id_de_una_bebida(sesion):
    bebida, postre = crear_bebida(), crear_postre()
    sesion.add_all([bebida, postre])
    sesion.commit()
    menu = MenuEjecutivo(
        nombre="Menú malo",
        nombre_normalizado="menú malo",
        precio=Decimal("1.00"),
        plato_id=bebida.id,
        postre_id=postre.id,
    )
    sesion.add(menu)
    with pytest.raises(IntegrityError):
        sesion.commit()


# --- 1.4: ComboPromocion, tablas de asociación y propiedades *_ids ---


def crear_combo(nombre="Combo", desde=date(2026, 6, 1), hasta=date(2026, 6, 30), **relaciones):
    return ComboPromocion(
        nombre=nombre,
        nombre_normalizado=nombre.strip().casefold(),
        precio=Decimal("3000.00"),
        fecha_desde=desde,
        fecha_hasta=hasta,
        **relaciones,
    )


def test_los_mappers_se_configuran_con_los_cinco_subtipos():
    configure_mappers()
    from sqlalchemy.orm import class_mapper

    for subtipo in (Plato, Bebida, Postre, MenuEjecutivo, ComboPromocion):
        class_mapper(subtipo)


@pytest.mark.parametrize(
    "tabla, columna_componente",
    [
        (combo_plato, "plato_id"),
        (combo_bebida, "bebida_id"),
        (combo_postre, "postre_id"),
    ],
)
def test_tablas_de_asociacion_con_pk_compuesta(motor, tabla, columna_componente):
    assert {c.name for c in tabla.primary_key.columns} == {"combo_id", columna_componente}
    assert tabla.name in inspect(motor).get_table_names()


@pytest.mark.parametrize(
    "tabla, fabrica, columna_componente",
    [
        (combo_plato, crear_plato, "plato_id"),
        (combo_bebida, crear_bebida, "bebida_id"),
        (combo_postre, crear_postre, "postre_id"),
    ],
)
def test_duplicado_en_tabla_de_asociacion_lanza_integrity_error(
    sesion, tabla, fabrica, columna_componente
):
    componente, combo = fabrica(), crear_combo()
    sesion.add_all([componente, combo])
    sesion.commit()
    fila = {"combo_id": combo.id, columna_componente: componente.id}
    sesion.execute(insert(tabla).values(**fila))
    with pytest.raises(IntegrityError):
        sesion.execute(insert(tabla).values(**fila))
    sesion.rollback()


def test_relaciones_del_combo_bidireccionales(sesion):
    plato, bebida, postre = crear_plato(), crear_bebida(), crear_postre()
    combo = crear_combo(platos=[plato], bebidas=[bebida], postres=[postre])
    sesion.add(combo)
    sesion.commit()
    assert plato.combos == [combo]
    assert bebida.combos == [combo]
    assert postre.combos == [combo]


def test_relaciones_asignadas_desde_el_componente():
    plato, bebida, postre = crear_plato(), crear_bebida(), crear_postre()
    combo = crear_combo()
    plato.combos.append(combo)
    bebida.combos.append(combo)
    postre.combos.append(combo)
    assert combo.platos == [plato]
    assert combo.bebidas == [bebida]
    assert combo.postres == [postre]


def test_propiedades_ids_devuelven_listas_ordenadas(sesion):
    platos = [crear_plato(nombre=f"Plato {n}") for n in range(3)]
    bebidas = [crear_bebida(nombre=f"Bebida {n}") for n in range(2)]
    sesion.add_all(platos + bebidas)
    sesion.commit()
    combo = crear_combo(platos=list(reversed(platos)), bebidas=list(reversed(bebidas)))
    sesion.add(combo)
    sesion.commit()
    assert combo.platos_ids == sorted(p.id for p in platos)
    assert combo.bebidas_ids == sorted(b.id for b in bebidas)
    assert combo.postres_ids == []


def test_check_rango_de_fechas_rechazado_por_la_bd(sesion):
    sesion.add(crear_combo(desde=date(2026, 7, 1), hasta=date(2026, 6, 1)))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_combo_con_fechas_iguales_permitido(sesion):
    sesion.add(crear_combo(desde=date(2026, 6, 1), hasta=date(2026, 6, 1)))
    sesion.commit()
