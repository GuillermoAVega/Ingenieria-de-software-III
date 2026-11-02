from decimal import Decimal

import pytest

from src.productos.exceptions import BajaRestringida, NombreDuplicado, ProductoNoEncontrado
from src.productos.postres import services as servicios_postres
from src.productos.postres.models import Postre
from src.productos.postres.schemas import PostreActualizar, PostreCrear


def _datos_crear(**cambios):
    datos = {"nombre": "Flan", "precio": Decimal("600.00")}
    datos.update(cambios)
    return PostreCrear(**datos)


def _datos_actualizar(**cambios):
    datos = {"nombre": "Flan", "precio": Decimal("600.00")}
    datos.update(cambios)
    return PostreActualizar(**datos)


def test_cat_07_crear_postre_persiste_los_campos_comunes(sesion):
    postre = servicios_postres.crear_postre(sesion, _datos_crear(nombre=" Flan Mixto "))

    guardado = sesion.get(Postre, postre.id)
    assert guardado.nombre == "Flan Mixto"
    assert guardado.nombre_normalizado == "flan mixto"
    assert guardado.precio == Decimal("600.00")
    assert guardado.dado_de_baja is False


def test_cat_21_crear_postre_con_el_nombre_de_una_bebida_activa(sesion, crear_bebida):
    sesion.add(crear_bebida(nombre="Flan"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_postres.crear_postre(sesion, _datos_crear())


def test_cat_11_actualizar_postre_con_id_desconocido(sesion, HOY):
    with pytest.raises(ProductoNoEncontrado):
        servicios_postres.actualizar_postre(sesion, 999, _datos_actualizar(), hoy=HOY)


def test_cat_08_actualizar_postre_con_id_de_otro_subtipo(sesion, crear_plato, HOY):
    plato = crear_plato()
    sesion.add(plato)
    sesion.commit()

    with pytest.raises(ProductoNoEncontrado):
        servicios_postres.actualizar_postre(sesion, plato.id, _datos_actualizar(), hoy=HOY)


def test_cat_13_actualizar_postre_es_reemplazo_completo(sesion, crear_postre, HOY):
    postre = crear_postre()
    postre.descripcion = "Con dulce de leche"
    postre.imagen = "flan.png"
    sesion.add(postre)
    sesion.commit()

    actualizado = servicios_postres.actualizar_postre(
        sesion, postre.id, _datos_actualizar(precio=Decimal("700.00")),
        hoy=HOY,
    )

    assert actualizado.precio == Decimal("700.00")
    assert actualizado.descripcion is None
    assert actualizado.imagen is None


def test_ld_08_actualizar_postre_con_dado_de_baja_true_sin_bloqueantes_lo_da_de_baja(
    sesion, crear_postre, HOY
):
    postre = crear_postre()
    sesion.add(postre)
    sesion.commit()

    actualizado = servicios_postres.actualizar_postre(
        sesion, postre.id, _datos_actualizar(dado_de_baja=True), hoy=HOY
    )

    sesion.expire_all()
    assert actualizado.dado_de_baja is True
    assert sesion.get(Postre, postre.id).dado_de_baja is True


def test_ld_12_actualizar_postre_con_dado_de_baja_true_bloqueado_por_un_menu(
    sesion, crear_plato, crear_postre, crear_menu, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    sesion.add_all([plato, postre, menu])
    sesion.commit()

    with pytest.raises(BajaRestringida) as error:
        servicios_postres.actualizar_postre(
            sesion, postre.id, _datos_actualizar(dado_de_baja=True), hoy=HOY
        )

    assert error.value.bloqueantes == [menu.id]
    sesion.expire_all()
    assert sesion.get(Postre, postre.id).dado_de_baja is False
