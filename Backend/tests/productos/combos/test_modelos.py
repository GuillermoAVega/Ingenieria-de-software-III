from datetime import date

import pytest
from sqlalchemy import inspect, insert
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


def test_relaciones_asignadas_desde_el_componente(
    crear_plato, crear_bebida, crear_postre, crear_combo
):
    plato, bebida, postre = crear_plato(), crear_bebida(), crear_postre()
    combo = crear_combo()
    plato.combos.append(combo)
    bebida.combos.append(combo)
    postre.combos.append(combo)
    assert combo.platos == [plato]
    assert combo.bebidas == [bebida]
    assert combo.postres == [postre]


def test_propiedades_ids_devuelven_listas_ordenadas(
    sesion, crear_plato, crear_bebida, crear_combo
):
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


def test_check_rango_de_fechas_rechazado_por_la_bd(sesion, crear_combo):
    sesion.add(crear_combo(desde=date(2026, 7, 1), hasta=date(2026, 6, 1)))
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_combo_con_fechas_iguales_permitido(sesion, crear_combo):
    sesion.add(crear_combo(desde=date(2026, 6, 1), hasta=date(2026, 6, 1)))
    sesion.commit()
