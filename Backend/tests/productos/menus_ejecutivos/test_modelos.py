from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import configure_mappers

from src.productos.menus_ejecutivos.models import MenuEjecutivo


def test_los_mappers_se_configuran_con_menu():
    configure_mappers()


def test_relacion_menu_plato_bidireccional(sesion, crear_plato, crear_postre, crear_menu):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    sesion.add(menu)
    sesion.commit()
    assert plato.menus == [menu]
    assert menu.plato is plato


def test_relacion_plato_menus_asignada_desde_el_otro_lado(
    crear_plato, crear_postre, crear_menu
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(None, None)
    plato.menus.append(menu)
    postre.menus.append(menu)
    assert menu.plato is plato
    assert menu.postre is postre


def test_fk_rechaza_plato_id_de_una_bebida(sesion, crear_bebida, crear_postre):
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
