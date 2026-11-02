from datetime import timedelta
from decimal import Decimal

import pytest

from src.productos.bebidas import services as servicios_bebidas
from src.productos.bebidas.models import Bebida
from src.productos.bebidas.schemas import BebidaActualizar, BebidaCrear
from src.productos.exceptions import BajaRestringida, NombreDuplicado, ProductoNoEncontrado


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


def test_cat_11_actualizar_bebida_con_id_desconocido(sesion, HOY):
    with pytest.raises(ProductoNoEncontrado):
        servicios_bebidas.actualizar_bebida(sesion, 999, _datos_actualizar(), hoy=HOY)


def test_cat_08_actualizar_bebida_con_id_de_otro_subtipo(sesion, crear_plato, HOY):
    plato = crear_plato()
    sesion.add(plato)
    sesion.commit()

    with pytest.raises(ProductoNoEncontrado):
        servicios_bebidas.actualizar_bebida(sesion, plato.id, _datos_actualizar(), hoy=HOY)


def test_cat_13_actualizar_bebida_es_reemplazo_completo(sesion, crear_bebida, HOY):
    bebida = crear_bebida(es_alcoholica=True)
    bebida.descripcion = "Rubia"
    bebida.imagen = "cerveza.png"
    sesion.add(bebida)
    sesion.commit()

    actualizada = servicios_bebidas.actualizar_bebida(
        sesion, bebida.id, _datos_actualizar(es_alcoholica=False),
        hoy=HOY,
    )

    assert actualizada.es_alcoholica is False
    assert actualizada.descripcion is None
    assert actualizada.imagen is None


def test_cat_26_actualizar_bebida_con_el_mismo_nombre(sesion, crear_bebida, HOY):
    bebida = crear_bebida(nombre="Cerveza")
    sesion.add(bebida)
    sesion.commit()

    actualizada = servicios_bebidas.actualizar_bebida(
        sesion, bebida.id, _datos_actualizar(precio=Decimal("900.00")),
        hoy=HOY,
    )

    assert actualizada.precio == Decimal("900.00")


def test_ld_22_actualizar_bebida_con_dado_de_baja_false_la_reactiva(sesion, crear_bebida, HOY):
    bebida = crear_bebida()
    bebida.dado_de_baja = True
    sesion.add(bebida)
    sesion.commit()

    actualizada = servicios_bebidas.actualizar_bebida(
        sesion, bebida.id, _datos_actualizar(dado_de_baja=False), hoy=HOY
    )

    sesion.expire_all()
    assert actualizada.dado_de_baja is False
    assert sesion.get(Bebida, bebida.id).dado_de_baja is False


def test_ld_11_actualizar_bebida_con_dado_de_baja_true_bloqueada_por_un_combo(
    sesion, crear_bebida, crear_combo, HOY
):
    bebida = crear_bebida()
    combo = crear_combo(bebidas=[bebida], hasta=HOY + timedelta(days=5))
    sesion.add_all([bebida, combo])
    sesion.commit()

    with pytest.raises(BajaRestringida) as error:
        servicios_bebidas.actualizar_bebida(
            sesion, bebida.id, _datos_actualizar(dado_de_baja=True), hoy=HOY
        )

    assert error.value.bloqueantes == [combo.id]
    sesion.expire_all()
    assert sesion.get(Bebida, bebida.id).dado_de_baja is False
