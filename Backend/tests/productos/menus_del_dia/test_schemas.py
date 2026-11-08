import pytest
from pydantic import ValidationError

from src.productos.menus_del_dia.schemas import (
    MenuDelDiaActualizar,
    MenuDelDiaCrear,
    MenuDelDiaRespuesta,
)


def test_mdd_20_acepta_solo_los_campos_comunes():
    menu = MenuDelDiaCrear(
        nombre="Menú del lunes", precio="2500.00", descripcion="x", imagen="f.png", seccion_id=1
    )
    assert menu.nombre == "Menú del lunes"
    assert menu.seccion_id == 1


def test_mdd_20_actualizar_agrega_dado_de_baja_opcional():
    assert MenuDelDiaActualizar(nombre="M", precio="1.00").dado_de_baja is None
    assert MenuDelDiaActualizar(nombre="M", precio="1.00", dado_de_baja=True).dado_de_baja is True


def test_mdd_20_respuesta_expone_tipo_y_no_expone_fechas(crear_menu_del_dia):
    menu = crear_menu_del_dia()
    menu.id = 3
    menu.dado_de_baja = False
    respuesta = MenuDelDiaRespuesta.model_validate(menu)
    datos = respuesta.model_dump()
    assert respuesta.tipo == "menu_del_dia"
    assert "fechas" not in datos
    assert "menus_del_dia" not in datos


@pytest.mark.parametrize(
    "cambios",
    [{"nombre": ""}, {"precio": "0"}, {"descripcion": "x" * 501}],
)
def test_mdd_34_valida_los_campos_comunes(cambios):
    datos = {"nombre": "Menú", "precio": "10.00", **cambios}
    with pytest.raises(ValidationError):
        MenuDelDiaCrear(**datos)
