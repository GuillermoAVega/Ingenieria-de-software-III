from datetime import date

import pytest
from pydantic import ValidationError

from src.productos.combos.schemas import ComboActualizar, ComboCrear, ComboRespuesta
from tests.productos.combos.ayudas import comp


def datos_combo(**cambios):
    datos = {
        "nombre": "Combo",
        "precio": "3000.00",
        "fecha_desde": date(2026, 6, 1),
        "fecha_hasta": date(2026, 6, 30),
        "platos": comp(1),
        "bebidas": comp(),
        "postres": comp(),
    }
    datos.update(cambios)
    return datos


def test_combo_sin_componentes_se_rechaza():
    with pytest.raises(ValidationError):
        ComboCrear(**datos_combo(platos=comp(), bebidas=comp(), postres=comp()))


def test_combo_con_listas_omitidas_se_rechaza():
    datos = datos_combo()
    del datos["platos"]
    with pytest.raises(ValidationError):
        ComboCrear(**datos)


def test_combo_con_una_lista_omitida_se_rechaza_aunque_otra_tenga_ids():
    datos = datos_combo(platos=comp(1), bebidas=comp(2), postres=comp(3))
    del datos["bebidas"]
    with pytest.raises(ValidationError):
        ComboCrear(**datos)


def test_un_solo_id_en_una_lista_es_valido():
    combo = ComboCrear(**datos_combo(platos=comp(), bebidas=comp(4)))
    assert combo.bebidas[0].model_dump() == {"id": 4, "cantidad": 1}
    assert combo.platos == []
    assert combo.postres == []


def test_ids_repetidos_en_una_lista_se_rechazan():
    with pytest.raises(ValidationError):
        ComboCrear(**datos_combo(platos=comp(1, 1)))


def test_el_mismo_id_en_listas_distintas_no_cuenta_como_duplicado():
    combo = ComboCrear(**datos_combo(platos=comp(1), bebidas=comp(1)))
    assert [c.model_dump() for c in combo.bebidas] == comp(1)


def test_rango_de_fechas_invertido_se_rechaza():
    with pytest.raises(ValidationError):
        ComboCrear(
            **datos_combo(fecha_desde=date(2026, 7, 1), fecha_hasta=date(2026, 6, 30))
        )


def test_fechas_iguales_son_validas():
    combo = ComboCrear(
        **datos_combo(fecha_desde=date(2026, 6, 1), fecha_hasta=date(2026, 6, 1))
    )
    assert combo.fecha_desde == combo.fecha_hasta


@pytest.mark.parametrize("campo", ["fecha_desde", "fecha_hasta"])
def test_las_fechas_son_obligatorias(campo):
    datos = datos_combo()
    del datos[campo]
    with pytest.raises(ValidationError):
        ComboCrear(**datos)


def test_actualizar_hereda_validaciones_y_agrega_dado_de_baja():
    assert ComboActualizar(**datos_combo()).dado_de_baja is None
    assert ComboActualizar(**datos_combo(dado_de_baja=True)).dado_de_baja is True
    with pytest.raises(ValidationError):
        ComboActualizar(**datos_combo(platos=comp()))


def test_respuesta_expone_los_componentes_con_su_cantidad_desde_el_modelo(
    sesion, crear_plato, crear_bebida, crear_combo
):
    plato, bebida = crear_plato(), crear_bebida()
    combo = crear_combo(platos=[(plato, 3)], bebidas=[bebida])
    sesion.add(combo)
    sesion.commit()
    respuesta = ComboRespuesta.model_validate(combo)
    assert respuesta.tipo == "combo_promocion"
    assert [c.model_dump() for c in respuesta.platos] == comp(plato.id, cantidad=3)
    assert [c.model_dump() for c in respuesta.bebidas] == comp(bebida.id)
    assert respuesta.postres == []
    assert respuesta.fecha_hasta == date(2026, 6, 30)
