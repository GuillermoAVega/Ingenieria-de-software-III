from datetime import date

import pytest
from pydantic import ValidationError

from src.productos.combos.schemas import ComboActualizar, ComboCrear, ComboRespuesta


def datos_combo(**cambios):
    datos = {
        "nombre": "Combo",
        "precio": "3000.00",
        "fecha_desde": date(2026, 6, 1),
        "fecha_hasta": date(2026, 6, 30),
        "platos_ids": [1],
        "bebidas_ids": [],
        "postres_ids": [],
    }
    datos.update(cambios)
    return datos


def test_combo_sin_componentes_se_rechaza():
    with pytest.raises(ValidationError):
        ComboCrear(**datos_combo(platos_ids=[], bebidas_ids=[], postres_ids=[]))


def test_combo_con_listas_omitidas_se_rechaza():
    datos = datos_combo()
    del datos["platos_ids"]
    with pytest.raises(ValidationError):
        ComboCrear(**datos)


def test_combo_con_una_lista_omitida_se_rechaza_aunque_otra_tenga_ids():
    datos = datos_combo(platos_ids=[1], bebidas_ids=[2], postres_ids=[3])
    del datos["bebidas_ids"]
    with pytest.raises(ValidationError):
        ComboCrear(**datos)


def test_un_solo_id_en_una_lista_es_valido():
    combo = ComboCrear(**datos_combo(platos_ids=[], bebidas_ids=[4]))
    assert combo.bebidas_ids == [4]
    assert combo.platos_ids == []
    assert combo.postres_ids == []


def test_ids_repetidos_en_una_lista_se_rechazan():
    with pytest.raises(ValidationError):
        ComboCrear(**datos_combo(platos_ids=[1, 1]))


def test_el_mismo_id_en_listas_distintas_no_cuenta_como_duplicado():
    combo = ComboCrear(**datos_combo(platos_ids=[1], bebidas_ids=[1]))
    assert combo.bebidas_ids == [1]


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
        ComboActualizar(**datos_combo(platos_ids=[]))


def test_respuesta_expone_los_ids_desde_el_modelo(
    crear_plato, crear_bebida, crear_combo
):
    plato, bebida = crear_plato(), crear_bebida()
    plato.id, bebida.id = 8, 4
    combo = crear_combo(platos=[plato], bebidas=[bebida])
    combo.id = 6
    combo.dado_de_baja = False
    respuesta = ComboRespuesta.model_validate(combo)
    assert respuesta.tipo == "combo_promocion"
    assert respuesta.platos_ids == [8]
    assert respuesta.bebidas_ids == [4]
    assert respuesta.postres_ids == []
    assert respuesta.fecha_hasta == date(2026, 6, 30)
