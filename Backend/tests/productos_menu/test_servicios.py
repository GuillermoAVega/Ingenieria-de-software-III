from datetime import date, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.productos.models import Producto
from src.productos_menu import services
from src.productos_menu.exceptions import (
    FechaMenuOcupada,
    ProductoDadoDeBaja,
    ProductoInexistente,
    ProductoMenuNoEncontrado,
)
from src.productos_menu.models import ProductoMenu
from src.productos_menu.schemas import ProductoMenuActualizar, ProductoMenuCrear
from src.productos_menu.services import (
    actualizar_fecha_producto_menu,
    crear_producto_menu,
    eliminar_producto_menu,
    obtener_producto_menu,
)


def _estado(sesion):
    """Conjunto persistido (id, producto_id, fecha); deja la transacción cerrada."""
    estado = set(
        sesion.execute(
            select(ProductoMenu.id, ProductoMenu.producto_id, ProductoMenu.fecha)
        ).all()
    )
    sesion.rollback()
    return estado


# --- 4.2 obtener_producto_menu ---


def test_obtener_producto_menu_existente_devuelve_la_fila(
    sesion, persistir, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    _, registro_id = persistir(plato, crear_producto_menu(plato))

    registro = obtener_producto_menu(sesion, registro_id)

    assert registro.id == registro_id


def test_obtener_producto_menu_inexistente_lanza_y_revierte(sesion):
    with pytest.raises(ProductoMenuNoEncontrado):
        obtener_producto_menu(sesion, 999)

    assert not sesion.in_transaction()


# --- 4.3 crear_producto_menu ---

F1 = date(2026, 7, 1)
F2 = date(2026, 7, 2)


def _alta(sesion, producto_id, fecha):
    return crear_producto_menu(sesion, ProductoMenuCrear(producto_id=producto_id, fecha=fecha))


def test_pmd_04_alta_valida_persiste_y_devuelve_id(sesion, persistir, crear_plato):
    plato_id = persistir(crear_plato())

    registro = _alta(sesion, plato_id, F1)

    assert registro.id is not None
    assert _estado(sesion) == {(registro.id, plato_id, F1)}


@pytest.mark.parametrize(
    "fecha",
    [date(2020, 1, 1), date.today(), date.today() + timedelta(days=30)],
    ids=["pasada", "hoy", "futura"],
)
def test_pmd_05_06_07_alta_con_fecha_pasada_hoy_y_futura(sesion, persistir, crear_plato, fecha):
    plato_id = persistir(crear_plato())

    registro = _alta(sesion, plato_id, fecha)

    assert registro.fecha == fecha


def test_pmd_08_alta_de_los_cinco_subtipos(
    sesion, persistir, crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo
):
    plato, postre = crear_plato(), crear_postre()
    menu = crear_menu(plato, postre)
    productos = [plato, postre, crear_bebida(), menu, crear_combo()]
    ids = persistir(*productos)

    for indice, producto_id in enumerate(ids):
        registro = _alta(sesion, producto_id, F1 + timedelta(days=indice))
        assert registro.producto_id == producto_id

    assert len(_estado(sesion)) == 5


def test_pmd_40_mismo_producto_en_dos_fechas(sesion, persistir, crear_plato):
    plato_id = persistir(crear_plato())

    _alta(sesion, plato_id, F1)
    _alta(sesion, plato_id, F2)

    assert {fecha for _, _, fecha in _estado(sesion)} == {F1, F2}


def test_pmd_13_producto_inexistente(sesion):
    with pytest.raises(ProductoInexistente) as info:
        _alta(sesion, 999, F1)

    assert info.value.producto_id == 999
    assert not sesion.in_transaction()
    assert _estado(sesion) == set()


def test_pmd_14_producto_dado_de_baja(sesion, persistir, crear_plato):
    plato_id = persistir(crear_plato(dado_de_baja=True))

    with pytest.raises(ProductoDadoDeBaja):
        _alta(sesion, plato_id, F1)

    assert not sesion.in_transaction()
    assert _estado(sesion) == set()


def test_pmd_15_fecha_ocupada_deja_el_existente_intacto(
    sesion, persistir, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    plato_id, existente_id = persistir(plato, crear_producto_menu(plato, F1))
    antes = _estado(sesion)

    with pytest.raises(FechaMenuOcupada):
        _alta(sesion, plato_id, F1)

    assert not sesion.in_transaction()
    assert _estado(sesion) == antes == {(existente_id, plato_id, F1)}


def test_pmd_17_inexistente_prevalece_sobre_fecha_ocupada(
    sesion, persistir, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    persistir(plato, crear_producto_menu(plato, F1))

    with pytest.raises(ProductoInexistente):
        _alta(sesion, 999, F1)


def test_pmd_18_baja_prevalece_sobre_fecha_ocupada(
    sesion, persistir, crear_plato, crear_bebida, crear_producto_menu
):
    plato, dada_de_baja = crear_plato(), crear_bebida()
    dada_de_baja.dado_de_baja = True
    _, baja_id, _ = persistir(plato, dada_de_baja, crear_producto_menu(plato, F1))

    with pytest.raises(ProductoDadoDeBaja):
        _alta(sesion, baja_id, F1)


def test_pmd_19_cada_error_deja_sin_transaccion_y_sin_cambios(
    sesion, persistir, crear_plato, crear_bebida, crear_producto_menu
):
    plato, baja = crear_plato(), crear_bebida()
    baja.dado_de_baja = True
    plato_id, baja_id, _ = persistir(plato, baja, crear_producto_menu(plato, F1))
    antes = _estado(sesion)

    for producto_id, error in (
        (999, ProductoInexistente),
        (baja_id, ProductoDadoDeBaja),
        (plato_id, FechaMenuOcupada),
    ):
        with pytest.raises(error):
            _alta(sesion, producto_id, F1)
        assert not sesion.in_transaction()
        assert _estado(sesion) == antes


def test_pmd_20_respaldo_traduce_la_violacion_del_indice_unico(
    sesion, persistir, crear_plato, crear_producto_menu, monkeypatch
):
    plato = crear_plato()
    plato_id, _ = persistir(plato, crear_producto_menu(plato, F1))
    antes = _estado(sesion)
    monkeypatch.setattr(services, "_verificar_fecha_libre", lambda *args, **kwargs: None)

    with pytest.raises(FechaMenuOcupada):
        _alta(sesion, plato_id, F1)

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
        sesion, registro_id, ProductoMenuActualizar(fecha=fecha, **extra)
    )


def test_pmd_21_mover_a_fecha_libre_libera_la_anterior(
    sesion, persistir, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    plato_id, registro_id = persistir(plato, crear_producto_menu(plato, F1))

    registro = _cambio(sesion, registro_id, F2)

    assert (registro.id, registro.producto_id, registro.fecha) == (registro_id, plato_id, F2)
    assert _estado(sesion) == {(registro_id, plato_id, F2)}
    _alta(sesion, plato_id, F1)  # F1 quedó libre


def test_pmd_22_conservar_la_fecha_propia(sesion, persistir, crear_plato, crear_producto_menu):
    plato = crear_plato()
    plato_id, registro_id = persistir(plato, crear_producto_menu(plato, F1))

    registro = _cambio(sesion, registro_id, F1)

    assert registro.fecha == F1
    assert _estado(sesion) == {(registro_id, plato_id, F1)}


def test_pmd_23_fecha_de_otro_registro_deja_ambos_intactos(
    sesion, persistir, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    _, primero_id, _ = persistir(
        plato, crear_producto_menu(plato, F1), crear_producto_menu(plato, F2)
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
    sesion, persistir, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    persistir(plato, crear_producto_menu(plato, F1))

    with pytest.raises(ProductoMenuNoEncontrado):
        _cambio(sesion, 999, F1)


@pytest.mark.parametrize("fecha_nueva", [F2, F1], ids=["fecha_libre", "misma_fecha"])
def test_pmd_25_producto_dado_de_baja_no_permite_cambiar(
    sesion, persistir, crear_plato, crear_producto_menu, fecha_nueva
):
    plato = crear_plato()
    plato.dado_de_baja = True
    plato_id, registro_id = persistir(plato, crear_producto_menu(plato, F1))

    with pytest.raises(ProductoDadoDeBaja):
        _cambio(sesion, registro_id, fecha_nueva)

    assert not sesion.in_transaction()
    assert _estado(sesion) == {(registro_id, plato_id, F1)}


def test_pmd_30_baja_prevalece_sobre_fecha_ocupada(
    sesion, persistir, crear_plato, crear_bebida, crear_producto_menu
):
    baja, activo = crear_plato(), crear_bebida()
    baja.dado_de_baja = True
    _, _, registro_id, _ = persistir(
        baja, activo, crear_producto_menu(baja, F1), crear_producto_menu(activo, F2)
    )

    with pytest.raises(ProductoDadoDeBaja):
        _cambio(sesion, registro_id, F2)


def test_pmd_26_producto_id_extra_no_cambia_el_producto(
    sesion, persistir, crear_plato, crear_bebida, crear_producto_menu
):
    plato, bebida = crear_plato(), crear_bebida()
    plato_id, bebida_id, registro_id = persistir(plato, bebida, crear_producto_menu(plato, F1))

    registro = _cambio(sesion, registro_id, F2, producto_id=bebida_id)

    assert registro.producto_id == plato_id
    assert _estado(sesion) == {(registro_id, plato_id, F2)}


def test_pmd_31_cada_error_deja_sin_transaccion_y_sin_cambios(
    sesion, persistir, crear_plato, crear_bebida, crear_producto_menu
):
    activo, baja = crear_plato(), crear_bebida()
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
        (r3, date(2026, 8, 1), ProductoDadoDeBaja),
        (r1, F2, FechaMenuOcupada),
    ):
        with pytest.raises(error):
            _cambio(sesion, registro_id, fecha)
        assert not sesion.in_transaction()
        assert _estado(sesion) == antes


def test_actualizar_respaldo_traduce_la_violacion_del_indice_unico(
    sesion, persistir, crear_plato, crear_producto_menu, monkeypatch
):
    plato = crear_plato()
    plato_id, r1, r2 = persistir(
        plato, crear_producto_menu(plato, F1), crear_producto_menu(plato, F2)
    )
    antes = _estado(sesion)
    monkeypatch.setattr(services, "_verificar_fecha_libre", lambda *args, **kwargs: None)

    with pytest.raises(FechaMenuOcupada):
        _cambio(sesion, r1, F2)

    assert not sesion.in_transaction()
    assert _estado(sesion) == antes


# --- 4.5 eliminar_producto_menu ---


def test_pmd_32_borra_la_fila_y_conserva_el_producto(
    sesion, persistir, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    plato_id, registro_id = persistir(plato, crear_producto_menu(plato, F1))

    assert eliminar_producto_menu(sesion, registro_id) is None

    assert _estado(sesion) == set()
    assert sesion.get(Producto, plato_id) is not None


def test_pmd_33_id_inexistente(sesion):
    with pytest.raises(ProductoMenuNoEncontrado):
        eliminar_producto_menu(sesion, 999)

    assert not sesion.in_transaction()


def test_pmd_34_borrado_repetido(sesion, persistir, crear_plato, crear_producto_menu):
    plato = crear_plato()
    _, registro_id = persistir(plato, crear_producto_menu(plato, F1))
    eliminar_producto_menu(sesion, registro_id)

    with pytest.raises(ProductoMenuNoEncontrado):
        eliminar_producto_menu(sesion, registro_id)

    assert not sesion.in_transaction()


def test_pmd_35_producto_dado_de_baja_no_impide_el_borrado(
    sesion, persistir, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    plato.dado_de_baja = True
    _, registro_id = persistir(plato, crear_producto_menu(plato, F1))

    eliminar_producto_menu(sesion, registro_id)

    assert _estado(sesion) == set()


def test_pmd_36_la_fecha_liberada_puede_reutilizarse(
    sesion, persistir, crear_plato, crear_producto_menu
):
    plato = crear_plato()
    plato_id, registro_id = persistir(plato, crear_producto_menu(plato, F1))
    eliminar_producto_menu(sesion, registro_id)

    nuevo = _alta(sesion, plato_id, F1)

    assert _estado(sesion) == {(nuevo.id, plato_id, F1)}
