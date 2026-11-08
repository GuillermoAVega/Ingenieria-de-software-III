from sqlalchemy.orm import class_mapper, configure_mappers

from src.productos.constants import TIPO_MENU_DEL_DIA
from src.productos.menus_del_dia.models import MenuDelDia
from src.productos.menus_ejecutivos.models import MenuEjecutivo


def test_mdd_30_menu_del_dia_tiene_identidad_polimorfica_y_tabla_propia():
    configure_mappers()
    mapper = class_mapper(MenuDelDia)
    assert TIPO_MENU_DEL_DIA == "menu_del_dia"
    assert mapper.polymorphic_identity == TIPO_MENU_DEL_DIA
    assert MenuDelDia.__tablename__ == "menu_del_dia"


def test_mdd_31_menu_del_dia_y_menu_ejecutivo_son_clases_y_tablas_distintas():
    assert MenuDelDia is not MenuEjecutivo
    assert MenuDelDia.__tablename__ != MenuEjecutivo.__tablename__
    assert (
        class_mapper(MenuDelDia).polymorphic_identity
        != class_mapper(MenuEjecutivo).polymorphic_identity
    )
