from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.productos.combos import services as servicios_combos
from src.productos.combos.exceptions import FechaHastaVencida
from src.productos.combos.models import ComboPromocion
from src.productos.combos.schemas import ComboActualizar, ComboCrear
from src.productos.exceptions import (
    ComponenteInactivo,
    ComponenteInvalido,
    NombreDuplicado,
    ProductoNoEncontrado,
    SeccionInexistente,
)
from src.productos.models import Producto


@pytest.fixture
def componentes(sesion, crear_plato, crear_bebida, crear_postre):
    """Un Plato, una Bebida y un Postre activos persistidos."""
    plato, bebida, postre = crear_plato(), crear_bebida(), crear_postre()
    sesion.add_all([plato, bebida, postre])
    sesion.commit()
    return plato, bebida, postre


def _datos(HOY, **cambios):
    datos = {
        "nombre": "Combo",
        "precio": Decimal("3000.00"),
        "fecha_desde": HOY,
        "fecha_hasta": HOY + timedelta(days=10),
        "platos_ids": [],
        "bebidas_ids": [],
        "postres_ids": [],
    }
    datos.update(cambios)
    return ComboCrear(**datos)


def _datos_actualizar(HOY, **cambios):
    datos = _datos(HOY, **cambios).model_dump()
    if "dado_de_baja" in cambios:
        datos["dado_de_baja"] = cambios["dado_de_baja"]
    return ComboActualizar(**datos)


@pytest.fixture
def combo_persistido(sesion, componentes, crear_combo, HOY):
    """Combo activo y vigente con los tres componentes."""
    plato, bebida, postre = componentes
    combo = crear_combo(
        "Combo",
        desde=HOY,
        hasta=HOY + timedelta(days=10),
        platos=[plato],
        bebidas=[bebida],
        postres=[postre],
    )
    sesion.add(combo)
    sesion.commit()
    return combo


def test_cat_34_crear_combo_con_componentes_activos_persiste(sesion, componentes, HOY):
    plato, bebida, postre = componentes

    combo = servicios_combos.crear_combo(
        sesion,
        _datos(
            HOY,
            nombre="  Combo Verano ",
            platos_ids=[plato.id],
            bebidas_ids=[bebida.id],
            postres_ids=[postre.id],
        ),
        HOY,
    )

    guardado = sesion.get(ComboPromocion, combo.id)
    assert guardado.nombre == "Combo Verano"
    assert guardado.nombre_normalizado == "combo verano"
    assert guardado.precio == Decimal("3000.00")
    assert guardado.fecha_desde == HOY
    assert guardado.platos_ids == [plato.id]
    assert guardado.bebidas_ids == [bebida.id]
    assert guardado.postres_ids == [postre.id]
    assert guardado.dado_de_baja is False


def test_cat_36_crear_combo_con_un_solo_componente_en_una_lista(sesion, componentes, HOY):
    _, bebida, _ = componentes

    combo = servicios_combos.crear_combo(sesion, _datos(HOY, bebidas_ids=[bebida.id]), HOY)

    assert combo.platos_ids == []
    assert combo.bebidas_ids == [bebida.id]
    assert combo.postres_ids == []


@pytest.mark.parametrize("id_ajeno", ["plato", "inexistente"])
def test_cat_38_bebidas_ids_con_id_de_otro_tipo_o_inexistente(
    sesion, componentes, HOY, id_ajeno
):
    plato, bebida, _ = componentes
    ajeno = plato.id if id_ajeno == "plato" else 999

    with pytest.raises(ComponenteInvalido) as error:
        servicios_combos.crear_combo(
            sesion, _datos(HOY, bebidas_ids=[bebida.id, ajeno]), HOY
        )

    assert error.value.campo == "bebidas_ids"
    assert error.value.ids == [ajeno]
    assert not sesion.scalars(select(ComboPromocion)).all()


def test_cat_39_crear_combo_con_bebida_dada_de_baja_es_componente_inactivo(
    sesion, componentes, HOY
):
    plato, bebida, _ = componentes
    bebida.dado_de_baja = True
    sesion.commit()

    with pytest.raises(ComponenteInactivo) as error:
        servicios_combos.crear_combo(
            sesion, _datos(HOY, platos_ids=[plato.id], bebidas_ids=[bebida.id]), HOY
        )

    assert error.value.ids == [bebida.id]
    assert not sesion.scalars(select(ComboPromocion)).all()


def test_cat_40_crear_combo_con_fecha_hasta_vencida(sesion, componentes, HOY):
    plato, _, _ = componentes
    datos = _datos(
        HOY,
        fecha_desde=HOY - timedelta(days=5),
        fecha_hasta=HOY - timedelta(days=1),
        platos_ids=[plato.id],
    )

    with pytest.raises(FechaHastaVencida):
        servicios_combos.crear_combo(sesion, datos, HOY)

    assert not sesion.scalars(select(ComboPromocion)).all()


def test_crear_combo_con_fecha_hasta_igual_a_hoy_se_acepta(sesion, componentes, HOY):
    plato, _, _ = componentes

    combo = servicios_combos.crear_combo(
        sesion, _datos(HOY, fecha_hasta=HOY, platos_ids=[plato.id]), HOY
    )

    assert combo.fecha_hasta == HOY


def test_cat_21_crear_combo_con_nombre_activo_duplicado(sesion, componentes, HOY):
    plato, _, _ = componentes

    with pytest.raises(NombreDuplicado):
        servicios_combos.crear_combo(
            sesion, _datos(HOY, nombre="MILANESA", platos_ids=[plato.id]), HOY
        )

    assert not sesion.scalars(select(ComboPromocion)).all()


def test_crear_combo_con_error_no_deja_filas_parciales(sesion, componentes, HOY):
    plato, bebida, _ = componentes
    bebida.dado_de_baja = True
    sesion.commit()

    with pytest.raises(ComponenteInactivo):
        servicios_combos.crear_combo(
            sesion, _datos(HOY, platos_ids=[plato.id], bebidas_ids=[bebida.id]), HOY
        )

    assert not sesion.in_transaction()
    assert sesion.scalars(select(Producto).where(Producto.tipo == "combo_promocion")).all() == []


def _ids_actuales(componentes):
    plato, bebida, postre = componentes
    return {
        "platos_ids": [plato.id],
        "bebidas_ids": [bebida.id],
        "postres_ids": [postre.id],
    }


def test_actualizar_combo_reemplaza_el_objeto_y_las_listas_completas(
    sesion, combo_persistido, componentes, crear_plato, HOY
):
    _, bebida, _ = componentes
    plato_nuevo = crear_plato("Pizza")
    sesion.add(plato_nuevo)
    sesion.commit()

    actualizado = servicios_combos.actualizar_combo(
        sesion,
        combo_persistido.id,
        _datos_actualizar(
            HOY, nombre="Combo nuevo", platos_ids=[plato_nuevo.id], bebidas_ids=[bebida.id]
        ),
        HOY,
    )

    assert actualizado.nombre == "Combo nuevo"
    assert actualizado.platos_ids == [plato_nuevo.id]
    assert actualizado.bebidas_ids == [bebida.id]
    assert actualizado.postres_ids == []
    assert actualizado.descripcion is None
    assert actualizado.dado_de_baja is False


def test_actualizar_combo_desconocido_es_404_antes_que_los_componentes(sesion, HOY):
    with pytest.raises(ProductoNoEncontrado):
        servicios_combos.actualizar_combo(
            sesion, 999, _datos_actualizar(HOY, platos_ids=[998]), HOY
        )


def test_cat_42_actualizar_combo_activo_con_componente_inactivo_no_cambia_nada(
    sesion, combo_persistido, componentes, crear_bebida, HOY
):
    bebida_inactiva = crear_bebida("Vino")
    bebida_inactiva.dado_de_baja = True
    sesion.add(bebida_inactiva)
    sesion.commit()
    ids = {**_ids_actuales(componentes), "bebidas_ids": [bebida_inactiva.id]}

    with pytest.raises(ComponenteInactivo) as error:
        servicios_combos.actualizar_combo(
            sesion, combo_persistido.id, _datos_actualizar(HOY, nombre="Otro", **ids), HOY
        )

    sesion.expire_all()
    guardado = sesion.get(ComboPromocion, combo_persistido.id)
    assert error.value.ids == [bebida_inactiva.id]
    assert guardado.nombre == "Combo"
    assert guardado.bebidas_ids == [componentes[1].id]


@pytest.mark.parametrize("dado_de_baja", [True, None], ids=["true", "omitido"])
def test_cat_43_editar_combo_de_baja_con_componente_inactivo_manteniendolo_de_baja(
    sesion, combo_persistido, componentes, HOY, dado_de_baja
):
    combo_persistido.dado_de_baja = True
    componentes[0].dado_de_baja = True
    sesion.commit()

    actualizado = servicios_combos.actualizar_combo(
        sesion,
        combo_persistido.id,
        _datos_actualizar(
            HOY, descripcion="Nueva", dado_de_baja=dado_de_baja, **_ids_actuales(componentes)
        ),
        HOY,
    )

    assert actualizado.descripcion == "Nueva"
    assert actualizado.dado_de_baja is True


def test_cat_44_combo_de_baja_con_componente_inexistente_es_invalido(
    sesion, combo_persistido, componentes, HOY
):
    combo_persistido.dado_de_baja = True
    sesion.commit()
    ids = {**_ids_actuales(componentes), "postres_ids": [999]}

    with pytest.raises(ComponenteInvalido) as error:
        servicios_combos.actualizar_combo(
            sesion, combo_persistido.id, _datos_actualizar(HOY, dado_de_baja=True, **ids), HOY
        )

    assert error.value.campo == "postres_ids"
    assert error.value.ids == [999]


def test_ld_20_reactivar_combo_con_componentes_activos(
    sesion, combo_persistido, componentes, HOY
):
    combo_persistido.dado_de_baja = True
    sesion.commit()

    actualizado = servicios_combos.actualizar_combo(
        sesion,
        combo_persistido.id,
        _datos_actualizar(HOY, dado_de_baja=False, **_ids_actuales(componentes)),
        HOY,
    )

    assert actualizado.dado_de_baja is False


def test_ld_19_reactivar_combo_con_componente_inactivo_sigue_de_baja(
    sesion, combo_persistido, componentes, HOY
):
    combo_persistido.dado_de_baja = True
    componentes[2].dado_de_baja = True
    sesion.commit()

    with pytest.raises(ComponenteInactivo) as error:
        servicios_combos.actualizar_combo(
            sesion,
            combo_persistido.id,
            _datos_actualizar(HOY, dado_de_baja=False, **_ids_actuales(componentes)),
            HOY,
        )

    sesion.expire_all()
    assert error.value.ids == [componentes[2].id]
    assert sesion.get(ComboPromocion, combo_persistido.id).dado_de_baja is True


def test_ld_21_reactivar_combo_con_nombre_en_conflicto(
    sesion, combo_persistido, componentes, crear_postre, HOY
):
    combo_persistido.dado_de_baja = True
    sesion.add(crear_postre("Combo"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_combos.actualizar_combo(
            sesion,
            combo_persistido.id,
            _datos_actualizar(HOY, dado_de_baja=False, **_ids_actuales(componentes)),
            HOY,
        )

    sesion.expire_all()
    assert sesion.get(ComboPromocion, combo_persistido.id).dado_de_baja is True


def test_cat_21_actualizar_combo_activo_con_nombre_de_otro_producto_duplicado(
    sesion, combo_persistido, componentes, HOY
):
    with pytest.raises(NombreDuplicado):
        servicios_combos.actualizar_combo(
            sesion,
            combo_persistido.id,
            _datos_actualizar(HOY, nombre="cerveza", **_ids_actuales(componentes)),
            HOY,
        )


# --- `seccion_id` en combos (secciones-backend) ---


@pytest.fixture
def seccion(sesion, crear_seccion):
    seccion = crear_seccion()
    sesion.add(seccion)
    sesion.commit()
    return seccion


def test_cat_s_04_crear_combo_con_seccion_guarda_seccion_id(sesion, componentes, seccion, HOY):
    plato, _, _ = componentes

    combo = servicios_combos.crear_combo(
        sesion, _datos(HOY, platos_ids=[plato.id], seccion_id=seccion.id), HOY
    )

    assert sesion.get(ComboPromocion, combo.id).seccion_id == seccion.id


def test_cat_s_05_crear_combo_con_seccion_inexistente_no_persiste(sesion, componentes, HOY):
    plato, _, _ = componentes

    with pytest.raises(SeccionInexistente):
        servicios_combos.crear_combo(
            sesion, _datos(HOY, platos_ids=[plato.id], seccion_id=999), HOY
        )

    assert sesion.scalars(select(ComboPromocion)).all() == []


def test_cat_s_09_28_combo_vigente_cambia_de_seccion_y_rechaza_inexistente(
    sesion, combo_persistido, seccion, HOY
):
    combo = combo_persistido
    base = {
        "platos_ids": combo.platos_ids,
        "bebidas_ids": combo.bebidas_ids,
        "postres_ids": combo.postres_ids,
    }

    servicios_combos.actualizar_combo(
        sesion, combo.id, _datos_actualizar(HOY, seccion_id=seccion.id, **base), HOY
    )
    assert combo.seccion_id == seccion.id

    with pytest.raises(SeccionInexistente):
        servicios_combos.actualizar_combo(
            sesion, combo.id, _datos_actualizar(HOY, seccion_id=999, **base), HOY
        )
    sesion.expire_all()
    assert sesion.get(ComboPromocion, combo.id).seccion_id == seccion.id


def test_cat_s_20_referencia_inexistente_tiene_prioridad_sobre_componente_inactivo(
    sesion, componentes, HOY
):
    plato, bebida, _ = componentes
    bebida.dado_de_baja = True
    sesion.commit()

    with pytest.raises(ComponenteInvalido) as error:
        servicios_combos.crear_combo(
            sesion,
            _datos(HOY, platos_ids=[plato.id, 999], bebidas_ids=[bebida.id]),
            HOY,
        )

    assert error.value.campo == "platos_ids"


def test_seccion_inexistente_tiene_prioridad_sobre_componente_inactivo_en_el_alta(
    sesion, componentes, HOY
):
    plato, bebida, _ = componentes
    bebida.dado_de_baja = True
    sesion.commit()

    with pytest.raises(SeccionInexistente):
        servicios_combos.crear_combo(
            sesion,
            _datos(HOY, platos_ids=[plato.id], bebidas_ids=[bebida.id], seccion_id=999),
            HOY,
        )


def test_seccion_inexistente_tiene_prioridad_sobre_componente_inactivo_en_el_put(
    sesion, combo_persistido, HOY
):
    combo = combo_persistido
    ids = {
        "platos_ids": combo.platos_ids,
        "bebidas_ids": combo.bebidas_ids,
        "postres_ids": combo.postres_ids,
    }
    combo.bebidas[0].dado_de_baja = True
    sesion.commit()

    with pytest.raises(SeccionInexistente):
        servicios_combos.actualizar_combo(
            sesion, combo.id, _datos_actualizar(HOY, seccion_id=999, **ids), HOY
        )
