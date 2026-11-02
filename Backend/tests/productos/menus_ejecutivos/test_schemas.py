import pytest
from pydantic import ValidationError

from src.productos.menus_ejecutivos.schemas import (
    MenuActualizar,
    MenuCrear,
    MenuRespuesta,
)


def datos_menu(**cambios):
    datos = {"nombre": "Menú del día", "precio": "2000.00", "plato_id": 1, "postre_id": 2}
    datos.update(cambios)
    return datos


@pytest.mark.parametrize("campo", ["plato_id", "postre_id"])
def test_menu_exige_plato_y_postre(campo):
    datos = datos_menu()
    del datos[campo]
    with pytest.raises(ValidationError):
        MenuCrear(**datos)


def test_actualizar_agrega_dado_de_baja_opcional():
    assert MenuActualizar(**datos_menu()).dado_de_baja is None
    assert MenuActualizar(**datos_menu(dado_de_baja=True)).dado_de_baja is True


def test_respuesta_se_construye_desde_el_modelo(
    crear_plato, crear_postre, crear_menu
):
    plato, postre = crear_plato(), crear_postre()
    plato.id, postre.id = 1, 2
    menu = crear_menu(plato, postre)
    # Fuera de una sesión las FK no se completan solas desde la relación
    menu.id, menu.plato_id, menu.postre_id = 3, 1, 2
    menu.dado_de_baja = False
    respuesta = MenuRespuesta.model_validate(menu)
    assert respuesta.tipo == "menu_ejecutivo"
    assert respuesta.plato_id == 1
    assert respuesta.postre_id == 2
