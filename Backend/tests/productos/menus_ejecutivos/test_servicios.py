from decimal import Decimal

import pytest
from sqlalchemy import select

from src.productos import services
from src.productos.exceptions import (
    ComponenteInactivo,
    ComponenteInvalido,
    NombreDuplicado,
    ProductoNoEncontrado,
)
from src.productos.menus_ejecutivos import services as servicios_menus
from src.productos.menus_ejecutivos.models import MenuEjecutivo
from src.productos.menus_ejecutivos.schemas import MenuActualizar, MenuCrear
from src.productos.models import Producto


def _crear_componentes(sesion, crear_plato, crear_bebida, crear_postre):
    plato, bebida, postre = crear_plato(), crear_bebida(), crear_postre()
    sesion.add_all([plato, bebida, postre])
    sesion.commit()
    return plato, bebida, postre


def test_cat_31_plato_id_de_una_bebida_es_componente_invalido(
    sesion, crear_plato, crear_bebida, crear_postre
):
    _, bebida, postre = _crear_componentes(sesion, crear_plato, crear_bebida, crear_postre)

    with pytest.raises(ComponenteInvalido) as error:
        servicios_menus.resolver_componentes_menu(sesion, bebida.id, postre.id, True)

    assert error.value.campo == "plato_id"
    assert error.value.ids == [bebida.id]


def test_cat_32_postre_id_inexistente_es_componente_invalido(
    sesion, crear_plato, crear_bebida, crear_postre
):
    plato, _, _ = _crear_componentes(sesion, crear_plato, crear_bebida, crear_postre)

    with pytest.raises(ComponenteInvalido) as error:
        servicios_menus.resolver_componentes_menu(sesion, plato.id, 999, True)

    assert error.value.campo == "postre_id"
    assert error.value.ids == [999]


def test_cat_33_plato_dado_de_baja_con_exigir_activos_es_componente_inactivo(
    sesion, crear_plato, crear_bebida, crear_postre
):
    plato, _, postre = _crear_componentes(sesion, crear_plato, crear_bebida, crear_postre)
    plato.dado_de_baja = True
    sesion.commit()

    with pytest.raises(ComponenteInactivo) as error:
        servicios_menus.resolver_componentes_menu(sesion, plato.id, postre.id, True)

    assert error.value.ids == [plato.id]


def test_cat_33_sin_exigir_activos_no_lanza_y_devuelve_los_componentes(
    sesion, crear_plato, crear_bebida, crear_postre
):
    plato, _, postre = _crear_componentes(sesion, crear_plato, crear_bebida, crear_postre)
    plato.dado_de_baja = True
    postre.dado_de_baja = True
    sesion.commit()

    resueltos = servicios_menus.resolver_componentes_menu(sesion, plato.id, postre.id, False)

    assert resueltos == (plato, postre)


def test_cat_44_la_existencia_se_valida_aunque_no_se_exijan_activos(
    sesion, crear_plato, crear_bebida, crear_postre
):
    plato, _, _ = _crear_componentes(sesion, crear_plato, crear_bebida, crear_postre)

    with pytest.raises(ComponenteInvalido):
        servicios_menus.resolver_componentes_menu(sesion, plato.id, 999, False)


def _datos_crear(plato, postre, **cambios):
    datos = {
        "nombre": "Menú del día",
        "precio": Decimal("2000.00"),
        "plato_id": plato.id,
        "postre_id": postre.id,
    }
    datos.update(cambios)
    return MenuCrear(**datos)


def _datos_actualizar(plato, postre, **cambios):
    datos = {
        "nombre": "Menú del día",
        "precio": Decimal("2000.00"),
        "plato_id": plato.id,
        "postre_id": postre.id,
    }
    datos.update(cambios)
    return MenuActualizar(**datos)


@pytest.fixture
def menu_con_componentes(sesion, crear_plato, crear_postre, crear_menu):
    """Menú persistido (activo) con su Plato y su Postre."""
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    sesion.add_all([plato, postre, menu])
    sesion.commit()
    return menu, plato, postre


def test_cat_30_crear_menu_con_componentes_activos_persiste(
    sesion, crear_plato, crear_postre
):
    plato, postre = crear_plato(), crear_postre()
    sesion.add_all([plato, postre])
    sesion.commit()

    menu = servicios_menus.crear_menu(
        sesion, _datos_crear(plato, postre, nombre="  Menú del día ")
    )

    guardado = sesion.get(MenuEjecutivo, menu.id)
    assert guardado.nombre == "Menú del día"
    assert guardado.nombre_normalizado == "menú del día"
    assert guardado.precio == Decimal("2000.00")
    assert guardado.plato_id == plato.id
    assert guardado.postre_id == postre.id
    assert guardado.dado_de_baja is False


def test_cat_21_crear_menu_con_nombre_activo_duplicado(sesion, crear_plato, crear_postre):
    plato, postre = crear_plato("Milanesa"), crear_postre()
    sesion.add_all([plato, postre])
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_menus.crear_menu(sesion, _datos_crear(plato, postre, nombre="MILANESA"))

    assert not sesion.scalars(select(MenuEjecutivo)).all()


def test_cat_33_crear_menu_con_plato_inactivo_no_persiste_nada(
    sesion, crear_plato, crear_postre
):
    plato, postre = crear_plato(), crear_postre()
    plato.dado_de_baja = True
    sesion.add_all([plato, postre])
    sesion.commit()

    with pytest.raises(ComponenteInactivo) as error:
        servicios_menus.crear_menu(sesion, _datos_crear(plato, postre))

    assert error.value.ids == [plato.id]
    assert not sesion.scalars(select(MenuEjecutivo)).all()


def test_cat_31_crear_menu_con_plato_id_de_una_bebida_es_invalido(
    sesion, crear_bebida, crear_postre
):
    bebida, postre = crear_bebida(), crear_postre()
    sesion.add_all([bebida, postre])
    sesion.commit()

    with pytest.raises(ComponenteInvalido) as error:
        servicios_menus.crear_menu(sesion, _datos_crear(bebida, postre))

    assert error.value.campo == "plato_id"
    assert not sesion.scalars(select(MenuEjecutivo)).all()


def test_cat_42_actualizar_menu_activo_con_postre_inactivo_no_cambia_el_menu(
    sesion, menu_con_componentes, crear_postre, HOY
):
    menu, plato, _ = menu_con_componentes
    postre_inactivo = crear_postre("Helado")
    postre_inactivo.dado_de_baja = True
    sesion.add(postre_inactivo)
    sesion.commit()

    with pytest.raises(ComponenteInactivo) as error:
        servicios_menus.actualizar_menu(
            sesion,
            menu.id,
            _datos_actualizar(plato, postre_inactivo, nombre="Otro nombre"),
            HOY,
        )

    sesion.expire_all()
    guardado = sesion.get(MenuEjecutivo, menu.id)
    assert error.value.ids == [postre_inactivo.id]
    assert guardado.nombre == "Menú del día"
    assert guardado.postre_id != postre_inactivo.id


@pytest.mark.parametrize("dado_de_baja", [True, None], ids=["true", "omitido"])
def test_cat_43_editar_menu_de_baja_con_plato_inactivo_manteniendolo_de_baja(
    sesion, menu_con_componentes, HOY, dado_de_baja
):
    menu, plato, postre = menu_con_componentes
    menu.dado_de_baja = True
    plato.dado_de_baja = True
    sesion.commit()

    actualizado = servicios_menus.actualizar_menu(
        sesion,
        menu.id,
        _datos_actualizar(plato, postre, descripcion="Nueva", dado_de_baja=dado_de_baja),
        HOY,
    )

    assert actualizado.descripcion == "Nueva"
    assert actualizado.dado_de_baja is True


def test_cat_44_menu_de_baja_con_postre_inexistente_es_invalido(
    sesion, menu_con_componentes, HOY
):
    menu, plato, _ = menu_con_componentes
    menu.dado_de_baja = True
    sesion.commit()

    with pytest.raises(ComponenteInvalido) as error:
        servicios_menus.actualizar_menu(
            sesion,
            menu.id,
            _datos_actualizar(plato, plato, postre_id=999, dado_de_baja=True),
            HOY,
        )

    assert error.value.campo == "postre_id"
    assert error.value.ids == [999]


def test_ld_19_reactivar_menu_con_componente_inactivo_sigue_de_baja(
    sesion, menu_con_componentes, HOY
):
    menu, plato, postre = menu_con_componentes
    menu.dado_de_baja = True
    plato.dado_de_baja = True
    sesion.commit()

    with pytest.raises(ComponenteInactivo) as error:
        servicios_menus.actualizar_menu(
            sesion, menu.id, _datos_actualizar(plato, postre, dado_de_baja=False), HOY
        )

    sesion.expire_all()
    assert error.value.ids == [plato.id]
    assert sesion.get(MenuEjecutivo, menu.id).dado_de_baja is True


def test_ld_20_reactivar_menu_con_componentes_activos(sesion, menu_con_componentes, HOY):
    menu, plato, postre = menu_con_componentes
    menu.dado_de_baja = True
    sesion.commit()

    actualizado = servicios_menus.actualizar_menu(
        sesion, menu.id, _datos_actualizar(plato, postre, dado_de_baja=False), HOY
    )

    assert actualizado.dado_de_baja is False


def test_ld_21_reactivar_menu_con_nombre_en_conflicto(
    sesion, menu_con_componentes, crear_bebida, HOY
):
    menu, plato, postre = menu_con_componentes
    menu.dado_de_baja = True
    sesion.add(crear_bebida(nombre="Menú del día"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_menus.actualizar_menu(
            sesion, menu.id, _datos_actualizar(plato, postre, dado_de_baja=False), HOY
        )

    sesion.expire_all()
    assert sesion.get(MenuEjecutivo, menu.id).dado_de_baja is True


def test_cat_21_actualizar_menu_activo_con_nombre_de_otro_producto_duplicado(
    sesion, menu_con_componentes, crear_bebida, HOY
):
    menu, plato, postre = menu_con_componentes
    sesion.add(crear_bebida(nombre="Cerveza"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_menus.actualizar_menu(
            sesion, menu.id, _datos_actualizar(plato, postre, nombre="cerveza"), HOY
        )


def test_cat_41_cambiar_el_precio_del_plato_no_cambia_el_del_menu(
    sesion, menu_con_componentes
):
    menu, plato, _ = menu_con_componentes

    plato.precio = Decimal("9999.00")
    sesion.commit()
    sesion.expire_all()

    assert sesion.get(MenuEjecutivo, menu.id).precio == Decimal("2000.00")


def test_actualizar_menu_reemplaza_el_objeto_completo_y_cambia_componentes(
    sesion, menu_con_componentes, crear_plato, crear_postre, HOY
):
    menu, _, _ = menu_con_componentes
    plato_nuevo, postre_nuevo = crear_plato("Pizza"), crear_postre("Helado")
    sesion.add_all([plato_nuevo, postre_nuevo])
    sesion.commit()

    actualizado = servicios_menus.actualizar_menu(
        sesion,
        menu.id,
        _datos_actualizar(plato_nuevo, postre_nuevo, precio=Decimal("2500.00")),
        HOY,
    )

    assert actualizado.plato_id == plato_nuevo.id
    assert actualizado.postre_id == postre_nuevo.id
    assert actualizado.precio == Decimal("2500.00")
    assert actualizado.descripcion is None


def test_cat_14_actualizar_menu_desconocido_es_404_antes_que_los_componentes(
    sesion, crear_plato, crear_postre, HOY
):
    plato, postre = crear_plato(), crear_postre()
    sesion.add_all([plato, postre])
    sesion.commit()

    with pytest.raises(ProductoNoEncontrado):
        servicios_menus.actualizar_menu(
            sesion, 999, _datos_actualizar(plato, postre, postre_id=998), HOY
        )


def test_cat_14_los_componentes_se_validan_antes_que_el_nombre(
    sesion, menu_con_componentes, crear_bebida, HOY
):
    menu, plato, _ = menu_con_componentes
    sesion.add(crear_bebida(nombre="Cerveza"))
    sesion.commit()

    with pytest.raises(ComponenteInvalido):
        servicios_menus.actualizar_menu(
            sesion,
            menu.id,
            _datos_actualizar(plato, plato, nombre="Cerveza", postre_id=999),
            HOY,
        )


def test_ld_16_dar_de_baja_un_menu_no_tiene_restriccion_ni_toca_componentes(
    sesion, menu_con_componentes, HOY
):
    menu, plato, postre = menu_con_componentes

    services.dar_de_baja(sesion, MenuEjecutivo, menu.id, HOY)

    sesion.expire_all()
    assert sesion.get(MenuEjecutivo, menu.id).dado_de_baja is True
    assert sesion.get(Producto, plato.id).dado_de_baja is False
    assert sesion.get(Producto, postre.id).dado_de_baja is False


def test_actualizar_menu_activo_a_baja_no_exige_componentes_activos(
    sesion, menu_con_componentes, HOY
):
    menu, plato, postre = menu_con_componentes
    postre.dado_de_baja = True
    sesion.commit()

    actualizado = servicios_menus.actualizar_menu(
        sesion, menu.id, _datos_actualizar(plato, postre, dado_de_baja=True), HOY
    )

    assert actualizado.dado_de_baja is True
