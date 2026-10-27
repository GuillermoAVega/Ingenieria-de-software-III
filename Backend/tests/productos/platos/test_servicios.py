from decimal import Decimal

import pytest
from sqlalchemy import select

from src.productos import services
from src.productos.exceptions import BajaRestringida, NombreDuplicado, ProductoNoEncontrado
from src.productos.models import Producto
from src.productos.platos import services as servicios_platos
from src.productos.platos.models import Plato
from src.productos.platos.schemas import PlatoActualizar, PlatoCrear


def _datos_crear(**cambios):
    datos = {"nombre": "Milanesa", "precio": Decimal("1500.00"), "cant_personas": 2}
    datos.update(cambios)
    return PlatoCrear(**datos)


def _datos_actualizar(**cambios):
    datos = {"nombre": "Milanesa", "precio": Decimal("1500.00"), "cant_personas": 2}
    datos.update(cambios)
    return PlatoActualizar(**datos)


def test_cat_07_crear_plato_persiste_y_calcula_nombre_normalizado(sesion):
    plato = servicios_platos.crear_plato(
        sesion, _datos_crear(nombre="  Milanesa Napolitana ", descripcion="Con jamón")
    )

    guardado = sesion.get(Plato, plato.id)
    assert guardado.nombre == "Milanesa Napolitana"
    assert guardado.nombre_normalizado == "milanesa napolitana"
    assert guardado.precio == Decimal("1500.00")
    assert guardado.cant_personas == 2
    assert guardado.descripcion == "Con jamón"
    assert guardado.dado_de_baja is False


@pytest.mark.parametrize(
    "nombre", ["Milanesa", "MILANESA", "  Milanesa "], ids=["exacto", "mayusculas", "espacios"]
)
def test_cat_21_22_23_crear_plato_con_nombre_activo_duplicado(sesion, crear_plato, nombre):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_platos.crear_plato(sesion, _datos_crear(nombre=nombre))

    assert len(sesion.scalars(select(Producto)).all()) == 1


def test_cat_24_crear_plato_con_tilde_distinta_no_es_duplicado(sesion, crear_plato):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()

    plato = servicios_platos.crear_plato(sesion, _datos_crear(nombre="Milanésa"))

    assert plato.id is not None


def test_cat_25_crear_plato_reutiliza_el_nombre_de_uno_dado_de_baja(sesion, crear_plato):
    sesion.add(crear_plato(nombre="Milanesa", dado_de_baja=True))
    sesion.commit()

    plato = servicios_platos.crear_plato(sesion, _datos_crear())

    assert plato.id is not None


def test_cat_21_integrity_error_del_indice_parcial_se_traduce_a_nombre_duplicado(
    sesion, crear_plato, monkeypatch
):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()
    # Simula la carrera: la verificación del servicio no detecta el duplicado
    monkeypatch.setattr(services, "verificar_nombre_unico", lambda *args, **kwargs: None)

    with pytest.raises(NombreDuplicado):
        servicios_platos.crear_plato(sesion, _datos_crear())

    # La sesión quedó utilizable tras el rollback
    assert len(sesion.scalars(select(Producto)).all()) == 1


def test_cat_26_actualizar_plato_con_el_mismo_nombre(sesion, crear_plato, HOY):
    plato = crear_plato(nombre="Milanesa")
    sesion.add(plato)
    sesion.commit()

    actualizado = servicios_platos.actualizar_plato(
        sesion, plato.id, _datos_actualizar(precio=Decimal("1800.00"), cant_personas=3),
        hoy=HOY,
    )

    assert actualizado.precio == Decimal("1800.00")
    assert actualizado.cant_personas == 3
    assert actualizado.nombre_normalizado == "milanesa"


def test_cat_21_actualizar_plato_con_nombre_de_otro_producto_activo(
    sesion, crear_plato, crear_bebida, HOY
):
    plato = crear_plato(nombre="Milanesa")
    sesion.add_all([plato, crear_bebida(nombre="Cerveza")])
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_platos.actualizar_plato(
            sesion, plato.id, _datos_actualizar(nombre="cerveza"), hoy=HOY
        )

    sesion.expire_all()
    assert sesion.get(Plato, plato.id).nombre == "Milanesa"


def test_cat_21_actualizar_plato_traduce_el_integrity_error_a_nombre_duplicado(
    sesion, crear_plato, crear_bebida, monkeypatch, HOY
):
    plato = crear_plato(nombre="Milanesa")
    sesion.add_all([plato, crear_bebida(nombre="Cerveza")])
    sesion.commit()
    monkeypatch.setattr(services, "verificar_nombre_unico", lambda *args, **kwargs: None)

    with pytest.raises(NombreDuplicado):
        servicios_platos.actualizar_plato(
            sesion, plato.id, _datos_actualizar(nombre="Cerveza"), hoy=HOY
        )

    sesion.expire_all()
    assert sesion.get(Plato, plato.id).nombre == "Milanesa"


def test_cat_11_actualizar_plato_con_id_desconocido(sesion, HOY):
    with pytest.raises(ProductoNoEncontrado):
        servicios_platos.actualizar_plato(sesion, 999, _datos_actualizar(), hoy=HOY)


def test_cat_08_actualizar_plato_con_id_de_otro_subtipo(sesion, crear_bebida, HOY):
    bebida = crear_bebida()
    sesion.add(bebida)
    sesion.commit()

    with pytest.raises(ProductoNoEncontrado):
        servicios_platos.actualizar_plato(sesion, bebida.id, _datos_actualizar(), hoy=HOY)


def test_cat_13_actualizar_plato_es_reemplazo_completo(sesion, crear_plato, HOY):
    plato = crear_plato(descripcion="Con papas", imagen="milanesa.png")
    sesion.add(plato)
    sesion.commit()

    actualizado = servicios_platos.actualizar_plato(sesion, plato.id, _datos_actualizar(), hoy=HOY)

    assert actualizado.descripcion is None
    assert actualizado.imagen is None


def test_cat_12_actualizar_plato_sin_dado_de_baja_conserva_el_estado(sesion, crear_plato, HOY):
    plato = crear_plato(dado_de_baja=True)
    sesion.add(plato)
    sesion.commit()

    actualizado = servicios_platos.actualizar_plato(
        sesion, plato.id, _datos_actualizar(dado_de_baja=None, precio=Decimal("2000.00")),
        hoy=HOY,
    )

    assert actualizado.dado_de_baja is True
    assert actualizado.precio == Decimal("2000.00")


def test_actualizar_un_plato_dado_de_baja_no_compite_por_el_nombre(sesion, crear_plato, HOY):
    sesion.add_all([crear_plato(nombre="Milanesa"), crear_plato(nombre="Pizza", dado_de_baja=True)])
    sesion.commit()
    baja = sesion.scalars(select(Plato).where(Plato.nombre == "Pizza")).one()

    # Mientras siga dado de baja, el nombre no compite con los activos
    actualizado = servicios_platos.actualizar_plato(
        sesion, baja.id, _datos_actualizar(nombre="Milanesa"),
        hoy=HOY,
    )

    assert actualizado.dado_de_baja is True


def test_ld_09_actualizar_plato_con_dado_de_baja_false_lo_reactiva(sesion, crear_plato, HOY):
    plato = crear_plato(dado_de_baja=True)
    sesion.add(plato)
    sesion.commit()

    actualizado = servicios_platos.actualizar_plato(
        sesion, plato.id, _datos_actualizar(dado_de_baja=False), hoy=HOY
    )

    sesion.expire_all()
    assert actualizado.dado_de_baja is False
    assert sesion.get(Plato, plato.id).dado_de_baja is False


def test_ld_21_reactivar_plato_con_nombre_activo_duplicado_no_cambia_el_estado(
    sesion, crear_plato, crear_bebida, HOY
):
    plato = crear_plato(nombre="Milanesa", dado_de_baja=True)
    sesion.add_all([plato, crear_bebida(nombre="Milanesa")])
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_platos.actualizar_plato(
            sesion, plato.id, _datos_actualizar(dado_de_baja=False), hoy=HOY
        )

    sesion.expire_all()
    assert sesion.get(Plato, plato.id).dado_de_baja is True


def test_ld_09_reactivar_con_nuevo_nombre_compara_el_nombre_nuevo(
    sesion, crear_plato, crear_bebida, HOY
):
    plato = crear_plato(nombre="Milanesa", dado_de_baja=True)
    sesion.add_all([plato, crear_bebida(nombre="Milanesa")])
    sesion.commit()

    actualizado = servicios_platos.actualizar_plato(
        sesion, plato.id, _datos_actualizar(nombre="Pizza", dado_de_baja=False), hoy=HOY
    )

    assert actualizado.dado_de_baja is False
    assert actualizado.nombre == "Pizza"


def test_ld_05_actualizar_plato_activo_con_dado_de_baja_false_es_edicion_normal(
    sesion, crear_plato, HOY
):
    plato = crear_plato(descripcion="Vieja")
    sesion.add(plato)
    sesion.commit()

    actualizado = servicios_platos.actualizar_plato(
        sesion, plato.id, _datos_actualizar(dado_de_baja=False, descripcion="Nueva"), hoy=HOY
    )

    assert actualizado.dado_de_baja is False
    assert actualizado.descripcion == "Nueva"


def test_ld_07_actualizar_plato_dado_de_baja_sin_dado_de_baja_conserva_el_estado(
    sesion, crear_plato, HOY
):
    plato = crear_plato(dado_de_baja=True)
    sesion.add(plato)
    sesion.commit()

    actualizado = servicios_platos.actualizar_plato(
        sesion, plato.id, _datos_actualizar(descripcion="Editado"), hoy=HOY
    )

    sesion.expire_all()
    assert actualizado.descripcion == "Editado"
    assert sesion.get(Plato, plato.id).dado_de_baja is True


def test_ld_10_actualizar_plato_con_dado_de_baja_true_bloqueado_no_cambia_nada(
    sesion, crear_plato, crear_postre, crear_menu, HOY
):
    plato, postre = crear_plato(descripcion="Vieja"), crear_postre()
    menu = crear_menu(plato, postre)
    sesion.add_all([plato, postre, menu])
    sesion.commit()

    with pytest.raises(BajaRestringida) as error:
        servicios_platos.actualizar_plato(
            sesion,
            plato.id,
            _datos_actualizar(dado_de_baja=True, descripcion="Nueva"),
            hoy=HOY,
        )

    assert error.value.bloqueantes == [menu.id]
    sesion.expire_all()
    guardado = sesion.get(Plato, plato.id)
    assert guardado.dado_de_baja is False
    assert guardado.descripcion == "Vieja"


def test_ld_03_actualizar_plato_ya_dado_de_baja_con_dado_de_baja_true_no_cambia_el_estado(
    sesion, crear_plato, HOY
):
    plato = crear_plato(dado_de_baja=True)
    sesion.add(plato)
    sesion.commit()

    actualizado = servicios_platos.actualizar_plato(
        sesion, plato.id, _datos_actualizar(dado_de_baja=True), hoy=HOY
    )

    assert actualizado.dado_de_baja is True
