from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy import event

from src.productos import services
from src.productos.combos import services as servicios_combos
from src.productos.combos.exceptions import ComboVencidoInmutable
from src.productos.combos.models import ComboPromocion
from src.productos.combos.schemas import ComboActualizar
from src.productos.exceptions import ProductoNoEncontrado


@pytest.fixture
def combo_vencido(sesion, crear_plato, crear_bebida, crear_combo, HOY):
    """Combo activo con `fecha_hasta` de ayer, con un Plato y una Bebida."""
    plato, bebida = crear_plato(), crear_bebida()
    combo = crear_combo(
        "Combo",
        desde=HOY - timedelta(days=10),
        hasta=HOY - timedelta(days=1),
        platos=[plato],
        bebidas=[bebida],
    )
    sesion.add_all([plato, bebida, combo])
    sesion.commit()
    return combo


def _datos(combo, **cambios):
    """Payload idéntico al estado persistido del combo, salvo `cambios`."""
    datos = {
        "nombre": combo.nombre,
        "precio": combo.precio,
        "descripcion": combo.descripcion,
        "imagen": combo.imagen,
        "fecha_desde": combo.fecha_desde,
        "fecha_hasta": combo.fecha_hasta,
        "platos_ids": combo.platos_ids,
        "bebidas_ids": combo.bebidas_ids,
        "postres_ids": combo.postres_ids,
    }
    datos.update(cambios)
    return ComboActualizar(**datos)


def test_cat_45_editar_un_combo_vencido_es_inmutable(sesion, combo_vencido, HOY):
    datos = _datos(combo_vencido, descripcion="Nueva")

    with pytest.raises(ComboVencidoInmutable):
        servicios_combos.actualizar_combo(sesion, combo_vencido.id, datos, HOY)

    sesion.expire_all()
    assert sesion.get(ComboPromocion, combo_vencido.id).descripcion is None


def test_cat_46_reactivar_un_combo_vencido_de_baja_es_inmutable(sesion, combo_vencido, HOY):
    combo_vencido.dado_de_baja = True
    sesion.commit()

    with pytest.raises(ComboVencidoInmutable):
        servicios_combos.actualizar_combo(
            sesion, combo_vencido.id, _datos(combo_vencido, dado_de_baja=False), HOY
        )

    sesion.expire_all()
    assert sesion.get(ComboPromocion, combo_vencido.id).dado_de_baja is True


def test_vencido_con_dado_de_baja_omitido_es_inmutable(sesion, combo_vencido, HOY):
    with pytest.raises(ComboVencidoInmutable):
        servicios_combos.actualizar_combo(sesion, combo_vencido.id, _datos(combo_vencido), HOY)


def test_cat_47_baja_via_put_de_un_combo_vencido_activo_lo_da_de_baja(
    sesion, combo_vencido, HOY
):
    actualizado = servicios_combos.actualizar_combo(
        sesion, combo_vencido.id, _datos(combo_vencido, dado_de_baja=True), HOY
    )

    sesion.expire_all()
    assert actualizado.dado_de_baja is True
    assert sesion.get(ComboPromocion, combo_vencido.id).dado_de_baja is True


def test_cat_48_baja_repetida_de_un_combo_vencido_no_escribe(sesion, combo_vencido, HOY):
    combo_vencido.dado_de_baja = True
    sesion.commit()
    confirmaciones = []
    event.listen(sesion, "after_commit", lambda _s: confirmaciones.append(1))

    actualizado = servicios_combos.actualizar_combo(
        sesion, combo_vencido.id, _datos(combo_vencido, dado_de_baja=True), HOY
    )

    assert actualizado.dado_de_baja is True
    assert confirmaciones == []


def test_cat_49_baja_con_otros_cambios_sobre_un_combo_vencido_es_inmutable(
    sesion, combo_vencido, HOY
):
    datos = _datos(combo_vencido, dado_de_baja=True, precio=Decimal("1.00"))

    with pytest.raises(ComboVencidoInmutable):
        servicios_combos.actualizar_combo(sesion, combo_vencido.id, datos, HOY)

    sesion.expire_all()
    guardado = sesion.get(ComboPromocion, combo_vencido.id)
    assert guardado.dado_de_baja is False
    assert guardado.precio == Decimal("3000.00")


def test_vencido_inexistente_es_404_antes_que_vencido(sesion, combo_vencido, HOY):
    with pytest.raises(ProductoNoEncontrado):
        servicios_combos.actualizar_combo(sesion, 999, _datos(combo_vencido), HOY)


def test_vencido_se_comprueba_antes_que_los_componentes(sesion, combo_vencido, HOY):
    datos = _datos(combo_vencido, dado_de_baja=False, postres_ids=[999])

    with pytest.raises(ComboVencidoInmutable):
        servicios_combos.actualizar_combo(sesion, combo_vencido.id, datos, HOY)


@pytest.mark.parametrize(
    "cambios",
    [
        {"nombre": "Otro"},
        {"precio": Decimal("3000.01")},
        {"descripcion": "x"},
        {"imagen": "x.png"},
        {"fecha_desde": None},
        {"fecha_hasta": None},
        {"platos_ids": []},
        {"postres_ids": [999]},
    ],
    ids=lambda c: next(iter(c)),
)
def test_sin_otros_cambios_detecta_cada_campo(sesion, combo_vencido, cambios):
    cambios = {
        campo: (getattr(combo_vencido, campo) - timedelta(days=1) if valor is None else valor)
        for campo, valor in cambios.items()
    }

    assert servicios_combos._sin_otros_cambios(combo_vencido, _datos(combo_vencido, **cambios)) is False


def test_sin_otros_cambios_ignora_el_orden_y_compara_precio_como_decimal(
    sesion, combo_vencido
):
    plato_extra = type(combo_vencido.platos[0])(
        nombre="Pizza", nombre_normalizado="pizza", precio=Decimal("10.00"), cant_personas=1
    )
    combo_vencido.platos.append(plato_extra)
    sesion.commit()
    ids_invertidos = list(reversed(combo_vencido.platos_ids))

    datos = _datos(combo_vencido, platos_ids=ids_invertidos, precio=Decimal("3000"))

    assert servicios_combos._sin_otros_cambios(combo_vencido, datos) is True


def test_ld_17_dar_de_baja_un_combo_vencido_activo(sesion, combo_vencido, HOY):
    services.dar_de_baja(sesion, ComboPromocion, combo_vencido.id, HOY)

    sesion.expire_all()
    assert sesion.get(ComboPromocion, combo_vencido.id).dado_de_baja is True


def test_ld_18_baja_via_put_de_un_combo_no_vencido(sesion, crear_plato, crear_combo, HOY):
    plato = crear_plato()
    combo = crear_combo(desde=HOY, hasta=HOY + timedelta(days=5), platos=[plato])
    sesion.add_all([plato, combo])
    sesion.commit()
    datos = _datos(combo, dado_de_baja=True, descripcion="Cambia")

    actualizado = servicios_combos.actualizar_combo(sesion, combo.id, datos, HOY)

    assert actualizado.dado_de_baja is True
    assert actualizado.descripcion == "Cambia"
