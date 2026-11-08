from decimal import Decimal

import pytest

from src.productos.exceptions import NombreDuplicado, ProductoNoEncontrado, SeccionInexistente
from src.productos.menus_del_dia import services as servicios_menus_del_dia
from src.productos.menus_del_dia.models import MenuDelDia
from src.productos.menus_del_dia.schemas import MenuDelDiaActualizar, MenuDelDiaCrear


def _datos_crear(**cambios):
    datos = {"nombre": "Menú del lunes", "precio": Decimal("2500.00")}
    datos.update(cambios)
    return MenuDelDiaCrear(**datos)


def _datos_actualizar(**cambios):
    datos = {"nombre": "Menú del lunes", "precio": Decimal("2500.00")}
    datos.update(cambios)
    return MenuDelDiaActualizar(**datos)


def test_mdd_32_crear_persiste_los_campos_comunes(sesion):
    menu = servicios_menus_del_dia.crear_menu_del_dia(sesion, _datos_crear(nombre=" Menú A "))

    guardado = sesion.get(MenuDelDia, menu.id)
    assert guardado.nombre == "Menú A"
    assert guardado.nombre_normalizado == "menú a"
    assert guardado.dado_de_baja is False


def test_mdd_34_crear_con_seccion_inexistente(sesion):
    with pytest.raises(SeccionInexistente):
        servicios_menus_del_dia.crear_menu_del_dia(sesion, _datos_crear(seccion_id=999))


def test_mdd_35_nombre_activo_duplicado_entre_subtipos(sesion, crear_plato):
    sesion.add(crear_plato(nombre="Menú del lunes"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_menus_del_dia.crear_menu_del_dia(sesion, _datos_crear())


def test_mdd_36_listar_solo_activos_por_id_ascendente(sesion, crear_menu_del_dia):
    a, b, c = crear_menu_del_dia("A"), crear_menu_del_dia("B"), crear_menu_del_dia("C")
    b.dado_de_baja = True
    sesion.add_all([c, b, a])
    sesion.commit()

    ids = [m.id for m in servicios_menus_del_dia.listar_menus_del_dia(sesion)]

    assert ids == sorted([a.id, c.id])


def test_mdd_38_obtener_un_menu_dado_de_baja(sesion, crear_menu_del_dia):
    from src.productos import services

    menu = crear_menu_del_dia()
    menu.dado_de_baja = True
    sesion.add(menu)
    sesion.commit()

    assert services.obtener(sesion, MenuDelDia, menu.id).dado_de_baja is True


def test_mdd_40_actualizar_es_reemplazo_completo(sesion, crear_menu_del_dia, HOY):
    menu = crear_menu_del_dia()
    menu.descripcion = "Con postre"
    menu.imagen = "m.png"
    sesion.add(menu)
    sesion.commit()

    actualizado = servicios_menus_del_dia.actualizar_menu_del_dia(
        sesion, menu.id, _datos_actualizar(precio=Decimal("3000.00")), hoy=HOY
    )

    assert actualizado.precio == Decimal("3000.00")
    assert actualizado.descripcion is None
    assert actualizado.imagen is None


def test_mdd_42_actualizar_con_id_de_otro_subtipo(sesion, crear_plato, HOY):
    plato = crear_plato()
    sesion.add(plato)
    sesion.commit()

    with pytest.raises(ProductoNoEncontrado):
        servicios_menus_del_dia.actualizar_menu_del_dia(
            sesion, plato.id, _datos_actualizar(), hoy=HOY
        )


def test_mdd_43_actualizar_con_seccion_valida_e_invalida(
    sesion, crear_menu_del_dia, crear_seccion, HOY
):
    menu, seccion = crear_menu_del_dia(), crear_seccion()
    sesion.add_all([menu, seccion])
    sesion.commit()

    actualizado = servicios_menus_del_dia.actualizar_menu_del_dia(
        sesion, menu.id, _datos_actualizar(seccion_id=seccion.id), hoy=HOY
    )
    assert actualizado.seccion_id == seccion.id

    with pytest.raises(SeccionInexistente):
        servicios_menus_del_dia.actualizar_menu_del_dia(
            sesion, menu.id, _datos_actualizar(seccion_id=999), hoy=HOY
        )
