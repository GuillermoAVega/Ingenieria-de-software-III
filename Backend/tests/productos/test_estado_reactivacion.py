import pytest

from src.productos import services
from src.productos.exceptions import (
    BajaRestringida,
    ComponenteInactivo,
    NombreDuplicado,
    ProductoNoEncontrado,
)
from src.productos.models import Producto
from src.productos.platos.models import Plato
from src.productos.platos.schemas import PlatoActualizar


def _persistir(sesion, *objetos):
    sesion.add_all(objetos)
    sesion.commit()


def test_ld_09_reactivar_un_plato_dado_de_baja_lo_deja_activo(sesion, crear_plato, HOY):
    plato = crear_plato(dado_de_baja=True)
    _persistir(sesion, plato)

    services.aplicar_cambio_estado(sesion, plato, False, HOY)

    assert plato.dado_de_baja is False


def test_ld_22_reactivar_una_bebida_con_nombre_unico_la_deja_activa(
    sesion, crear_bebida, crear_plato, HOY
):
    bebida = crear_bebida(nombre="Cerveza")
    bebida.dado_de_baja = True
    _persistir(sesion, bebida, crear_plato(nombre="Milanesa"))

    services.aplicar_cambio_estado(sesion, bebida, False, HOY)

    assert bebida.dado_de_baja is False


def test_ld_21_reactivar_con_nombre_activo_duplicado_lanza_nombre_duplicado(
    sesion, crear_plato, crear_bebida, HOY
):
    plato = crear_plato(nombre="Milanesa", dado_de_baja=True)
    _persistir(sesion, plato, crear_bebida(nombre="MILANESA"))

    with pytest.raises(NombreDuplicado):
        services.aplicar_cambio_estado(sesion, plato, False, HOY)

    assert plato.dado_de_baja is True


def test_reactivar_compara_el_nombre_indicado_y_no_el_actual(
    sesion, crear_plato, crear_bebida, HOY
):
    plato = crear_plato(nombre="Milanesa", dado_de_baja=True)
    _persistir(sesion, plato, crear_bebida(nombre="Milanesa"))

    # El PUT lo renombra a un nombre libre: el nombre viejo ya no compite
    services.aplicar_cambio_estado(sesion, plato, False, HOY, nombre="Pizza")
    assert plato.dado_de_baja is False

    plato.dado_de_baja = True
    with pytest.raises(NombreDuplicado):
        services.aplicar_cambio_estado(sesion, plato, False, HOY, nombre="Milanesa")


def test_verificar_reactivacion_se_invoca_antes_de_la_unicidad_y_su_error_se_propaga(
    sesion, crear_plato, crear_bebida, HOY
):
    plato = crear_plato(nombre="Milanesa", dado_de_baja=True)
    # Hay un nombre duplicado: el gancho debe fallar primero
    _persistir(sesion, plato, crear_bebida(nombre="Milanesa"))
    recibidos = []

    def _gancho(producto):
        recibidos.append(producto)
        raise ComponenteInactivo([7])

    with pytest.raises(ComponenteInactivo):
        services.aplicar_cambio_estado(
            sesion, plato, False, HOY, verificar_reactivacion=_gancho
        )

    assert recibidos == [plato]
    assert plato.dado_de_baja is True


def test_verificar_reactivacion_no_se_invoca_en_una_baja_ni_sin_cambio(
    sesion, crear_plato, HOY
):
    plato = crear_plato()
    _persistir(sesion, plato)

    def _gancho(producto):
        raise AssertionError("no debía invocarse")

    services.aplicar_cambio_estado(sesion, plato, True, HOY, verificar_reactivacion=_gancho)
    services.aplicar_cambio_estado(sesion, plato, True, HOY, verificar_reactivacion=_gancho)

    assert plato.dado_de_baja is True


def test_ld_01_dar_de_baja_no_borra_la_fila(sesion, crear_plato, HOY):
    plato = crear_plato()
    _persistir(sesion, plato)

    services.dar_de_baja(sesion, Plato, plato.id, HOY)

    sesion.expire_all()
    guardado = sesion.get(Producto, plato.id)
    assert guardado is not None
    assert guardado.dado_de_baja is True


def test_ld_02_dar_de_baja_con_id_desconocido_o_de_otro_subtipo(sesion, crear_bebida, HOY):
    bebida = crear_bebida()
    _persistir(sesion, bebida)

    with pytest.raises(ProductoNoEncontrado):
        services.dar_de_baja(sesion, Plato, 999, HOY)
    with pytest.raises(ProductoNoEncontrado):
        services.dar_de_baja(sesion, Plato, bebida.id, HOY)

    assert bebida.dado_de_baja is False


def test_ld_03_dar_de_baja_repetido_es_idempotente(sesion, crear_plato, HOY):
    plato = crear_plato()
    _persistir(sesion, plato)

    services.dar_de_baja(sesion, Plato, plato.id, HOY)
    services.dar_de_baja(sesion, Plato, plato.id, HOY)

    sesion.expire_all()
    assert sesion.get(Plato, plato.id).dado_de_baja is True


def test_ld_10_ld_23_dar_de_baja_bloqueado_no_cambia_el_estado(
    sesion, crear_plato, crear_postre, crear_menu, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    _persistir(sesion, plato, postre, menu)

    with pytest.raises(BajaRestringida) as error:
        services.dar_de_baja(sesion, Plato, plato.id, HOY)

    assert error.value.bloqueantes == [menu.id]
    sesion.expire_all()
    assert sesion.get(Plato, plato.id).dado_de_baja is False
    assert sesion.get(Producto, menu.id).dado_de_baja is False


def test_actualizar_producto_revierte_la_sesion_si_el_gancho_de_reactivacion_falla(
    sesion, crear_plato, HOY
):
    plato = crear_plato(dado_de_baja=True)
    _persistir(sesion, plato)
    datos = PlatoActualizar(
        nombre="Milanesa", precio="1500.00", cant_personas=2, dado_de_baja=False
    )

    def gancho(_producto):
        raise ComponenteInactivo([7])

    with pytest.raises(ComponenteInactivo):
        services.actualizar_producto(
            sesion, Plato, plato.id, datos, HOY, verificar_reactivacion=gancho, cant_personas=2
        )

    assert not sesion.in_transaction()
