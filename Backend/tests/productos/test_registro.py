import pytest
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import class_mapper, configure_mappers

from src.productos.constants import (
    TIPO_BEBIDA,
    TIPO_COMBO_PROMOCION,
    TIPO_MENU_EJECUTIVO,
    TIPO_PLATO,
    TIPO_POSTRE,
)
from src.productos.bebidas.schemas import BebidaRespuesta
from src.productos.combos.schemas import ComboRespuesta
from src.productos.menus_ejecutivos.schemas import MenuRespuesta
from src.productos.platos.schemas import PlatoRespuesta
from src.productos.postres.schemas import PostreRespuesta
from src.productos.registro import MODELOS_POR_TIPO, ProductoRespuesta


def test_modelos_por_tipo_contiene_los_cinco_tipos():
    assert set(MODELOS_POR_TIPO) == {
        TIPO_PLATO,
        TIPO_BEBIDA,
        TIPO_POSTRE,
        TIPO_MENU_EJECUTIVO,
        TIPO_COMBO_PROMOCION,
    }


def test_cada_clase_tiene_su_identidad_polimorfica():
    for tipo, clase in MODELOS_POR_TIPO.items():
        assert class_mapper(clase).polymorphic_identity == tipo


def test_configure_mappers_no_falla_tras_importar_solo_el_registro():
    configure_mappers()


def test_union_resuelve_cada_instancia_orm_a_su_esquema(
    crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo
):
    plato, bebida, postre = crear_plato(), crear_bebida(), crear_postre()
    menu = crear_menu(plato, postre)
    combo = crear_combo(platos=[plato])
    esperados = [
        (plato, PlatoRespuesta),
        (bebida, BebidaRespuesta),
        (postre, PostreRespuesta),
        (menu, MenuRespuesta),
        (combo, ComboRespuesta),
    ]
    for identificador, (objeto, _) in enumerate(esperados, start=1):
        objeto.id = identificador
        objeto.dado_de_baja = False
    # Fuera de una sesión las FK no se completan solas desde la relación
    menu.plato_id, menu.postre_id = plato.id, postre.id

    adaptador = TypeAdapter(ProductoRespuesta)
    for objeto, esquema in esperados:
        assert type(adaptador.validate_python(objeto, from_attributes=True)) is esquema


def test_union_con_tipo_desconocido_se_rechaza():
    datos = {
        "id": 1,
        "tipo": "otro",
        "nombre": "X",
        "precio": "1.00",
        "descripcion": None,
        "imagen": None,
        "dado_de_baja": False,
    }
    with pytest.raises(ValidationError):
        TypeAdapter(ProductoRespuesta).validate_python(datos)
