from decimal import Decimal

import pytest

from src.productos.bebidas import services as servicios_bebidas
from src.productos.bebidas.models import Bebida
from src.productos.bebidas.schemas import BebidaActualizar, BebidaCrear
from src.productos.exceptions import NombreDuplicado, ProductoNoEncontrado


def _datos_crear(**cambios):
    datos = {"nombre": "Cerveza", "precio": Decimal("800.00"), "es_alcoholica": True}
    datos.update(cambios)
    return BebidaCrear(**datos)


def _datos_actualizar(**cambios):
    datos = {"nombre": "Cerveza", "precio": Decimal("800.00"), "es_alcoholica": True}
    datos.update(cambios)
    return BebidaActualizar(**datos)


def test_cat_07_crear_bebida_persiste_los_campos_comunes_y_propios(sesion):
    bebida = servicios_bebidas.crear_bebida(
        sesion, _datos_crear(nombre=" Gaseosa ", es_alcoholica=False)
    )

    guardada = sesion.get(Bebida, bebida.id)
    assert guardada.nombre == "Gaseosa"
    assert guardada.nombre_normalizado == "gaseosa"
    assert guardada.es_alcoholica is False
    assert guardada.dado_de_baja is False


def test_cat_21_crear_bebida_con_el_nombre_de_un_plato_activo(sesion, crear_plato):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_bebidas.crear_bebida(sesion, _datos_crear(nombre="Milanesa"))


def test_cat_11_actualizar_bebida_con_id_desconocido(sesion):
    with pytest.raises(ProductoNoEncontrado):
        servicios_bebidas.actualizar_bebida(sesion, 999, _datos_actualizar())


def test_cat_08_actualizar_bebida_con_id_de_otro_subtipo(sesion, crear_plato):
    plato = crear_plato()
    sesion.add(plato)
    sesion.commit()

    with pytest.raises(ProductoNoEncontrado):
        servicios_bebidas.actualizar_bebida(sesion, plato.id, _datos_actualizar())


def test_cat_13_actualizar_bebida_es_reemplazo_completo(sesion, crear_bebida):
    bebida = crear_bebida(es_alcoholica=True)
    bebida.descripcion = "Rubia"
    bebida.imagen = "cerveza.png"
    sesion.add(bebida)
    sesion.commit()

    actualizada = servicios_bebidas.actualizar_bebida(
        sesion, bebida.id, _datos_actualizar(es_alcoholica=False)
    )

    assert actualizada.es_alcoholica is False
    assert actualizada.descripcion is None
    assert actualizada.imagen is None


def test_cat_26_actualizar_bebida_con_el_mismo_nombre(sesion, crear_bebida):
    bebida = crear_bebida(nombre="Cerveza")
    sesion.add(bebida)
    sesion.commit()

    actualizada = servicios_bebidas.actualizar_bebida(
        sesion, bebida.id, _datos_actualizar(precio=Decimal("900.00"))
    )

    assert actualizada.precio == Decimal("900.00")
