from datetime import date

import pytest
from sqlalchemy import inspect, insert, select
from sqlalchemy.exc import IntegrityError

from src.productos.combos.models import combo_bebida, combo_plato, combo_postre


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
    "tabla, nombre_fabrica, columna_componente",
    [
        (combo_plato, "crear_plato", "plato_id"),
        (combo_bebida, "crear_bebida", "bebida_id"),
        (combo_postre, "crear_postre", "postre_id"),
    ],
)
def test_duplicado_en_tabla_de_asociacion_lanza_integrity_error(
    sesion, crear_combo, request, tabla, nombre_fabrica, columna_componente
):
    fabrica = request.getfixturevalue(nombre_fabrica)
    componente, combo = fabrica(), crear_combo()
    sesion.add_all([componente, combo])
    sesion.commit()
    fila = {"combo_id": combo.id, columna_componente: componente.id}
    sesion.execute(insert(tabla).values(**fila))
    with pytest.raises(IntegrityError):
        sesion.execute(insert(tabla).values(**fila))
    sesion.rollback()


def test_relaciones_del_combo_bidireccionales(
    sesion, crear_plato, crear_bebida, crear_postre, crear_combo
):
    plato, bebida, postre = crear_plato(), crear_bebida(), crear_postre()
    combo = crear_combo(platos=[plato], bebidas=[bebida], postres=[postre])
    sesion.add(combo)
    sesion.commit()
    assert plato.combos == [combo]
    assert bebida.combos == [combo]
    assert postre.combos == [combo]


def test_relacion_inversa_del_componente_es_de_solo_lectura(
    sesion, crear_plato, crear_combo
):
    plato = crear_plato()
    combo = crear_combo(platos=[(plato, 2)])
    sesion.add(combo)
    sesion.commit()
    assert plato.combos == [combo]


def test_propiedades_devuelven_componentes_con_cantidad_ordenados_por_id(
    sesion, crear_plato, crear_bebida, crear_combo
):
    platos = [crear_plato(nombre=f"Plato {n}") for n in range(3)]
    bebidas = [crear_bebida(nombre=f"Bebida {n}") for n in range(2)]
    sesion.add_all(platos + bebidas)
    sesion.commit()
    combo = crear_combo(
        platos=[(p, n + 2) for n, p in enumerate(reversed(platos))],
        bebidas=list(reversed(bebidas)),
    )
    sesion.add(combo)
    sesion.commit()
    assert combo.platos == [
        {"id": p.id, "cantidad": 4 - n} for n, p in enumerate(platos)
    ]
    assert combo.bebidas == [{"id": b.id, "cantidad": 1} for b in bebidas]
    assert combo.postres == []


@pytest.mark.parametrize(
    "tabla, nombre_fabrica, columna_componente",
    [
        (combo_plato, "crear_plato", "plato_id"),
        (combo_bebida, "crear_bebida", "bebida_id"),
        (combo_postre, "crear_postre", "postre_id"),
    ],
)
def test_plc_61_check_de_cantidad_rechazado_por_la_bd(
    sesion, crear_combo, request, tabla, nombre_fabrica, columna_componente
):
    componente, combo = request.getfixturevalue(nombre_fabrica)(), crear_combo()
    sesion.add_all([componente, combo])
    sesion.commit()
    fila = {"combo_id": combo.id, columna_componente: componente.id}
    with pytest.raises(IntegrityError):
        sesion.execute(insert(tabla).values(**fila, cantidad=0))
    sesion.rollback()


@pytest.mark.parametrize(
    "tabla, nombre_fabrica, columna_componente",
    [
        (combo_plato, "crear_plato", "plato_id"),
        (combo_bebida, "crear_bebida", "bebida_id"),
        (combo_postre, "crear_postre", "postre_id"),
    ],
)
def test_cantidad_tiene_server_default_uno(
    sesion, crear_combo, request, tabla, nombre_fabrica, columna_componente
):
    componente, combo = request.getfixturevalue(nombre_fabrica)(), crear_combo()
    sesion.add_all([componente, combo])
    sesion.commit()
    sesion.execute(insert(tabla).values(combo_id=combo.id, **{columna_componente: componente.id}))
    assert sesion.execute(select(tabla.c.cantidad)).scalar_one() == 1


def test_plc_60_baja_de_un_plato_componente_de_un_combo_activo_sigue_bloqueada(
    cliente, crear_plato, crear_combo, persistir
):
    plato = crear_plato()
    plato_id, _ = persistir(plato, crear_combo(platos=[(plato, 3)], hasta=date(2100, 1, 1)))
    assert cliente.delete(f"/productos/platos/{plato_id}").status_code == 409


def test_check_rango_de_fechas_rechazado_por_la_bd(sesion, crear_combo):
    sesion.add(crear_combo(desde=date(2026, 7, 1), hasta=date(2026, 6, 1)))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_combo_con_fechas_iguales_permitido(sesion, crear_combo):
    sesion.add(crear_combo(desde=date(2026, 6, 1), hasta=date(2026, 6, 1)))
    sesion.commit()
