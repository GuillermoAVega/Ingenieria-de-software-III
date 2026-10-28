from sqlalchemy.orm import class_mapper, configure_mappers

from src.productos.constants import (
    TIPO_BEBIDA,
    TIPO_COMBO_PROMOCION,
    TIPO_MENU_EJECUTIVO,
    TIPO_PLATO,
    TIPO_POSTRE,
)
from src.productos.registro import MODELOS_POR_TIPO


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


def test_sec_01_mappers_se_configuran_con_la_nueva_entidad():
    from src.productos.registro import Seccion

    configure_mappers()
    assert class_mapper(Seccion).relationships["productos"].mapper.class_.__name__ == "Producto"
