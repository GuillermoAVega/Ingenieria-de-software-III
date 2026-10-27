from datetime import timedelta

import pytest

from src.productos import services
from src.productos.exceptions import BajaRestringida
from src.productos.models import Producto


def _persistir(sesion, *objetos):
    sesion.add_all(objetos)
    sesion.commit()


@pytest.fixture
def sin_consulta_de_bloqueantes(monkeypatch):
    def _no_debe_llamarse(*args, **kwargs):
        raise AssertionError("no debía consultar los bloqueantes")

    monkeypatch.setattr(services, "buscar_bloqueantes", _no_debe_llamarse)


def test_ld_03_nuevo_estado_none_no_cambia_nada_ni_consulta_bloqueantes(
    sesion, crear_plato, sin_consulta_de_bloqueantes, HOY
):
    plato = crear_plato()
    _persistir(sesion, plato)

    services.aplicar_cambio_estado(sesion, plato, None, HOY)

    assert plato.dado_de_baja is False


def test_ld_03_baja_de_un_producto_ya_dado_de_baja_es_idempotente(
    sesion, crear_plato, sin_consulta_de_bloqueantes, HOY
):
    plato = crear_plato(dado_de_baja=True)
    _persistir(sesion, plato)

    services.aplicar_cambio_estado(sesion, plato, True, HOY)

    assert plato.dado_de_baja is True


def test_estado_igual_al_actual_activo_no_consulta_bloqueantes(
    sesion, crear_plato, sin_consulta_de_bloqueantes, HOY
):
    plato = crear_plato()
    _persistir(sesion, plato)

    services.aplicar_cambio_estado(sesion, plato, False, HOY)

    assert plato.dado_de_baja is False


def test_ld_10_baja_de_plato_con_menu_activo_lanza_baja_restringida(
    sesion, crear_plato, crear_postre, crear_menu, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    _persistir(sesion, plato, postre, menu)

    with pytest.raises(BajaRestringida) as error:
        services.aplicar_cambio_estado(sesion, plato, True, HOY)

    assert error.value.bloqueantes == [menu.id]


def test_ld_11_baja_de_bebida_con_combo_activo_lanza_baja_restringida(
    sesion, crear_bebida, crear_combo, HOY
):
    bebida = crear_bebida()
    combo = crear_combo(bebidas=[bebida], hasta=HOY + timedelta(days=5))
    _persistir(sesion, bebida, combo)

    with pytest.raises(BajaRestringida) as error:
        services.aplicar_cambio_estado(sesion, bebida, True, HOY)

    assert error.value.bloqueantes == [combo.id]


def test_ld_12_baja_de_postre_con_combo_futuro_lanza_baja_restringida(
    sesion, crear_postre, crear_combo, HOY
):
    postre = crear_postre()
    combo = crear_combo(
        postres=[postre], desde=HOY + timedelta(days=10), hasta=HOY + timedelta(days=20)
    )
    _persistir(sesion, postre, combo)

    with pytest.raises(BajaRestringida) as error:
        services.aplicar_cambio_estado(sesion, postre, True, HOY)

    assert error.value.bloqueantes == [combo.id]


def test_ld_13_multiples_bloqueantes_quedan_ordenados_en_la_excepcion(
    sesion, crear_plato, crear_postre, crear_menu, crear_combo, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    combo = crear_combo(platos=[plato], hasta=HOY + timedelta(days=5))
    _persistir(sesion, plato, postre, menu, combo)

    with pytest.raises(BajaRestringida) as error:
        services.aplicar_cambio_estado(sesion, plato, True, HOY)

    assert error.value.bloqueantes == sorted([menu.id, combo.id])


def test_ld_14_baja_con_compuestos_dados_de_baja_o_vencidos_procede(
    sesion, crear_plato, crear_postre, crear_menu, crear_combo, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    menu.dado_de_baja = True
    combo = crear_combo(
        platos=[plato], desde=HOY - timedelta(days=30), hasta=HOY - timedelta(days=1)
    )
    _persistir(sesion, plato, postre, menu, combo)

    services.aplicar_cambio_estado(sesion, plato, True, HOY)

    assert plato.dado_de_baja is True


def test_ld_15_baja_con_combo_activo_vencido_procede(sesion, crear_bebida, crear_combo, HOY):
    bebida = crear_bebida()
    combo = crear_combo(
        bebidas=[bebida], desde=HOY - timedelta(days=30), hasta=HOY - timedelta(days=1)
    )
    _persistir(sesion, bebida, combo)

    services.aplicar_cambio_estado(sesion, bebida, True, HOY)

    assert bebida.dado_de_baja is True


def test_ld_16_ld_18_baja_de_menu_y_de_combo_no_tiene_restriccion(
    sesion, crear_plato, crear_postre, crear_menu, crear_combo, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    combo = crear_combo(platos=[plato], hasta=HOY + timedelta(days=5))
    _persistir(sesion, plato, postre, menu, combo)

    services.aplicar_cambio_estado(sesion, menu, True, HOY)
    services.aplicar_cambio_estado(sesion, combo, True, HOY)

    assert menu.dado_de_baja is True
    assert combo.dado_de_baja is True
    # Los componentes quedan intactos
    assert plato.dado_de_baja is False
    assert postre.dado_de_baja is False


def test_ld_23_tras_baja_restringida_el_estado_persistido_no_cambia(
    sesion, crear_plato, crear_postre, crear_menu, HOY
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    _persistir(sesion, plato, postre, menu)

    with pytest.raises(BajaRestringida):
        services.aplicar_cambio_estado(sesion, plato, True, HOY)
    sesion.rollback()

    sesion.expire_all()
    assert sesion.get(Producto, plato.id).dado_de_baja is False
    assert sesion.get(Producto, menu.id).dado_de_baja is False
