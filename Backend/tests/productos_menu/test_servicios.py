from datetime import date, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.productos.models import Producto
from src.productos_menu import services
from src.productos_menu.exceptions import (
    FechaMenuOcupada,
    FechaMenuPasada,
    MenuDelDiaDadoDeBaja,
    MenuDelDiaInexistente,
    ProductoMenuNoEncontrado,
    ProductoNoMenuDelDia,
)
from src.productos_menu.models import ProductoMenu
from src.productos_menu.schemas import ProductoMenuActualizar, ProductoMenuCrear
from tests.conftest import HOY_FIJO
from src.productos_menu.services import (
    actualizar_fecha_producto_menu,
    crear_producto_menu,
    eliminar_producto_menu,
    obtener_producto_menu,
)


def _estado(sesion):
    """Conjunto persistido (id, menu_del_dia_id, fecha); deja la transacción cerrada."""
    estado = set(
        sesion.execute(
            select(ProductoMenu.id, ProductoMenu.menu_del_dia_id, ProductoMenu.fecha)
        ).all()
    )
    sesion.rollback()
    return estado


# --- 4.2 obtener_producto_menu ---


def test_obtener_producto_menu_existente_devuelve_la_fila(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    _, registro_id = persistir(mdd, crear_producto_menu(mdd))

    registro = obtener_producto_menu(sesion, registro_id)

    assert registro.id == registro_id


def test_obtener_producto_menu_inexistente_lanza_y_revierte(sesion):
    with pytest.raises(ProductoMenuNoEncontrado):
        obtener_producto_menu(sesion, 999)

    assert not sesion.in_transaction()


# --- 4.3 crear_producto_menu ---

F1 = date(2026, 7, 1)
F2 = date(2026, 7, 2)


def _alta(sesion, menu_del_dia_id, fecha):
    return crear_producto_menu(sesion, ProductoMenuCrear(menu_del_dia_id=menu_del_dia_id, fecha=fecha), HOY_FIJO)


def test_pmd_04_alta_valida_persiste_y_devuelve_id(sesion, persistir, crear_menu_del_dia):
    menu_del_dia_id = persistir(crear_menu_del_dia())

    registro = _alta(sesion, menu_del_dia_id, F1)

    assert registro.id is not None
    assert _estado(sesion) == {(registro.id, menu_del_dia_id, F1)}


@pytest.mark.parametrize(
    "fecha",
    [HOY_FIJO, HOY_FIJO + timedelta(days=1), HOY_FIJO + timedelta(days=30)],
    ids=["hoy", "manana", "futura"],
)
def test_pmd_06_07_alta_con_fecha_de_hoy_y_futura(sesion, persistir, crear_menu_del_dia, fecha):
    menu_del_dia_id = persistir(crear_menu_del_dia())

    registro = _alta(sesion, menu_del_dia_id, fecha)

    assert registro.fecha == fecha


@pytest.mark.parametrize(
    "fecha", [HOY_FIJO - timedelta(days=1), date(2020, 1, 1)], ids=["ayer", "lejana"]
)
def test_pmd_05_alta_con_fecha_pasada_se_rechaza_sin_registro(
    sesion, persistir, crear_menu_del_dia, fecha
):
    menu_del_dia_id = persistir(crear_menu_del_dia())

    with pytest.raises(FechaMenuPasada):
        _alta(sesion, menu_del_dia_id, fecha)

    assert not sesion.in_transaction()
    assert _estado(sesion) == set()


def test_fecha_pasada_prevalece_sobre_baja_y_ocupada(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    mdd.dado_de_baja = True
    ayer = HOY_FIJO - timedelta(days=1)
    persistir(mdd, crear_producto_menu(mdd, ayer))

    with pytest.raises(FechaMenuPasada):
        _alta(sesion, 1, ayer)


def test_menu_del_dia_inexistente_prevalece_sobre_fecha_pasada(sesion):
    with pytest.raises(MenuDelDiaInexistente):
        _alta(sesion, 999, HOY_FIJO - timedelta(days=1))


def test_pmd_08_alta_de_un_menu_del_dia(sesion, persistir, crear_menu_del_dia):
    menu_del_dia_id = persistir(crear_menu_del_dia())

    registro = _alta(sesion, menu_del_dia_id, F1)

    assert registro.menu_del_dia_id == menu_del_dia_id


@pytest.mark.parametrize("subtipo", ["plato", "bebida", "postre", "menu", "combo"])
def test_pmd_05_rechaza_producto_que_no_es_menu_del_dia(
    sesion, persistir, crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo, subtipo
):
    plato, postre = crear_plato(), crear_postre()
    producto = {
        "plato": lambda: plato,
        "bebida": crear_bebida,
        "postre": lambda: postre,
        "menu": lambda: crear_menu(plato, postre),
        "combo": crear_combo,
    }[subtipo]()
    ids = persistir(plato, postre, producto)
    menu_del_dia_id = ids[-1]

    with pytest.raises(ProductoNoMenuDelDia) as info:
        _alta(sesion, menu_del_dia_id, F1)

    assert info.value.menu_del_dia_id == menu_del_dia_id
    assert not sesion.in_transaction()
    assert _estado(sesion) == set()


def test_pmd_40_mismo_producto_en_dos_fechas(sesion, persistir, crear_menu_del_dia):
    menu_del_dia_id = persistir(crear_menu_del_dia())

    _alta(sesion, menu_del_dia_id, F1)
    _alta(sesion, menu_del_dia_id, F2)

    assert {fecha for _, _, fecha in _estado(sesion)} == {F1, F2}


def test_pmd_13_menu_del_dia_inexistente(sesion):
    with pytest.raises(MenuDelDiaInexistente) as info:
        _alta(sesion, 999, F1)

    assert info.value.menu_del_dia_id == 999
    assert not sesion.in_transaction()
    assert _estado(sesion) == set()


def test_pmd_14_menu_del_dia_dado_de_baja(sesion, persistir, crear_menu_del_dia):
    menu_del_dia_id = persistir(crear_menu_del_dia(dado_de_baja=True))

    with pytest.raises(MenuDelDiaDadoDeBaja):
        _alta(sesion, menu_del_dia_id, F1)

    assert not sesion.in_transaction()
    assert _estado(sesion) == set()


def test_pmd_15_fecha_ocupada_deja_el_existente_intacto(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, existente_id = persistir(mdd, crear_producto_menu(mdd, F1))
    antes = _estado(sesion)

    with pytest.raises(FechaMenuOcupada):
        _alta(sesion, menu_del_dia_id, F1)

    assert not sesion.in_transaction()
    assert _estado(sesion) == antes == {(existente_id, menu_del_dia_id, F1)}


def test_pmd_17_inexistente_prevalece_sobre_fecha_ocupada(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    persistir(mdd, crear_producto_menu(mdd, F1))

    with pytest.raises(MenuDelDiaInexistente):
        _alta(sesion, 999, F1)


def test_pmd_18_baja_prevalece_sobre_fecha_ocupada(
    sesion, persistir, crear_menu_del_dia, crear_bebida, crear_producto_menu
):
    mdd, dada_de_baja = crear_menu_del_dia(), crear_menu_del_dia()
    dada_de_baja.dado_de_baja = True
    _, baja_id, _ = persistir(mdd, dada_de_baja, crear_producto_menu(mdd, F1))

    with pytest.raises(MenuDelDiaDadoDeBaja):
        _alta(sesion, baja_id, F1)


def test_pmd_19_cada_error_deja_sin_transaccion_y_sin_cambios(
    sesion, persistir, crear_menu_del_dia, crear_plato, crear_producto_menu
):
    mdd, baja, plato = crear_menu_del_dia(), crear_menu_del_dia(), crear_plato()
    baja.dado_de_baja = True
    menu_del_dia_id, baja_id, plato_id, _ = persistir(
        mdd, baja, plato, crear_producto_menu(mdd, F1)
    )
    antes = _estado(sesion)

    for menu_del_dia_id, error in (
        (999, MenuDelDiaInexistente),
        (plato_id, ProductoNoMenuDelDia),
        (baja_id, MenuDelDiaDadoDeBaja),
        (menu_del_dia_id, FechaMenuOcupada),
    ):
        with pytest.raises(error):
            _alta(sesion, menu_del_dia_id, F1)
        assert not sesion.in_transaction()
        assert _estado(sesion) == antes


def test_pmd_20_respaldo_traduce_la_violacion_del_indice_unico(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu, monkeypatch
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, _ = persistir(mdd, crear_producto_menu(mdd, F1))
    antes = _estado(sesion)
    monkeypatch.setattr(services, "_verificar_fecha_libre", lambda *args, **kwargs: None)

    with pytest.raises(FechaMenuOcupada):
        _alta(sesion, menu_del_dia_id, F1)

    assert not sesion.in_transaction()
    assert _estado(sesion) == antes


def test_confirmar_propaga_integrity_error_ajeno_al_indice_de_fecha(sesion, monkeypatch):
    class OrigAjeno(Exception):
        pass

    def commit_ajeno():
        raise IntegrityError("INSERT", {}, OrigAjeno("NOT NULL constraint failed: otra.columna"))

    monkeypatch.setattr(sesion, "commit", commit_ajeno)

    with pytest.raises(IntegrityError):
        services._confirmar(sesion)

    assert not sesion.in_transaction()


# --- 4.4 actualizar_fecha_producto_menu ---

F3 = date(2026, 7, 3)


def _cambio(sesion, registro_id, fecha, **extra):
    return actualizar_fecha_producto_menu(
        sesion, registro_id, ProductoMenuActualizar(fecha=fecha, **extra), HOY_FIJO
    )


def test_pmd_21_mover_a_fecha_libre_libera_la_anterior(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))

    registro = _cambio(sesion, registro_id, F2)

    assert (registro.id, registro.menu_del_dia_id, registro.fecha) == (registro_id, menu_del_dia_id, F2)
    assert _estado(sesion) == {(registro_id, menu_del_dia_id, F2)}
    _alta(sesion, menu_del_dia_id, F1)  # F1 quedó libre


def test_pmd_22_conservar_la_fecha_propia(sesion, persistir, crear_menu_del_dia, crear_producto_menu):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))

    registro = _cambio(sesion, registro_id, F1)

    assert registro.fecha == F1
    assert _estado(sesion) == {(registro_id, menu_del_dia_id, F1)}


def test_pmd_23_fecha_de_otro_registro_deja_ambos_intactos(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    _, primero_id, _ = persistir(
        mdd, crear_producto_menu(mdd, F1), crear_producto_menu(mdd, F2)
    )
    antes = _estado(sesion)

    with pytest.raises(FechaMenuOcupada):
        _cambio(sesion, primero_id, F2)

    assert not sesion.in_transaction()
    assert _estado(sesion) == antes


def test_pmd_24_id_inexistente(sesion):
    with pytest.raises(ProductoMenuNoEncontrado):
        _cambio(sesion, 999, F1)

    assert not sesion.in_transaction()


def test_pmd_29_id_inexistente_prevalece_sobre_fecha_ocupada(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    persistir(mdd, crear_producto_menu(mdd, F1))

    with pytest.raises(ProductoMenuNoEncontrado):
        _cambio(sesion, 999, F1)


@pytest.mark.parametrize("fecha_nueva", [F2, F1], ids=["fecha_libre", "misma_fecha"])
def test_pmd_25_menu_del_dia_dado_de_baja_no_permite_cambiar(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu, fecha_nueva
):
    mdd = crear_menu_del_dia()
    mdd.dado_de_baja = True
    menu_del_dia_id, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))

    with pytest.raises(MenuDelDiaDadoDeBaja):
        _cambio(sesion, registro_id, fecha_nueva)

    assert not sesion.in_transaction()
    assert _estado(sesion) == {(registro_id, menu_del_dia_id, F1)}


def test_pmd_30_baja_prevalece_sobre_fecha_ocupada(
    sesion, persistir, crear_menu_del_dia, crear_bebida, crear_producto_menu
):
    baja, activo = crear_menu_del_dia(), crear_menu_del_dia(nombre="Menú B")
    baja.dado_de_baja = True
    _, _, registro_id, _ = persistir(
        baja, activo, crear_producto_menu(baja, F1), crear_producto_menu(activo, F2)
    )

    with pytest.raises(MenuDelDiaDadoDeBaja):
        _cambio(sesion, registro_id, F2)


def test_pmd_26_producto_id_extra_no_cambia_el_producto(
    sesion, persistir, crear_menu_del_dia, crear_bebida, crear_producto_menu
):
    mdd, mdd_b = crear_menu_del_dia(), crear_menu_del_dia(nombre="Menú B")
    menu_del_dia_id, mdd_b_id, registro_id = persistir(mdd, mdd_b, crear_producto_menu(mdd, F1))

    registro = _cambio(sesion, registro_id, F2, menu_del_dia_id=mdd_b_id)

    assert registro.menu_del_dia_id == menu_del_dia_id
    assert _estado(sesion) == {(registro_id, menu_del_dia_id, F2)}


def test_pmd_31_cada_error_deja_sin_transaccion_y_sin_cambios(
    sesion, persistir, crear_menu_del_dia, crear_bebida, crear_producto_menu
):
    activo, baja = crear_menu_del_dia(), crear_menu_del_dia(nombre="Menú B")
    baja.dado_de_baja = True
    _, _, r1, r2, r3 = persistir(
        activo,
        baja,
        crear_producto_menu(activo, F1),
        crear_producto_menu(activo, F2),
        crear_producto_menu(baja, F3),
    )
    antes = _estado(sesion)

    for registro_id, fecha, error in (
        (999, F1, ProductoMenuNoEncontrado),
        (r3, date(2026, 8, 1), MenuDelDiaDadoDeBaja),
        (r1, F2, FechaMenuOcupada),
    ):
        with pytest.raises(error):
            _cambio(sesion, registro_id, fecha)
        assert not sesion.in_transaction()
        assert _estado(sesion) == antes


def test_actualizar_respaldo_traduce_la_violacion_del_indice_unico(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu, monkeypatch
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, r1, r2 = persistir(
        mdd, crear_producto_menu(mdd, F1), crear_producto_menu(mdd, F2)
    )
    antes = _estado(sesion)
    monkeypatch.setattr(services, "_verificar_fecha_libre", lambda *args, **kwargs: None)

    with pytest.raises(FechaMenuOcupada):
        _cambio(sesion, r1, F2)

    assert not sesion.in_transaction()
    assert _estado(sesion) == antes


# --- 4.5 eliminar_producto_menu ---


def test_pmd_32_borra_la_fila_y_conserva_el_producto(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))

    assert eliminar_producto_menu(sesion, registro_id) is None

    assert _estado(sesion) == set()
    assert sesion.get(Producto, menu_del_dia_id) is not None


def test_pmd_33_id_inexistente(sesion):
    with pytest.raises(ProductoMenuNoEncontrado):
        eliminar_producto_menu(sesion, 999)

    assert not sesion.in_transaction()


def test_pmd_34_borrado_repetido(sesion, persistir, crear_menu_del_dia, crear_producto_menu):
    mdd = crear_menu_del_dia()
    _, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))
    eliminar_producto_menu(sesion, registro_id)

    with pytest.raises(ProductoMenuNoEncontrado):
        eliminar_producto_menu(sesion, registro_id)

    assert not sesion.in_transaction()


def test_pmd_35_menu_del_dia_dado_de_baja_no_impide_el_borrado(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    mdd.dado_de_baja = True
    _, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))

    eliminar_producto_menu(sesion, registro_id)

    assert _estado(sesion) == set()


def test_pmd_36_la_fecha_liberada_puede_reutilizarse(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))
    eliminar_producto_menu(sesion, registro_id)

    nuevo = _alta(sesion, menu_del_dia_id, F1)

    assert _estado(sesion) == {(nuevo.id, menu_del_dia_id, F1)}


@pytest.mark.parametrize(
    "fecha", [HOY_FIJO, HOY_FIJO + timedelta(days=5)], ids=["hoy", "futura"]
)
def test_cambio_a_hoy_o_futura_se_acepta(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu, fecha
):
    mdd = crear_menu_del_dia()
    _, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))

    assert _cambio(sesion, registro_id, fecha).fecha == fecha


@pytest.mark.parametrize(
    "fecha", [HOY_FIJO - timedelta(days=1), date(2020, 1, 1)], ids=["ayer", "lejana"]
)
def test_cambio_a_fecha_pasada_se_rechaza_sin_cambios(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu, fecha
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))

    with pytest.raises(FechaMenuPasada):
        _cambio(sesion, registro_id, fecha)

    assert not sesion.in_transaction()
    assert _estado(sesion) == {(registro_id, menu_del_dia_id, F1)}


def test_cambio_404_prevalece_sobre_fecha_pasada(sesion):
    with pytest.raises(ProductoMenuNoEncontrado):
        _cambio(sesion, 999, HOY_FIJO - timedelta(days=1))


def test_cambio_fecha_pasada_prevalece_sobre_baja(
    sesion, persistir, crear_menu_del_dia, crear_producto_menu
):
    mdd = crear_menu_del_dia()
    mdd.dado_de_baja = True
    _, registro_id = persistir(mdd, crear_producto_menu(mdd, F1))

    with pytest.raises(FechaMenuPasada):
        _cambio(sesion, registro_id, HOY_FIJO - timedelta(days=1))
